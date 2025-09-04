from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_core.schema.tool import Tool as Tool
from gllm_core.utils.retry import RetryConfig
from gllm_inference.constants import INVOKER_DEFAULT_TIMEOUT as INVOKER_DEFAULT_TIMEOUT, INVOKER_PROPAGATED_MAX_RETRIES as INVOKER_PROPAGATED_MAX_RETRIES
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.lm_invoker.schema.langchain import InputType as InputType, Key as Key
from gllm_inference.schema import Attachment as Attachment, AttachmentType as AttachmentType, LMOutput as LMOutput, Message as Message, MessageRole as MessageRole, ModelId as ModelId, ModelProvider as ModelProvider, ResponseSchema as ResponseSchema, TokenUsage as TokenUsage, ToolCall as ToolCall, ToolResult as ToolResult
from gllm_inference.utils import load_langchain_model as load_langchain_model, parse_model_data as parse_model_data
from langchain_core.language_models import BaseChatModel as BaseChatModel
from langchain_core.messages import BaseMessage as BaseMessage
from langchain_core.tools import Tool as LangChainTool
from typing import Any

SUPPORTED_ATTACHMENTS: Incomplete
MESSAGE_CLASS_MAP: Incomplete

class LangChainLMInvoker(BaseLMInvoker):
    '''A language model invoker to interact with LangChain\'s BaseChatModel.

    Attributes:
        model_id (str): The model ID of the language model.
        model_provider (str): The provider of the language model.
        model_name (str): The name of the language model.
        model (BaseChatModel): The LangChain\'s BaseChatModel instance.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
        tools (list[Any]): The list of tools provided to the model to enable tool calling.
        response_schema (ResponseSchema | None): The schema of the response. If provided, the model will output a
            structured response as defined by the schema. Supports both Pydantic BaseModel and JSON schema dictionary.
        output_analytics (bool): Whether to output the invocation analytics.
        retry_config (RetryConfig | None): The retry configuration for the language model.

    Basic usage:
        The `LangChainLMInvoker` can be used as follows:
        ```python
        lm_invoker = LangChainLMInvoker(
            model_class_path="langchain_openai.ChatOpenAI",
            model_name="gpt-4.1-nano",
        )
        result = await lm_invoker.invoke("Hi there!")
        ```

    Initialization:
        The `LangChainLMInvoker` can be initialized by either passing:

        1. A LangChain\'s BaseChatModel instance:
        Usage example:
        ```python
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(model="gpt-4.1-nano", api_key="your_api_key")
        lm_invoker = LangChainLMInvoker(model=model)
        ```

        2. A model path in the format of "<package>.<class>":
        Usage example:
        ```python
        lm_invoker = LangChainLMInvoker(
            model_class_path="langchain_openai.ChatOpenAI",
            model_name="gpt-4.1-nano",
            model_kwargs={"api_key": "your_api_key"}
        )
        ```
        For the list of supported providers, please refer to the following table:
        https://python.langchain.com/docs/integrations/chat/#featured-providers

    Input types:
        The `LangChainLMInvoker` supports the following input types: text and image.
        Non-text inputs can be passed as an `Attachment` object and with specific roles,
        depending on the language model\'s capabilities.

        Usage example:
        ```python
        text = "What animal is in this image?"
        image = Attachment.from_path("path/to/local/image.png")
        result = await lm_invoker.invoke([text, image])
        ```

    Tool calling:
        Tool calling is a feature that allows the language model to call tools to perform tasks.
        Tools can be passed to the via the `tools` parameter as a list of `Tool` objects.
        When tools are provided and the model decides to call a tool, the tool calls are stored in the
        `tool_calls` attribute in the output.

        Usage example:
        ```python
        lm_invoker = LangChainLMInvoker(..., tools=[tool_1, tool_2])
        ```

        Output example:
        ```python
        LMOutput(
            response="Let me call the tools...",
            tool_calls=[
                ToolCall(id="123", name="tool_1", args={"key": "value"}),
                ToolCall(id="456", name="tool_2", args={"key": "value"}),
            ]
        )
        ```

    Structured output:
        Structured output is a feature that allows the language model to output a structured response.
        This feature can be enabled by providing a schema to the `response_schema` parameter.

        The schema must be either a JSON schema dictionary or a Pydantic BaseModel class.
        If JSON schema is used, it must be compatible with Pydantic\'s JSON schema, especially for complex schemas.
        For this reason, it is recommended to create the JSON schema using Pydantic\'s `model_json_schema` method.

        Structured output is not compatible with tool calling. The language model also doesn\'t need to stream
        anything when structured output is enabled. Thus, standard invocation will be performed regardless of
        whether the `event_emitter` parameter is provided or not.

        When enabled, the structured output is stored in the `structured_output` attribute in the output.
        1. If the schema is a JSON schema dictionary, the structured output is a dictionary.
        2. If the schema is a Pydantic BaseModel class, the structured output is a Pydantic model.

        # Example 1: Using a JSON schema dictionary
        Usage example:
        ```python
        schema = {
            "title": "Animal",
            "description": "A description of an animal.",
            "properties": {
                "color": {"title": "Color", "type": "string"},
                "name": {"title": "Name", "type": "string"},
            },
            "required": ["name", "color"],
            "type": "object",
        }
        lm_invoker = LangChainLMInvoker(..., response_schema=schema)
        ```
        Output example:
        ```python
        LMOutput(structured_output={"name": "Golden retriever", "color": "Golden"})
        ```

        # Example 2: Using a Pydantic BaseModel class
        Usage example:
        ```python
        class Animal(BaseModel):
            name: str
            color: str

        lm_invoker = LangChainLMInvoker(..., response_schema=Animal)
        ```
        Output example:
        ```python
        LMOutput(structured_output=Animal(name="Golden retriever", color="Golden"))
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

    Retry and timeout:
        The `LangChainLMInvoker` supports retry and timeout configuration.
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
        lm_invoker = LangChainLMInvoker(..., retry_config=retry_config)
        ```

    Output types:
        The output of the `LangChainLMInvoker` can either be:
        1. `str`: The text response if no additional output is needed.
        2. `LMOutput`: A Pydantic model with the following attributes if any additional output is needed:
            2.1. response (str): The text response.
            2.2. tool_calls (list[ToolCall]): The tool calls, if the `tools` parameter is defined and the language
                model decides to invoke tools. Defaults to an empty list.
            2.3. structured_output (dict[str, Any] | BaseModel | None): The structured output, if the `response_schema`
                parameter is defined. Defaults to None.
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
    model: Incomplete
    def __init__(self, model: BaseChatModel | None = None, model_class_path: str | None = None, model_name: str | None = None, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, tools: list[Tool | LangChainTool] | None = None, response_schema: ResponseSchema | None = None, output_analytics: bool = False, retry_config: RetryConfig | None = None) -> None:
        '''Initializes a new instance of the LangChainLMInvoker class.

        Args:
            model (BaseChatModel | None, optional): The LangChain\'s BaseChatModel instance. If provided, will take
                precedence over the `model_class_path` parameter. Defaults to None.
            model_class_path (str | None, optional): The LangChain\'s BaseChatModel class path. Must be formatted as
                "<package>.<class>" (e.g. "langchain_openai.ChatOpenAI"). Ignored if `model` is provided.
                Defaults to None.
            model_name (str | None, optional): The model name. Only used if `model_class_path` is provided.
                Defaults to None.
            model_kwargs (dict[str, Any] | None, optional): The additional keyword arguments. Only used if
                `model_class_path` is provided. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            tools (list[Tool | LangChainTool] | None, optional): Tools provided to the model to enable tool calling.
                Defaults to None.
            response_schema (ResponseSchema | None, optional): The schema of the response. If provided, the model will
                output a structured response as defined by the schema. Supports both Pydantic BaseModel and JSON schema
                dictionary. Defaults to None.
            output_analytics (bool, optional): Whether to output the invocation analytics. Defaults to False.
            retry_config (RetryConfig | None, optional): The retry configuration for the language model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout will be used.

        Raises:
            ValueError: If `response_schema` is provided, but `tools` are also provided.
        '''
    tools: Incomplete
    def set_tools(self, tools: list[Tool | LangChainTool]) -> None:
        """Sets the tools for LangChain's BaseChatModel.

        This method sets the tools for LangChain's BaseChatModel. Any existing tools will be replaced.

        Args:
            tools (list[Tool]): The list of tools to be used.

        Raises:
            ValueError: If `response_schema` exists.
        """
    def set_response_schema(self, response_schema: ResponseSchema | None) -> None:
        """Sets the response schema for the LangChain's BaseChatModel.

        This method sets the response schema for the LangChain's BaseChatModel. Any existing response schema will be
        replaced.

        Args:
            response_schema (ResponseSchema | None): The response schema to be used.

        Raises:
            ValueError: If `tools` exists.
        """
