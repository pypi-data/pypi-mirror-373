from _typeshed import Incomplete
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.constants import GOOGLE_SCOPES as GOOGLE_SCOPES, SECONDS_TO_MILLISECONDS as SECONDS_TO_MILLISECONDS
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker as BaseEMInvoker
from gllm_inference.em_invoker.schema.google import Key as Key
from gllm_inference.schema import ModelId as ModelId, ModelProvider as ModelProvider, Vector as Vector
from typing import Any

SUPPORTED_ATTACHMENTS: Incomplete

class GoogleEMInvoker(BaseEMInvoker):
    '''An embedding model invoker to interact with Google embedding models.

    Attributes:
        model_id (str): The model ID of the embedding model.
        model_provider (str): The provider of the embedding model.
        model_name (str): The name of the embedding model.
        client_params (dict[str, Any]): The Google client instance init parameters.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the embedding model.
        retry_config (RetryConfig | None): The retry configuration for the language model.

    Initialization:
        The `GoogleEMInvoker` can use either Google Gen AI or Google Vertex AI.

        Google Gen AI is recommended for quick prototyping and development.
        It requires a Gemini API key for authentication.

        Usage example:
        ```python
        em_invoker = GoogleEMInvoker(
            model_name="text-embedding-004",
            api_key="your_api_key"
        )
        ```

        Google Vertex AI is recommended to build production-ready applications.
        It requires a service account JSON file for authentication.

        Usage example:
        ```python
        em_invoker = GoogleEMInvoker(
            model_name="text-embedding-004",
            credentials_path="path/to/service_account.json"
        )
        ```

        If neither `api_key` nor `credentials_path` is provided, Google Gen AI will be used by default.
        The `GOOGLE_API_KEY` environment variable will be used for authentication.

    Input types:
        The `GoogleEMInvoker` only supports text inputs.

    Output format:
        The `GoogleEMInvoker` can embed either:
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
        The `GoogleEMInvoker` supports retry and timeout configuration.
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
        em_invoker = GoogleEMInvoker(..., retry_config=retry_config)
        ```
    '''
    client_params: Incomplete
    def __init__(self, model_name: str, api_key: str | None = None, credentials_path: str | None = None, project_id: str | None = None, location: str = 'us-central1', model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, retry_config: RetryConfig | None = None) -> None:
        '''Initializes a new instance of the GoogleEMInvoker class.

        Args:
            model_name (str): The name of the model to use.
            api_key (str | None, optional): Required for Google Gen AI authentication. Cannot be used together
                with `credentials_path`. Defaults to None.
            credentials_path (str | None, optional): Required for Google Vertex AI authentication. Path to the service
                account credentials JSON file. Cannot be used together with `api_key`. Defaults to None.
            project_id (str | None, optional): The Google Cloud project ID for Vertex AI. Only used when authenticating
                with `credentials_path`. Defaults to None, in which case it will be loaded from the credentials file.
            location (str, optional): The location of the Google Cloud project for Vertex AI. Only used when
                authenticating with `credentials_path`. Defaults to "us-central1".
            model_kwargs (dict[str, Any] | None, optional): Additional keyword arguments for the Google client.
                Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            retry_config (RetryConfig | None, optional): The retry configuration for the embedding model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout will be used.

        Note:
            If neither `api_key` nor `credentials_path` is provided, Google Gen AI will be used by default.
            The `GOOGLE_API_KEY` environment variable will be used for authentication.
        '''
