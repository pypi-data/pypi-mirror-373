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
import os
from datetime import datetime
from threading import Lock
from typing import Optional

from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter as OTLPLogExporterGrpc
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPSpanExporterGrpc
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter as OTLPLogExporterHttp
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPSpanExporterHttp
from opentelemetry.sdk._logs.export import ConsoleLogExporter, LogExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

from training_telemetry.config import (
    ApplicationConfig,
    BackendType,
    FileBackendConfig,
    LoggerBackendConfig,
    NVTXBackendConfig,
    OTLPLogsBackendConfig,
    OTLPTracesBackendConfig,
    TelemetryConfig,
)
from training_telemetry.internal.backend import Backend
from training_telemetry.internal.backends.file_backend import FileBackend
from training_telemetry.internal.backends.logger_backend import PythonLoggerBackend
from training_telemetry.internal.backends.nvtx_backend import NVTXBackend
from training_telemetry.internal.backends.otlp_logs_backend import OTLPLogsBackend
from training_telemetry.internal.backends.otlp_traces_backend import OTLPTracesBackend
from training_telemetry.internal.standard_recorder import StandardRecorder
from training_telemetry.recorder import Recorder
from training_telemetry.torch.utils import get_rank
from training_telemetry.utils import get_logger
from training_telemetry.verbosity import Verbosity
from training_telemetry.version import __version__

_logger = get_logger(__name__, level=logging.INFO)


class Provider:
    """A provider class for creating telemetry loggers."""

    _instance: Optional["Provider"] = None
    _config: Optional[TelemetryConfig] = None
    _lock: Lock = Lock()

    @classmethod
    def set_provider(cls, config: TelemetryConfig, logger: Optional[logging.Logger] = None) -> "Provider":
        _logger.debug(f"Setting provider with CONFIG: {config}, VERSION: {__version__}")
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = Provider(config, logger)
                    _logger.debug(f"Provider created with CONFIG: {config}, VERSION: {__version__}")
        if config != cls.instance()._config:
            raise ValueError(
                f"Provider already initialized with a different config: {cls.instance()._config} != {config}"
            )
        return cls._instance

    def __init__(self, config: TelemetryConfig, logger: Optional[logging.Logger] = None):
        """Initialize the Provider with optional configuration.

        Args:
            config (TelemetryConfig): Configuration for the provider.
            logger (logging.Logger): Optional logger to use for the provider.
            If this is provided, it will be used for the logger backend overriding the logger config.
        """
        self._config = config
        backends: list[Backend] = []
        for backend_config in config.backends:
            _logger.debug(f"Examining backend config: {backend_config}")
            match backend_config.backend_type:
                case BackendType.LOGGER:
                    assert isinstance(backend_config, LoggerBackendConfig)
                    logger_backend = self._get_logger_backend(backend_config, logger)
                    if logger_backend is not None:
                        backends.append(logger_backend)
                case BackendType.FILE:
                    assert isinstance(backend_config, FileBackendConfig)
                    backends.append(self._get_file_backend(backend_config))
                case BackendType.OTLP_TRACES:
                    assert isinstance(backend_config, OTLPTracesBackendConfig)
                    backends.append(self._get_otlp_traces_backend(backend_config))
                case BackendType.OTLP_LOGS:
                    assert isinstance(backend_config, OTLPLogsBackendConfig)
                    backends.append(self._get_otlp_logs_backend(backend_config, config.application))
                case BackendType.NVTX:
                    assert isinstance(backend_config, NVTXBackendConfig)
                    backends.append(self._get_nvtx_backend(backend_config))
                case _:
                    raise ValueError(f"Unsupported backend type: {backend_config.backend_type}")
        _logger.info(f"Initializing recorder with {len(backends)} backends, training-telemetry-version={__version__}")
        self._recorder = StandardRecorder(backends=backends)

    def _get_logger_backend(
        self, config: LoggerBackendConfig, telemetry_logger: Optional[logging.Logger] = None
    ) -> PythonLoggerBackend:

        if telemetry_logger is None:
            logger_name = config.name
            if config.rank_aware:
                logger_name += f"_rank{get_rank()}"
            _logger.info(
                f"Initializing logger backend, rank_aware={config.rank_aware}, logger_name={logger_name}, errors_only={config.errors_only}"
            )
            telemetry_logger = get_logger(
                name=logger_name,
                level=config.log_level,
                propagate=config.propagate_log_context,
                format=config.log_format,
            )
        else:
            _logger.info(f"Using existing logger for logger backend, errors_only={config.errors_only}")
        verbosity = Verbosity.ERROR if config.errors_only else Verbosity.INFO
        return PythonLoggerBackend(logger=telemetry_logger, verbosity=verbosity)

    def _get_file_backend(self, config: FileBackendConfig) -> FileBackend:
        output_file_path = config.output_file_path
        if config.rank_aware:
            output_file_path += f"_rank{get_rank()}"
        if config.date_aware:
            output_file_path += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_file_path += ".json"
        _logger.info(
            f"Initializing file backend, rank={get_rank()}, rank_aware={config.rank_aware}, output_file_path={output_file_path}"
        )
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        return FileBackend(filepath=output_file_path)

    def _get_otlp_traces_backend(self, config: OTLPTracesBackendConfig) -> OTLPTracesBackend:
        _logger.info(f"Initializing OTLP traces backend, exporter={config.exporter}, endpoint={config.endpoint}")
        if config.exporter == "console":
            return OTLPTracesBackend(ConsoleSpanExporter())
        elif config.exporter == "grpc":
            return OTLPTracesBackend(OTLPSpanExporterGrpc(endpoint=config.endpoint))
        elif config.exporter == "http":
            return OTLPTracesBackend(OTLPSpanExporterHttp(endpoint=config.endpoint))
        else:
            raise ValueError(f"Unsupported OTEL exporter: {config.exporter}")

    def _get_otlp_logs_backend(self, config: OTLPLogsBackendConfig, application: ApplicationConfig) -> OTLPLogsBackend:
        exporter: LogExporter | None = None
        if config.exporter == "console":
            exporter = ConsoleLogExporter()
        elif config.exporter == "grpc":
            exporter = OTLPLogExporterGrpc(endpoint=config.endpoint)
        elif config.exporter == "http":
            exporter = OTLPLogExporterHttp(endpoint=config.endpoint)
        else:
            raise ValueError(f"Unsupported OTEL exporter: {config.exporter}")

        name = config.name
        if config.rank_aware:
            name += f"_rank{get_rank()}"
        _logger.info(
            f"Initializing OTLP logs backend, exporter={config.exporter}, endpoint={config.endpoint}, rank_aware={config.rank_aware}, logger_name={name}, log_level={config.log_level}"
        )
        return OTLPLogsBackend(
            name=name,
            level=config.log_level,
            exporter=exporter,
            verbosity=Verbosity.INFO,
            application=application,
            version=__version__,
        )

    def _get_nvtx_backend(self, config: NVTXBackendConfig) -> NVTXBackend:
        _logger.info(f"Initializing NVTX backend")
        del config
        return NVTXBackend()

    @property
    def config(self) -> TelemetryConfig:
        assert self._config is not None
        return self._config

    @classmethod
    def instance(cls) -> "Provider":
        assert cls._instance is not None
        return cls._instance

    @property
    def recorder(self) -> Recorder:
        assert self._recorder is not None
        return self._recorder
