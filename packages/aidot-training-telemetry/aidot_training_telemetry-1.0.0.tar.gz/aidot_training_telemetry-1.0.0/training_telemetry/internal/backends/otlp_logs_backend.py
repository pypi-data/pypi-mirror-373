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
import logging

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, LogExporter
from opentelemetry.sdk.resources import Resource

from training_telemetry.config import ApplicationConfig, BackendType
from training_telemetry.internal.backends.logger_backend import PythonLoggerBackend
from training_telemetry.verbosity import Verbosity


class OTLPLogsBackend(PythonLoggerBackend):
    """Backend implementation that sends OpenTelemetry logs over OTLP."""

    def __init__(
        self,
        name: str,
        level: int,
        exporter: LogExporter,
        verbosity: Verbosity,
        application: ApplicationConfig,
        version: str,
    ) -> None:
        resource: Resource = Resource.create(
            {
                "job_name": application.job_name,
                "job_id": application.job_id,
                "rank": application.rank,
                "world_size": application.world_size,
                "training_telemetry_version": version,
            }
        )
        self._provider = LoggerProvider(resource=resource)
        self._processor = BatchLogRecordProcessor(exporter)
        self._provider.add_log_record_processor(self._processor)

        # Create a Python logger that will send logs through OpenTelemetry
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Create a LoggingHandler that will send logs to OpenTelemetry
        handler = LoggingHandler(level=level, logger_provider=self._provider)
        logger.addHandler(handler)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

        super().__init__(logger, verbosity)

    def type(self) -> BackendType:
        return BackendType.OTLP_LOGS

    def close(self) -> None:
        super().close()
        self._provider.shutdown()
