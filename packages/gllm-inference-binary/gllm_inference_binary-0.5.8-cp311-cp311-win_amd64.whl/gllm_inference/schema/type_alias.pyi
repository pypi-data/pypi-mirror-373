from aiohttp import ClientResponse
from gllm_inference.schema.code_exec_result import Attachment as Attachment
from gllm_inference.schema.reasoning import Reasoning as Reasoning
from gllm_inference.schema.tool_call import ToolCall as ToolCall
from gllm_inference.schema.tool_result import ToolResult as ToolResult
from httpx import Response as HttpxResponse
from pydantic import BaseModel
from requests import Response
from typing import Any

ErrorResponse = Response | HttpxResponse | ClientResponse | str | dict[str, Any]
ResponseSchema = dict[str, Any] | type[BaseModel]
MessageContent = str | Attachment | ToolCall | ToolResult | Reasoning
EMContent = str | Attachment | tuple[str | Attachment, ...]
Vector = list[float]
