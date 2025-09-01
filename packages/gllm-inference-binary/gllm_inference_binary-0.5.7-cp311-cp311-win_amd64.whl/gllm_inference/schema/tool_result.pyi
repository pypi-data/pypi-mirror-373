from pydantic import BaseModel

class ToolResult(BaseModel):
    """Defines a tool result to be sent back to the language model.

    Attributes:
        id (str): The ID of the tool call.
        output (str): The output of the tool call.
    """
    id: str
    output: str
