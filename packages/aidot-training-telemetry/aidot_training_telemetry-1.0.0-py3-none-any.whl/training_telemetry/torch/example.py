#
#  Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an
# express license agreement from NVIDIA CORPORATION is strictly
# prohibited.
#
import os
import tempfile
from typing import Any

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from tzlocal import get_localzone

from training_telemetry.config import ApplicationConfig, LoggerBackendConfig, OTLPLogsBackendConfig, TelemetryConfig
from training_telemetry.context import checkpoint_save, get_recorder, running, timed_span, training
from training_telemetry.events import Event, EventName
from training_telemetry.metrics import ApplicationMetrics, CheckpointMetrics, CheckPointType, IterationMetrics
from training_telemetry.provider import Provider
from training_telemetry.spans import SpanColor, SpanName
from training_telemetry.torch.utils import get_rank, get_world_size
from training_telemetry.verbosity import Verbosity

# Generate some random data for this example
torch.manual_seed(42)
# Generate random input features and binary labels
X = torch.randn(1000, 10, dtype=torch.float32)
y = (X.sum(dim=1) > 0).float()
dataset = TensorDataset(X, y)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
num_epochs = 100

# Initialize the telemetry provider with a default configuration
Provider.set_provider(
    TelemetryConfig(
        application=ApplicationConfig(
            job_name="torch_example", job_id="1234567890", rank=get_rank(), world_size=get_world_size()
        ),
        backends=[
            OTLPLogsBackendConfig(exporter="grpc", endpoint="http://localhost:4317"),
            LoggerBackendConfig(),
        ],
    )
)


# Define a simple model
class SimpleModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(10, 64), nn.ReLU(), nn.Linear(64, 1), nn.Sigmoid())

    def forward(self, x: torch.Tensor) -> Any:
        return self.layers(x)


def get_application_metrics() -> ApplicationMetrics:
    return ApplicationMetrics.create(
        rank=get_rank(),
        world_size=get_world_size(),
        node_name="localhost",
        timezone=str(get_localzone()),
        total_iterations=num_epochs * len(dataloader),
        checkpoint_enabled=True,
        checkpoint_strategy="sync",
    )


@running(metrics=get_application_metrics())
def main() -> None:
    # Initialize model, loss function and optimizer
    model = SimpleModel()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters())

    with training() as training_span:
        current_iteration = 0
        accuracy = torch.tensor(float("nan"))
        loss = torch.tensor(float("nan"))

        for epoch in range(num_epochs):
            for batch_idx, (inputs, targets) in enumerate(dataloader):
                with timed_span(SpanName.ITERATION, color=SpanColor.RED, verbosity=Verbosity.PROFILING):
                    # Forward pass
                    with timed_span(SpanName.MODEL_FORWARD, color=SpanColor.RED, verbosity=Verbosity.PROFILING):
                        outputs = model(inputs)
                        loss = criterion(outputs.squeeze(), targets)

                    # Backward pass and optimize
                    with timed_span(SpanName.ZERO_GRAD, color=SpanColor.GREEN, verbosity=Verbosity.PROFILING):
                        optimizer.zero_grad()
                    with timed_span(SpanName.MODEL_BACKWARD, color=SpanColor.BLUE, verbosity=Verbosity.PROFILING):
                        loss.backward()
                    with timed_span(SpanName.OPTIMIZER_UPDATE, color=SpanColor.YELLOW, verbosity=Verbosity.PROFILING):
                        optimizer.step()

                    # Calculate accuracy
                    predictions = (outputs.squeeze() > 0.5).float()
                    accuracy = (predictions == targets).float().mean()

                    current_iteration += 1

            # Log iteration metrics every 2 epochs
            if epoch % 2 == 0:
                metrics = IterationMetrics.create(
                    current_iteration=current_iteration,
                    num_iterations=len(dataloader),
                    interval=len(dataloader),
                    loss=loss.item(),
                    tflops=100,
                )
                get_recorder().event(Event.create(EventName.TRAINING_ITERATIONS, metrics=metrics), training_span)

            # Save checkpoint every 5 epochs
            if epoch % 5 == 0:
                print(
                    f"Epoch [{epoch+1}/{num_epochs}], "
                    f"Batch [{batch_idx+1}/{len(dataloader)}], "
                    f"Loss: {loss.item():.4f}, "
                    f"Accuracy: {accuracy.item():.4f}"
                )
                checkpoint = {
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "epoch": epoch,
                    "iteration": current_iteration,
                    "loss": loss.item(),
                    "accuracy": accuracy.item(),
                }
                with checkpoint_save() as checkpoint_save_span:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        checkpoint_file_name = os.path.join(temp_dir, f"checkpoint_iter_{current_iteration}.pt")
                        torch.save(checkpoint, checkpoint_file_name)
                        checkpoint_save_span.add_metrics(
                            CheckpointMetrics.create(
                                checkpoint_type=CheckPointType.LOCAL,
                                current_iteration=current_iteration,
                                num_iterations=len(dataloader),
                                checkpoint_directory=temp_dir,
                            )
                        )


if __name__ == "__main__":
    main()
