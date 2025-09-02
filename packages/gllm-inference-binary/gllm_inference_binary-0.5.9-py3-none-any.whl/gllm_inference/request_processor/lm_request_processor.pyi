from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser
from gllm_inference.prompt_builder.prompt_builder import PromptBuilder as PromptBuilder
from gllm_inference.schema import LMOutput as LMOutput, Message as Message, MessageContent as MessageContent, ResponseSchema as ResponseSchema, ToolCall as ToolCall, ToolResult as ToolResult
from langchain_core.tools import Tool as Tool
from typing import Any

class LMRequestProcessor:
    """A request processor to perform language models inference.

    The `LMRequestProcessor` class handles the process of building a prompt, invoking a language model, and optionally
    parsing the output. It combines a prompt builder, language model invoker, and an optional output parser to manage
    the inference process in Gen AI applications.

    Attributes:
        prompt_builder (PromptBuilder): The prompt builder used to format the prompt.
        lm_invoker (BaseLMInvoker): The language model invoker that handles the model inference.
        output_parser (BaseOutputParser | None): The optional parser to process the model's output, if any.
        tool_dict (dict[str, Tool]): A dictionary of tools provided to the language model to enable tool calling,
            if any. The dictionary maps the tool name to the tools themselves.
    """
    prompt_builder: Incomplete
    lm_invoker: Incomplete
    output_parser: Incomplete
    tool_dict: Incomplete
    def __init__(self, prompt_builder: PromptBuilder, lm_invoker: BaseLMInvoker, output_parser: BaseOutputParser | None = None) -> None:
        """Initializes a new instance of the LMRequestProcessor class.

        Args:
            prompt_builder (PromptBuilder): The prompt builder used to format the prompt.
            lm_invoker (BaseLMInvoker): The language model invoker that handles the model inference.
            output_parser (BaseOutputParser, optional): An optional parser to process the model's output.
                Defaults to None.
        """
    def set_tools(self, tools: list[Tool]) -> None:
        """Sets the tools for the LM invoker.

        This method sets the tools for the LM invoker. Any existing tools will be replaced.

        Args:
            tools (list[Tool]): The list of tools to be used.
        """
    def clear_tools(self) -> None:
        """Clears the tools for the LM invoker.

        This method clears the tools for the LM invoker.
        """
    def set_response_schema(self, response_schema: ResponseSchema | None) -> None:
        """Sets the response schema for the LM invoker.

        This method sets the response schema for the LM invoker. Any existing response schema will be replaced.

        Args:
            response_schema (ResponseSchema | None): The response schema to be used.
        """
    def clear_response_schema(self) -> None:
        """Clears the response schema for the LM invoker.

        This method clears the response schema for the LM invoker.
        """
    async def process(self, prompt_kwargs: dict[str, Any] | None = None, history: list[Message] | None = None, extra_contents: list[MessageContent] | None = None, hyperparameters: dict[str, Any] | None = None, event_emitter: EventEmitter | None = None, auto_execute_tools: bool = True, max_lm_calls: int = 5) -> Any:
        """Processes a language model inference request.

        This method processes the language model inference request as follows:
        1. Assembling the prompt using the provided keyword arguments.
        2. Invoking the language model with the assembled prompt and optional hyperparameters.
        3. If `auto_execute_tools` is True, the method will automatically execute tools if the LM output includes
           tool calls.
        4. Optionally parsing the model's output using the output parser if provided. If the model output is an
           LMOutput object, the output parser will process the `response` attribute of the LMOutput object.

        Args:
            prompt_kwargs (dict[str, Any], optional): A dictionary of arguments used to format the prompt.
                Defaults to None, in which case no arguments will be passed to the prompt builder.
            history (list[Message] | None, optional): A list of conversation history to be included in the prompt.
                Defaults to None.
            extra_contents (list[MessageContent] | None, optional): A list of extra contents to be included in the
                user message. Defaults to None.
            hyperparameters (dict[str, Any] | None, optional): A dictionary of hyperparameters for the model invocation.
                Defaults to None.
            event_emitter (EventEmitter | None, optional): An event emitter for streaming model outputs.
                Defaults to None.
            auto_execute_tools (bool, optional): Whether to automatically execute tools if the LM invokes output
                tool calls. Defaults to True.
            max_lm_calls (int, optional): The maximum number of times the language model can be invoked
                when `auto_execute_tools` is True. Defaults to 5.

        Returns:
            Any: The result of the language model invocation, optionally parsed by the output parser.
        """
