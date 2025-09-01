from _typeshed import Incomplete
from gllm_inference.em_invoker import AzureOpenAIEMInvoker as AzureOpenAIEMInvoker, GoogleEMInvoker as GoogleEMInvoker, LangChainEMInvoker as LangChainEMInvoker, OpenAICompatibleEMInvoker as OpenAICompatibleEMInvoker, OpenAIEMInvoker as OpenAIEMInvoker, TwelveLabsEMInvoker as TwelveLabsEMInvoker, VoyageEMInvoker as VoyageEMInvoker
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker as BaseEMInvoker
from gllm_inference.schema.model_id import ModelId as ModelId, ModelProvider as ModelProvider
from typing import Any

PROVIDER_TO_EM_INVOKER_MAP: dict[str, type[BaseEMInvoker]]
logger: Incomplete

class Key:
    """Defines valid keys in the config."""
    API_KEY: str
    AZURE_DEPLOYMENT: str
    AZURE_ENDPOINT: str
    BASE_URL: str
    CREDENTIALS_PATH: str
    MODEL_KWARGS: str
    MODEL_NAME: str
    MODEL_CLASS_PATH: str

def build_em_invoker(model_id: str | ModelId, credentials: str | dict[str, Any] | None = None, config: dict[str, Any] | None = None) -> BaseEMInvoker:
    '''Build an embedding model invoker based on the provided configurations.

    Args:
        model_id (str | ModelId): The model id, can either be a ModelId instance or a string in the following format:
            1. For `azure-openai` provider: `azure-openai/azure-endpoint:azure-deployment`.
            2. For `openai-compatible` provider: `openai-compatible/base-url:model-name`.
            3. For `langchain` provider: `langchain/<package>.<class>:model-name`.
            4. For other providers: `provider/model-name`.
        credentials (str | dict[str, Any] | None, optional): The credentials for the language model. Can either be:
            1. An API key.
            2. A path to a credentials JSON file, currently only supported for Google Vertex AI.
            3. A dictionary of credentials, currently only supported for LangChain.
            Defaults to None, in which case the credentials will be loaded from the appropriate environment variables.
        config (dict[str, Any] | None, optional): Additional configuration for the embedding model. Defaults to None.

    Returns:
        BaseEMInvoker: The initialized embedding model invoker.

    Raises:
        ValueError: If the provider is invalid.

    Usage examples:
        # Using Google Gen AI (via API key)
        ```python
        em_invoker = build_em_invoker(
            model_id="google/text-embedding-004",
            credentials="AIzaSyD..."
        )
        ```
        The credentials can also be provided through the `GOOGLE_API_KEY` environment variable.

        # Using Google Vertex AI (via service account)
        ```python
        em_invoker = build_em_invoker(
            model_id="google/text-embedding-004",
            credentials="/path/to/google-credentials.json"
        )
        ```
        Providing credentials through environment variable is not supported for Google Vertex AI.

        # Using OpenAI
        ```python
        em_invoker = build_em_invoker(
            model_id="openai/text-embedding-3-small",
            credentials="sk-..."
        )
        ```
        The credentials can also be provided through the `OPENAI_API_KEY` environment variable.

        # Using Azure OpenAI
        ```python
        em_invoker = build_em_invoker(
            model_id="azure-openai/https://my-resource.openai.azure.com:my-deployment",
            credentials="azure-api-key"
        )
        ```
        The credentials can also be provided through the `AZURE_OPENAI_API_KEY` environment variable.

        # Using OpenAI Compatible endpoint (e.g. Text Embeddings Inference)
        ```python
        em_invoker = build_em_invoker(
            model_id="openai-compatible/https://my-text-embeddings-inference-endpoint.com:model-name",
            credentials="tei-api-key"
        )
        ```
        The credentials can also be provided through the `OPENAI_API_KEY` environment variable.

        # Using TwelveLabs
        ```python
        em_invoker = build_em_invoker(
            model_id="twelvelabs/Marengo-retrieval-2.7",
            credentials="tlk_..."
        )
        ```
        The credentials can also be provided through the `TWELVELABS_API_KEY` environment variable.

        # Using Voyage
        ```python
        em_invoker = build_em_invoker(
            model_id="voyage/voyage-3.5-lite",
            credentials="sk-..."
        )
        ```
        The credentials can also be provided through the `VOYAGE_API_KEY` environment variable.

        # Using LangChain
        ```python
        em_invoker = build_em_invoker(
            model_id="langchain/langchain_openai.OpenAIEmbeddings:text-embedding-3-small",
            credentials={"api_key": "sk-..."}
        )
        ```
        The credentials can also be provided through various environment variables depending on the
        LangChain module being used. For the list of supported providers and the supported environment
        variables credentials, please refer to the following page:
        https://python.langchain.com/docs/integrations/text_embedding/

    Security warning:
        Please provide the EM invoker credentials ONLY to the `credentials` parameter. Do not put any kind of
        credentials in the `config` parameter as the content of the `config` parameter will be logged.
    '''
