from gllm_core.schema import Chunk as Chunk
from gllm_inference.schema.code_exec_result import CodeExecResult as CodeExecResult
from gllm_inference.schema.reasoning import Reasoning as Reasoning
from gllm_inference.schema.token_usage import TokenUsage as TokenUsage
from gllm_inference.schema.tool_call import ToolCall as ToolCall
from pydantic import BaseModel
from typing import Any

class LMOutput(BaseModel):
    """Defines the output of a language model.

    Attributes:
        response (str): The text response. Defaults to an empty string.
        tool_calls (list[ToolCall]): The tool calls, if the language model decides to invoke tools.
            Defaults to an empty list.
        structured_output (dict[str, Any] | BaseModel | None): The structured output, if a response schema is defined
            for the language model. Defaults to None.
        token_usage (TokenUsage | None): The token usage analytics, if requested. Defaults to None.
        duration (float | None): The duration of the invocation in seconds, if requested. Defaults to None.
        finish_details (dict[str, Any]): The details about how the generation finished, if requested.
            Defaults to an empty dictionary.
        reasoning (list[Reasoning]): The reasoning, if the language model is configured to output reasoning.
            Defaults to an empty list.
        citations (list[Chunk]): The citations, if the language model outputs citations. Defaults to an empty list.
        code_exec_results (list[CodeExecResult]): The code execution results, if the language model decides to
            execute code. Defaults to an empty list.
    """
    response: str
    tool_calls: list[ToolCall]
    structured_output: dict[str, Any] | BaseModel | None
    token_usage: TokenUsage | None
    duration: float | None
    finish_details: dict[str, Any]
    reasoning: list[Reasoning]
    citations: list[Chunk]
    code_exec_results: list[CodeExecResult]
