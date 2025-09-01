from _typeshed import Incomplete
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.constants import INVOKER_PROPAGATED_MAX_RETRIES as INVOKER_PROPAGATED_MAX_RETRIES
from gllm_inference.em_invoker.openai_em_invoker import OpenAIEMInvoker as OpenAIEMInvoker
from gllm_inference.em_invoker.schema.openai_compatible import Key as Key
from gllm_inference.schema import ModelId as ModelId, ModelProvider as ModelProvider
from typing import Any

class OpenAICompatibleEMInvoker(OpenAIEMInvoker):
    '''An embedding model invoker to interact with endpoints compatible with OpenAI\'s embedding API contract.

    Attributes:
        model_id (str): The model ID of the embedding model.
        model_provider (str): The provider of the embedding model.
        model_name (str): The name of the embedding model.
        client (AsyncOpenAI): The OpenAI client instance.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the embedding model.
        retry_config (RetryConfig): The retry configuration for the embedding model.

    When to use:
        The `OpenAICompatibleEMInvoker` is designed to interact with endpoints that are compatible with OpenAI\'s
        embedding API contract. This includes but are not limited to:
        1. Text Embeddings Inference (https://github.com/huggingface/text-embeddings-inference)
        2. vLLM (https://vllm.ai/)
        When using this invoker, please note that the supported features and capabilities may vary between different
        endpoints and language models. Using features that are not supported by the endpoint will result in an error.

    Input types:
        The `OpenAICompatibleEMInvoker` only supports text inputs.

    Output format:
        The `OpenAICompatibleEMInvoker` can embed either:
        1. A single content.
           1. A single content is a single text.
           2. The output will be a `Vector`, representing the embedding of the content.

           # Example 1: Embedding a text content.
           ```python
           text = "This is a text"
           result = await em_invoker.invoke(text)
           ```

           The above examples will return a `Vector` with a size of (embedding_size,).

        2. A list of contents.
           1. A list of contents is a list of texts.
           2. The output will be a `list[Vector]`, where each element is a `Vector` representing the
              embedding of each single content.

           # Example: Embedding a list of contents.
           ```python
           text1 = "This is a text"
           text2 = "This is another text"
           text3 = "This is yet another text"
           result = await em_invoker.invoke([text1, text2, text3])
           ```

           The above examples will return a `list[Vector]` with a size of (3, embedding_size).

    Retry and timeout:
        The `OpenAICompatibleEMInvoker` supports retry and timeout configuration.
        By default, the max retries is set to 0 and the timeout is set to 30.0 seconds.
        They can be customized by providing a custom `RetryConfig` object to the `retry_config` parameter.

        Retry config examples:
        ```python
        retry_config = RetryConfig(max_retries=0, timeout=0.0)  # No retry, no timeout
        retry_config = RetryConfig(max_retries=0, timeout=10.0)  # No retry, 10.0 seconds timeout
        retry_config = RetryConfig(max_retries=5, timeout=0.0)  # 5 max retries, no timeout
        retry_config = RetryConfig(max_retries=5, timeout=10.0)  # 5 max retries, 10.0 seconds timeout
        ```

        Usage example:
        ```python
        em_invoker = OpenAICompatibleEMInvoker(..., retry_config=retry_config)
        ```
    '''
    client: Incomplete
    def __init__(self, model_name: str, base_url: str, api_key: str | None = None, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, retry_config: RetryConfig | None = None) -> None:
        """Initializes a new instance of the OpenAICompatibleEMInvoker class.

        Args:
            model_name (str): The name of the embedding model hosted on the OpenAI compatible endpoint.
            base_url (str): The base URL for the OpenAI compatible endpoint.
            api_key (str | None, optional): The API key for authenticating with the OpenAI compatible endpoint.
                Defaults to None, in which case the `OPENAI_API_KEY` environment variable will be used.
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            retry_config (RetryConfig | None, optional): The retry configuration for the embedding model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout will be used.
        """
