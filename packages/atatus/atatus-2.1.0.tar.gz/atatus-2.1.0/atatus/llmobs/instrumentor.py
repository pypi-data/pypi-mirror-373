from importlib.metadata import Distribution, distributions
from enum import Enum
from typing import Optional, Set
# from atatus.base import get_client
from atatus.utils.logging import get_logger
from opentelemetry.semconv_ai import SpanAttributes
from opentelemetry.context import get_value, attach, set_value
from opentelemetry import trace

logging = get_logger("atatus")
def _get_package_name(dist: Distribution) -> str | None:
    try:
        return dist.name.lower()
    except (KeyError, AttributeError):
        return None

installed_packages = {name for dist in distributions() if (name := _get_package_name(dist)) is not None}


def is_package_installed(package_name: str) -> bool:
    return package_name.lower() in installed_packages


def set_association_properties(properties: dict) -> None:
    attach(set_value("association_properties", properties))

    # Attach association properties to the current span, if it's a workflow or a task
    span = trace.get_current_span()
    if get_value("workflow_name") is not None or get_value("entity_name") is not None:
        _set_association_properties_attributes(span, properties)


def _set_association_properties_attributes(span, properties: dict) -> None:
    for key, value in properties.items():
        span.set_attribute(
            f"{SpanAttributes.TRACELOOP_ASSOCIATION_PROPERTIES}.{key}", value
        )


def set_workflow_name(workflow_name: str) -> None:
    attach(set_value("workflow_name", workflow_name))


def set_entity_path(entity_path: str) -> None:
    attach(set_value("entity_path", entity_path))

def get_chained_entity_path(entity_name: str) -> str:
    parent = get_value("entity_path")
    if parent is None:
        return entity_name
    else:
        return f"{parent}.{entity_name}"


class Instruments(Enum):
    ALEPHALPHA = "alephalpha"
    ANTHROPIC = "anthropic"
    BEDROCK = "bedrock"
    CHROMA = "chroma"
    COHERE = "cohere"
    CREW = "crew"
    GOOGLE_GENERATIVEAI = "google_generativeai"
    GROQ = "groq"
    HAYSTACK = "haystack"
    LANCEDB = "lancedb"
    LANGCHAIN = "langchain"
    LLAMA_INDEX = "llama_index"
    MARQO = "marqo"
    MCP = "mcp"
    MILVUS = "milvus"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    OPENAI = "openai"
    PINECONE = "pinecone"
    # PYMYSQL = "pymysql"
    QDRANT = "qdrant"
    # REDIS = "redis"
    REPLICATE = "replicate"
    # REQUESTS = "requests"
    SAGEMAKER = "sagemaker"
    TOGETHER = "together"
    TRANSFORMERS = "transformers"
    # URLLIB3 = "urllib3"
    VERTEXAI = "vertexai"
    WATSONX = "watsonx"
    WEAVIATE = "weaviate"

def init_instrumentations(
    should_enrich_metrics: bool,
    instruments: Optional[Set[Instruments]] = None,
    block_instruments: Optional[Set[Instruments]] = None,
):
    block_instruments = block_instruments or set()
    instruments = instruments or set(
        Instruments
    )  # Use all instruments if none specified

    # Remove any instruments that were explicitly blocked
    instruments = instruments - block_instruments

    instrument_set = False
    for instrument in instruments:
        if instrument == Instruments.ALEPHALPHA:
            if init_alephalpha_instrumentor():
                instrument_set = True
        elif instrument == Instruments.ANTHROPIC:
            if init_anthropic_instrumentor(should_enrich_metrics):
                instrument_set = True
        elif instrument == Instruments.BEDROCK:
            if init_bedrock_instrumentor(should_enrich_metrics):
                instrument_set = True
        elif instrument == Instruments.CHROMA:
            if init_chroma_instrumentor():
                instrument_set = True
        elif instrument == Instruments.COHERE:
            if init_cohere_instrumentor():
                instrument_set = True
        elif instrument == Instruments.CREW:
            if init_crewai_instrumentor():
                instrument_set = True
        elif instrument == Instruments.GOOGLE_GENERATIVEAI:
            if init_google_generativeai_instrumentor():
                instrument_set = True
        elif instrument == Instruments.GROQ:
            if init_groq_instrumentor():
                instrument_set = True
        elif instrument == Instruments.HAYSTACK:
            if init_haystack_instrumentor():
                instrument_set = True
        elif instrument == Instruments.LANCEDB:
            if init_lancedb_instrumentor():
                instrument_set = True
        elif instrument == Instruments.LANGCHAIN:
            if init_langchain_instrumentor():
                instrument_set = True
        elif instrument == Instruments.LLAMA_INDEX:
            if init_llama_index_instrumentor():
                instrument_set = True
        elif instrument == Instruments.MARQO:
            if init_marqo_instrumentor():
                instrument_set = True
        elif instrument == Instruments.MCP:
            if init_mcp_instrumentor():
                instrument_set = True
        elif instrument == Instruments.MILVUS:
            if init_milvus_instrumentor():
                instrument_set = True
        elif instrument == Instruments.MISTRAL:
            if init_mistralai_instrumentor():
                instrument_set = True
        elif instrument == Instruments.OLLAMA:
            if init_ollama_instrumentor():
                instrument_set = True
        elif instrument == Instruments.OPENAI:
            if init_openai_instrumentor(should_enrich_metrics):
                instrument_set = True
        elif instrument == Instruments.PINECONE:
            if init_pinecone_instrumentor():
                instrument_set = True
        # elif instrument == Instruments.PYMYSQL:
        #     if init_pymysql_instrumentor():
        #         instrument_set = True
        elif instrument == Instruments.QDRANT:
            if init_qdrant_instrumentor():
                instrument_set = True
        # elif instrument == Instruments.REDIS:
        #     if init_redis_instrumentor():
        #         instrument_set = True
        elif instrument == Instruments.REPLICATE:
            if init_replicate_instrumentor():
                instrument_set = True
        # elif instrument == Instruments.REQUESTS:
        #     if init_requests_instrumentor():
        #         instrument_set = True
        elif instrument == Instruments.SAGEMAKER:
            if init_sagemaker_instrumentor(should_enrich_metrics):
                instrument_set = True
        elif instrument == Instruments.TOGETHER:
            if init_together_instrumentor():
                instrument_set = True
        elif instrument == Instruments.TRANSFORMERS:
            if init_transformers_instrumentor():
                instrument_set = True
        # elif instrument == Instruments.URLLIB3:
        #     if init_urllib3_instrumentor():
        #         instrument_set = True
        elif instrument == Instruments.VERTEXAI:
            if init_vertexai_instrumentor():
                instrument_set = True
        elif instrument == Instruments.WATSONX:
            if init_watsonx_instrumentor():
                instrument_set = True
        elif instrument == Instruments.WEAVIATE:
            if init_weaviate_instrumentor():
                instrument_set = True
        else:
            logging.warning(f"Warning: {instrument} instrumentation does not exist.")
            logging.warning(
                "Usage:\n"
                "from atatus.llmobs import Instruments\n"
                "Traceloop.init(app_name='...', instruments=set([Instruments.OPENAI]))"
            )
            # print(Fore.RESET)

    if not instrument_set:
        logging.warning(
            "Warning: No valid instruments set. ",
            "Specify instruments or remove 'instruments' argument to use all instruments."
        )
        # print(Fore.RESET)

    return instrument_set


def init_openai_instrumentor(should_enrich_metrics: bool):
    try:
        if is_package_installed("openai"):
            from opentelemetry.instrumentation.openai import OpenAIInstrumentor

            instrumentor = OpenAIInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
                enrich_assistant=should_enrich_metrics,
                get_common_metrics_attributes=metrics_common_attributes,
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True

    except Exception as e:
        logging.error(f"Error initializing OpenAI instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_anthropic_instrumentor(
    should_enrich_metrics: bool
):
    try:
        if is_package_installed("anthropic"):
            from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

            instrumentor = AnthropicInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
                get_common_metrics_attributes=metrics_common_attributes,
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Anthropic instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_cohere_instrumentor():
    try:
        if is_package_installed("cohere"):
            from opentelemetry.instrumentation.cohere import CohereInstrumentor

            instrumentor = CohereInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Cohere instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_pinecone_instrumentor():
    try:
        if is_package_installed("pinecone"):
            from opentelemetry.instrumentation.pinecone import PineconeInstrumentor

            instrumentor = PineconeInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Pinecone instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_qdrant_instrumentor():
    try:
        if is_package_installed("qdrant_client"):
            from opentelemetry.instrumentation.qdrant import QdrantInstrumentor

            instrumentor = QdrantInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
    except Exception as e:
        logging.error(f"Error initializing Qdrant instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_chroma_instrumentor():
    try:
        if is_package_installed("chromadb"):
            from opentelemetry.instrumentation.chromadb import ChromaInstrumentor

            instrumentor = ChromaInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Chroma instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_google_generativeai_instrumentor():
    try:
        if is_package_installed("google-generativeai"):
            from opentelemetry.instrumentation.google_generativeai import (
                GoogleGenerativeAiInstrumentor,
            )

            instrumentor = GoogleGenerativeAiInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Gemini instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_haystack_instrumentor():
    try:
        if is_package_installed("haystack"):
            from opentelemetry.instrumentation.haystack import HaystackInstrumentor

            instrumentor = HaystackInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Haystack instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_langchain_instrumentor():
    try:
        if is_package_installed("langchain") or is_package_installed("langgraph"):
            from opentelemetry.instrumentation.langchain import LangchainInstrumentor

            instrumentor = LangchainInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing LangChain instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_mistralai_instrumentor():
    try:
        if is_package_installed("mistralai"):
            from opentelemetry.instrumentation.mistralai import MistralAiInstrumentor

            instrumentor = MistralAiInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing MistralAI instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_ollama_instrumentor():
    try:
        if is_package_installed("ollama"):
            from opentelemetry.instrumentation.ollama import OllamaInstrumentor

            instrumentor = OllamaInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Ollama instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_transformers_instrumentor():
    try:
        if is_package_installed("transformers"):
            from opentelemetry.instrumentation.transformers import (
                TransformersInstrumentor,
            )

            instrumentor = TransformersInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Transformers instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_together_instrumentor():
    try:
        if is_package_installed("together"):
            from opentelemetry.instrumentation.together import TogetherAiInstrumentor

            instrumentor = TogetherAiInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing TogetherAI instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_llama_index_instrumentor():
    try:
        if is_package_installed("llama-index") or is_package_installed("llama_index"):
            from opentelemetry.instrumentation.llamaindex import LlamaIndexInstrumentor

            instrumentor = LlamaIndexInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing LlamaIndex instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_milvus_instrumentor():
    try:
        if is_package_installed("pymilvus"):
            from opentelemetry.instrumentation.milvus import MilvusInstrumentor

            instrumentor = MilvusInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Milvus instrumentor: {e}")
        # get_client().capture_exception()
        return False


# def init_requests_instrumentor():
#     try:
#         if is_package_installed("requests"):
#             from opentelemetry.instrumentation.requests import RequestsInstrumentor
#
#             instrumentor = RequestsInstrumentor()
#             if not instrumentor.is_instrumented_by_opentelemetry:
#                 instrumentor.instrument(excluded_urls=EXCLUDED_URLS)
#         return True
#     except Exception as e:
#         logging.error(f"Error initializing Requests instrumentor: {e}")
#         # get_client().capture_exception()
#         return False


# def init_urllib3_instrumentor():
#     try:
#         if is_package_installed("urllib3"):
#             from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
#
#             instrumentor = URLLib3Instrumentor()
#             if not instrumentor.is_instrumented_by_opentelemetry:
#                 instrumentor.instrument(excluded_urls=EXCLUDED_URLS)
#         return True
#     except Exception as e:
#         logging.error(f"Error initializing urllib3 instrumentor: {e}")
#         # get_client().capture_exception()
#         return False
#

def init_pymysql_instrumentor():
    try:
        if is_package_installed("sqlalchemy"):
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

            instrumentor = SQLAlchemyInstrumentor()
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing SQLAlchemy instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_bedrock_instrumentor(should_enrich_metrics: bool):
    try:
        if is_package_installed("boto3"):
            from opentelemetry.instrumentation.bedrock import BedrockInstrumentor

            instrumentor = BedrockInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Bedrock instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_sagemaker_instrumentor(should_enrich_metrics: bool):
    try:
        if is_package_installed("boto3"):
            from opentelemetry.instrumentation.sagemaker import SageMakerInstrumentor

            instrumentor = SageMakerInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing SageMaker instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_replicate_instrumentor():
    try:
        if is_package_installed("replicate"):
            from opentelemetry.instrumentation.replicate import ReplicateInstrumentor

            instrumentor = ReplicateInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Replicate instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_vertexai_instrumentor():
    try:
        if is_package_installed("google-cloud-aiplatform"):
            from opentelemetry.instrumentation.vertexai import VertexAIInstrumentor

            instrumentor = VertexAIInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.warning(f"Error initializing Vertex AI instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_watsonx_instrumentor():
    try:
        if is_package_installed("ibm-watsonx-ai") or is_package_installed(
            "ibm_watson_machine_learning"
        ):
            from opentelemetry.instrumentation.watsonx import WatsonxInstrumentor

            instrumentor = WatsonxInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.warning(f"Error initializing Watsonx instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_weaviate_instrumentor():
    try:
        if is_package_installed("weaviate"):
            from opentelemetry.instrumentation.weaviate import WeaviateInstrumentor

            instrumentor = WeaviateInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.warning(f"Error initializing Weaviate instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_alephalpha_instrumentor():
    try:
        if is_package_installed("aleph_alpha_client"):
            from opentelemetry.instrumentation.alephalpha import AlephAlphaInstrumentor

            instrumentor = AlephAlphaInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Aleph Alpha instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_marqo_instrumentor():
    try:
        if is_package_installed("marqo"):
            from opentelemetry.instrumentation.marqo import MarqoInstrumentor

            instrumentor = MarqoInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing marqo instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_lancedb_instrumentor():
    try:
        if is_package_installed("lancedb"):
            from opentelemetry.instrumentation.lancedb import LanceInstrumentor

            instrumentor = LanceInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing LanceDB instrumentor: {e}")


# def init_redis_instrumentor():
#     try:
#         if is_package_installed("redis"):
#             from opentelemetry.instrumentation.redis import RedisInstrumentor
#
#             instrumentor = RedisInstrumentor()
#             if not instrumentor.is_instrumented_by_opentelemetry:
#                 instrumentor.instrument(excluded_urls=EXCLUDED_URLS)
#         return True
#     except Exception as e:
#         logging.error(f"Error initializing redis instrumentor: {e}")
#         # get_client().capture_exception()
#         return False


def init_groq_instrumentor():
    try:
        if is_package_installed("groq"):
            from opentelemetry.instrumentation.groq import GroqInstrumentor

            instrumentor = GroqInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing Groq instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_crewai_instrumentor():
    try:
        if is_package_installed("crewai"):
            from opentelemetry.instrumentation.crewai import CrewAIInstrumentor

            instrumentor = CrewAIInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing CrewAI instrumentor: {e}")
        # get_client().capture_exception()
        return False


def init_mcp_instrumentor():
    try:
        if is_package_installed("mcp"):
            from opentelemetry.instrumentation.mcp import McpInstrumentor

            instrumentor = McpInstrumentor(
               # exception_logger=lambda e: # get_client().capture_exception(),
            )
            if not instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.instrument()
        return True
    except Exception as e:
        logging.error(f"Error initializing MCP instrumentor: {e}")
        # get_client().capture_exception()
        return False


def metrics_common_attributes():
    common_attributes = {}
    workflow_name = get_value("workflow_name")
    if workflow_name is not None:
        common_attributes[SpanAttributes.TRACELOOP_WORKFLOW_NAME] = workflow_name

    entity_name = get_value("entity_name")
    if entity_name is not None:
        common_attributes[SpanAttributes.TRACELOOP_ENTITY_NAME] = entity_name

    association_properties = get_value("association_properties")
    if association_properties is not None:
        for key, value in association_properties.items():
            common_attributes[
                f"{SpanAttributes.TRACELOOP_ASSOCIATION_PROPERTIES}.{key}"
            ] = value

    return common_attributes
