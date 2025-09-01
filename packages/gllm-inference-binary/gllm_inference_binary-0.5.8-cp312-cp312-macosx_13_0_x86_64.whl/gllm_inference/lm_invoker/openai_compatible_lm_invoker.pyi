from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_core.schema.tool import Tool as Tool
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.constants import INVOKER_PROPAGATED_MAX_RETRIES as INVOKER_PROPAGATED_MAX_RETRIES
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.lm_invoker.schema.openai_compatible import InputType as InputType, Key as Key, ReasoningEffort as ReasoningEffort
from gllm_inference.schema import Attachment as Attachment, AttachmentType as AttachmentType, EmitDataType as EmitDataType, LMOutput as LMOutput, Message as Message, MessageRole as MessageRole, ModelId as ModelId, ModelProvider as ModelProvider, Reasoning as Reasoning, ResponseSchema as ResponseSchema, TokenUsage as TokenUsage, ToolCall as ToolCall, ToolResult as ToolResult
from gllm_inference.utils import validate_string_enum as validate_string_enum
from langchain_core.tools import Tool as LangChainTool
from typing import Any

SUPPORTED_ATTACHMENTS: Incomplete

class OpenAICompatibleLMInvoker(BaseLMInvoker):
    '''A language model invoker to interact with endpoints compatible with OpenAI\'s chat completion API contract.

    Attributes:
        model_id (str): The model ID of the language model.
        model_provider (str): The provider of the language model.
        model_name (str): The name of the language model.
        client (AsyncOpenAI): The OpenAI client instance.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
        tools (list[Tool]): The list of tools provided to the model to enable tool calling.
        response_schema (ResponseSchema | None): The schema of the response. If provided, the model will output a
            structured response as defined by the schema. Supports both Pydantic BaseModel and JSON schema dictionary.
        output_analytics (bool): Whether to output the invocation analytics.
        retry_config (RetryConfig | None): The retry configuration for the language model.

    When to use:
        The `OpenAICompatibleLMInvoker` is designed to interact with endpoints that are compatible with OpenAI\'s chat
        completion API contract. This includes but are not limited to:
        1. DeepInfra (https://deepinfra.com/)
        2. DeepSeek (https://deepseek.com/)
        3. Groq (https://groq.com/)
        4. OpenRouter (https://openrouter.ai/)
        5. Text Generation Inference (https://github.com/huggingface/text-generation-inference)
        6. Together.ai (https://together.ai/)
        7. vLLM (https://vllm.ai/)
        When using this invoker, please note that the supported features and capabilities may vary between different
        endpoints and language models. Using features that are not supported by the endpoint will result in an error.

    Basic usage:
        The `OpenAICompatibleLMInvoker` can be used as follows:
        ```python
        lm_invoker = OpenAICompatibleLMInvoker(
            model_name="llama3-8b-8192",
            base_url="https://api.groq.com/openai/v1",
            api_key="<your-api-key>"
        )
        result = await lm_invoker.invoke("Hi there!")
        ```

    Input types:
        The `OpenAICompatibleLMInvoker` supports the following input types: text, audio, and image.
        Non-text inputs can be passed as an `Attachment` object with the `user` role.

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
        lm_invoker = OpenAICompatibleLMInvoker(..., tools=[tool_1, tool_2])
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

        The language model also doesn\'t need to stream anything when structured output is enabled. Thus, standard
        invocation will be performed regardless of whether the `event_emitter` parameter is provided or not.

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
        lm_invoker = OpenAICompatibleLMInvoker(..., response_schema=schema)
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

        lm_invoker = OpenAICompatibleLMInvoker(..., response_schema=Animal)
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

        When streaming is enabled, token usage is not supported. Therefore, the `token_usage` attribute will be `None`
        regardless of the value of the `output_analytics` parameter.

    Retry and timeout:
        The `OpenAICompatibleLMInvoker` supports retry and timeout configuration.
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
        lm_invoker = OpenAICompatibleLMInvoker(..., retry_config=retry_config)
        ```

    Reasoning:
        Some language models support advanced reasoning capabilities. When using such reasoning-capable models,
        you can configure how much reasoning the model should perform before generating a final response by setting
        reasoning-related parameters.

        The reasoning effort of reasoning models can be set via the `reasoning_effort` parameter. This parameter
        will guide the models on how many reasoning tokens it should generate before creating a response to the prompt.
        The reasoning effort is only supported by some language models.
        Available options include:
        1. "low": Favors speed and economical token usage.
        2. "medium": Favors a balance between speed and reasoning accuracy.
        3. "high": Favors more complete reasoning at the cost of more tokens generated and slower responses.
        This may differ between models. When not set, the reasoning effort will be equivalent to None by default.

        When using reasoning models, some providers might output the reasoning summary. These will be stored in the
        `reasoning` attribute in the output.

        Output example:
        ```python
        LMOutput(
            response="Golden retriever is a good dog breed.",
            reasoning=[Reasoning(id="", reasoning="Let me think about it...")],
        )
        ```

        When streaming is enabled along with reasoning and the provider supports reasoning output, the reasoning token
        will be streamed with the `EventType.DATA` event type.

        Streaming output example:
        ```python
        {"type": "data", "value": \'{"data_type": "thinking_start", "data_value": ""}\', ...}
        {"type": "data", "value": \'{"data_type": "thinking", "data_value": "Let me think "}\', ...}
        {"type": "data", "value": \'{"data_type": "thinking", "data_value": "about it..."}\', ...}
        {"type": "data", "value": \'{"data_type": "thinking_end", "data_value": ""}\', ...}
        {"type": "response", "value": "Golden retriever ", ...}
        {"type": "response", "value": "is a good dog breed.", ...}

        Setting reasoning-related parameters for non-reasoning models will raise an error.

    Output types:
        The output of the `OpenAICompatibleLMInvoker` can either be:
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
    client: Incomplete
    def __init__(self, model_name: str, base_url: str, api_key: str | None = None, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, tools: list[Tool | LangChainTool] | None = None, response_schema: ResponseSchema | None = None, output_analytics: bool = False, retry_config: RetryConfig | None = None, reasoning_effort: ReasoningEffort | None = None) -> None:
        '''Initializes a new instance of the OpenAICompatibleLMInvoker class.

        Args:
            model_name (str): The name of the language model hosted on the OpenAI compatible endpoint.
            base_url (str): The base URL for the OpenAI compatible endpoint.
            api_key (str | None, optional): The API key for authenticating with the OpenAI compatible endpoint.
                Defaults to None, in which case the `OPENAI_API_KEY` environment variable will be used.
                If the endpoint does not require an API key, a dummy value can be passed (e.g. "<empty>").
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
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
            reasoning_effort (str | None, optional): The reasoning effort for the language model. Defaults to None.
        '''
    def set_response_schema(self, response_schema: ResponseSchema | None) -> None:
        """Sets the response schema for the language model hosted on the OpenAI compatible endpoint.

        This method sets the response schema for the language model hosted on the OpenAI compatible endpoint. Any
        existing response schema will be replaced.

        Args:
            response_schema (ResponseSchema | None): The response schema to be used.
        """
