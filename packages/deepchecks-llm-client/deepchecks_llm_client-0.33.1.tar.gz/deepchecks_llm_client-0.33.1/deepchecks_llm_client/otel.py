import logging
import typing as t

from deepchecks_llm_client.client import DeepchecksLLMClient
from deepchecks_llm_client.data_types import EnvType
from wrapt import ObjectProxy

logging.basicConfig()
logger = logging.getLogger(__name__)

try:
    from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor, SpanExporter, SpanExportResult
except ImportError:
    logger.error("OpenTelemetry SDK is not installed. Please install opentelemetry-api and opentelemetry-sdk to use the DCSpanExporter.")
    raise


class DCSpanExporter(SpanExporter):
    def __init__(
            self,
            dc_client: DeepchecksLLMClient,
            app_name: str,
            version_name: str,
            env_type: t.Union[EnvType, str],
    ):
        """
        Initializes the DCSpanExporter with the given host and API key.

        Args:
            dc_client: An instance of DeepchecksLLMClient.
            app_name: The name of the application.
            version_name: The name of the application version.
            env_type: The environment type (e.g., PROD, EVAL).
             If not provided, a new instance will be created.
        """
        self._dc_client = DCClientOtel(dc_client)
        self._app_name = app_name
        self._version_name = version_name
        self._env_type = env_type

    def export(
        self, spans: t.Sequence[ReadableSpan]
    ) -> "SpanExportResult":
        """Exports a batch of telemetry data.

        Args:
            spans: The list of ReadableSpan objects to be exported

        Returns:
            The result of the export
        """
        try:
            self._dc_client.send_spans(
                app_name=self._app_name,
                version_name=self._version_name,
                env_type=self._env_type,
                spans=spans,
            )
            return SpanExportResult.SUCCESS
        except Exception as e: # pylint: disable=broad-except
            # Handle export failure
            logger.error(f"Export failed: {e}")
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool: # pylint: disable=unused-argument
        """Nothing is buffered in this exporter, so this method does nothing."""
        return True


class DCClientOtel(ObjectProxy):
    """
    DCClientOtel is a proxy class for the DeepchecksLLMClient that provides
    a method to send spans to the Deepchecks LLM backend.
    It is initialized with a DeepchecksLLMClient instance.
    """
    def send_spans(
            self,
            app_name: str,
            version_name: str,
            env_type: t.Union[EnvType, str],
            spans: t.Sequence[ReadableSpan]):
        """Send spans to the Deepchecks LLM backend.

        Parameters
        ----------
        app_name : str
            Application name
        version_name : str
            Name of application version
        env_type : EnvType | str
            Environment type (PROD/EVAL)
        spans : List[ReadableSpan]
            List of spans to send
        """
        self.api.send_spans(
            app_name=app_name,
            version_name=version_name,
            env_type=env_type,
            spans=spans,
        )


def register_dc_exporter(
        host: str,
        api_key: str,
        app_name: str,
        version_name: str,
        env_type: t.Union[EnvType, str],
        tracer_provider: t.Optional[TracerProvider] = None,
        dc_client: t.Optional[DeepchecksLLMClient] = None,
        log_to_console: bool = False,
) -> TracerProvider:
    """
    Registers the OpenTelemetry tracer with the provided host and API key.
    This function sets up the tracer provider with a console exporter for debugging
    and a DCSpanExporter for sending spans to Deepchecks LLM.
    Parameters
    ----------
    host : str
        The host URL for the Deepchecks LLM API.
    api_key : str
        The API key for authenticating with the Deepchecks LLM API.
    app_name : str
        The name of the application for which spans are being sent.
    version_name : str
        The name of the application version for which spans are being sent.
    env_type : EnvType | str
        The environment type (e.g., PROD, EVAL) for which spans are being sent.
    tracer_provider : TracerProvider, optional
        The OpenTelemetry TracerProvider to which the span processors will be added too.
    dc_client : DeepchecksLLMClient, optional
        An instance of DeepchecksLLMClient to use for sending spans.
        If not provided, a new instance will be created using the host and api_key.
    log_to_console : bool, optional
        If True, a console exporter will be added for debugging purposes.
        Defaults to False.
    """
    tracer_provider = tracer_provider or TracerProvider()
    # create a DeepchecksLLMClient instance if not provided:
    dc_client = dc_client or DeepchecksLLMClient(
        host=host,
        api_token=api_key,
    )
    # console exporter for debugging if needed:
    if log_to_console:
        logger.info("Adding console exporter for debugging")
        # Add a console exporter to the tracer provider for debugging
        console_exporter = ConsoleSpanExporter()
        console_span_processor = SimpleSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(console_span_processor)
    # DCSpanExporter for sending spans to Deepchecks LLM:
    dc_span_exporter = DCSpanExporter(dc_client=dc_client, app_name=app_name,
                                       version_name=version_name, env_type=env_type)
    dc_span_processor = BatchSpanProcessor(dc_span_exporter)
    tracer_provider.add_span_processor(dc_span_processor)
    # Return the tracer provider for further use
    return tracer_provider
