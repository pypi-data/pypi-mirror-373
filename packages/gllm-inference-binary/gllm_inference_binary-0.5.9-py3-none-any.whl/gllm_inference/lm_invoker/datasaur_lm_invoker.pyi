from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_core.schema.tool import Tool as Tool
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.constants import DOCUMENT_MIME_TYPES as DOCUMENT_MIME_TYPES, INVOKER_PROPAGATED_MAX_RETRIES as INVOKER_PROPAGATED_MAX_RETRIES
from gllm_inference.lm_invoker.openai_compatible_lm_invoker import OpenAICompatibleLMInvoker as OpenAICompatibleLMInvoker
from gllm_inference.lm_invoker.schema.datasaur import InputType as InputType, Key as Key
from gllm_inference.schema import Attachment as Attachment, AttachmentType as AttachmentType, LMOutput as LMOutput, Message as Message, ModelId as ModelId, ModelProvider as ModelProvider, ResponseSchema as ResponseSchema, ToolCall as ToolCall, ToolResult as ToolResult
from langchain_core.tools import Tool as LangChainTool
from typing import Any

SUPPORTED_ATTACHMENTS: Incomplete

class DatasaurLMInvoker(OpenAICompatibleLMInvoker):
    '''A language model invoker to interact with Datasaur LLM Projects Deployment API.

    Attributes:
        model_id (str): The model ID of the language model.
        model_provider (str): The provider of the language model.
        model_name (str): The name of the language model.
        client (AsyncOpenAI): The OpenAI client instance.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
        tools (list[Any]): The list of tools provided to the model to enable tool calling. Currently not supported.
        response_schema (ResponseSchema | None): The schema of the response. Currently not supported.
        output_analytics (bool): Whether to output the invocation analytics.
        retry_config (RetryConfig | None): The retry configuration for the language model.
        citations (bool): Whether to output the citations.

    Basic usage:
        The `DatasaurLMInvoker` can be used as follows:
        ```python
        lm_invoker = DatasaurLMInvoker(base_url="https://deployment.datasaur.ai/api/deployment/teamId/deploymentId/")
        result = await lm_invoker.invoke("Hi there!")
        ```

    Input types:
        The `DatasaurLMInvoker` supports the following input types: text, audio, image, and document.
        Non-text inputs can be passed as an `Attachment` object with the `user` role.

        Usage example:
        ```python
        text = "What animal is in this image?"
        image = Attachment.from_path("path/to/local/image.png")
        result = await lm_invoker.invoke([text, image])
        ```

    Analytics tracking:
        Analytics tracking is a feature that allows the module to output additional information about the invocation.
        This feature can be enabled by setting the `output_analytics` parameter to `True`.
        When enabled, the following attributes will be stored in the output:
        1. `token_usage`: The token usage.
        2. `duration`: The duration in seconds.
        3. `finish_details`: The details about how the generation finished.

        Output example:
        ```python
        LMOutput(
            response="Golden retriever is a good dog breed.",
            token_usage=TokenUsage(input_tokens=100, output_tokens=50),
            duration=0.729,
            finish_details={"finish_reason": "stop"},
        )
        ```

        When streaming is enabled, token usage is not supported. Therefore, the `token_usage` attribute will be `None`
        regardless of the value of the `output_analytics` parameter.

    Retry and timeout:
        The `DatasaurLMInvoker` supports retry and timeout configuration.
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
        lm_invoker = DatasaurLMInvoker(..., retry_config=retry_config)
        ```

    Citations:
        The `DatasaurLMInvoker` can be configured to output the citations used to generate the response.
        They can be enabled by setting the `citations` parameter to `True`.
        When enabled, the citations will be stored as `Chunk` objects in the `citations` attribute in the output.

        Usage example:
        ```python
        lm_invoker = DatasaurLMInvoker(..., citations=True)
        ```

        Output example:
        ```python
        LMOutput(
            response="The winner of the match is team A ([Example title](https://www.example.com)).",
            citations=[Chunk(id="123", content="...", metadata={...}, score=0.95)],
        )
        ```

    Output types:
        The output of the `DatasaurLMInvoker` can either be:
        1. `str`: The text response if no additional output is needed.
        2. `LMOutput`: A Pydantic model with the following attributes if any additional output is needed:
            2.1. response (str): The text response.
            2.2. tool_calls (list[ToolCall]): The tool calls. Currently not supported. Defaults to an empty list.
            2.3. structured_output (dict[str, Any] | BaseModel | None): The structured output. Currently not supported.
                Defaults to None.
            2.4. token_usage (TokenUsage | None): The token usage analytics, if the `output_analytics` parameter is
                set to `True`. Defaults to None.
            2.5. duration (float | None): The duration of the invocation in seconds, if the `output_analytics`
                parameter is set to `True`. Defaults to None.
            2.6. finish_details (dict[str, Any] | None): The details about how the generation finished, if the
                `output_analytics` parameter is set to `True`. Defaults to None.
            2.7. reasoning (list[Reasoning]): The reasoning objects. Currently not supported. Defaults to an empty list.
            2.8. citations (list[Chunk]): The citations. Currently not supported. Defaults to an empty list.
            2.9. code_exec_results (list[CodeExecResult]): The code execution results. Currently not supported.
                Defaults to an empty list.
    '''
    client: Incomplete
    citations: Incomplete
    def __init__(self, base_url: str, api_key: str | None = None, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, output_analytics: bool = False, retry_config: RetryConfig | None = None, citations: bool = False) -> None:
        """Initializes a new instance of the DatasaurLMInvoker class.

        Args:
            base_url (str): The base URL of the Datasaur LLM Projects Deployment API.
            api_key (str | None, optional): The API key for authenticating with Datasaur LLM Projects Deployment API.
                Defaults to None, in which case the `DATASAUR_API_KEY` environment variable will be used.
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            output_analytics (bool, optional): Whether to output the invocation analytics. Defaults to False.
            retry_config (RetryConfig | None, optional): The retry configuration for the language model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout will be used.
            citations (bool, optional): Whether to output the citations. Defaults to False.

        Raises:
            ValueError: If the `api_key` is not provided and the `DATASAUR_API_KEY` environment variable is not set.
        """
    def set_tools(self, tools: list[Tool | LangChainTool]) -> None:
        """Sets the tools for the Datasaur LLM Projects Deployment API.

        This method is raises a `NotImplementedError` because the Datasaur LLM Projects Deployment API does not
        support tools.

        Args:
            tools (list[Tool | LangChainTool]): The list of tools to be used.

        Raises:
            NotImplementedError: This method is not supported for the Datasaur LLM Projects Deployment API.
        """
    def set_response_schema(self, response_schema: ResponseSchema | None) -> None:
        """Sets the response schema for the Datasaur LLM Projects Deployment API.

        This method is raises a `NotImplementedError` because the Datasaur LLM Projects Deployment API does not
        support response schema.

        Args:
            response_schema (ResponseSchema | None): The response schema to be used.

        Raises:
            NotImplementedError: This method is not supported for the Datasaur LLM Projects Deployment API.
        """
