from pydantic import BaseModel
from typing import Any

class ToolCall(BaseModel):
    """Defines a tool call request when a language model decides to invoke a tool.

    Attributes:
        id (str): The ID of the tool call.
        name (str): The name of the tool.
        args (dict[str, Any]): The arguments of the tool call.
    """
    id: str
    name: str
    args: dict[str, Any]
