from gllm_inference.schema.attachment import Attachment as Attachment
from pydantic import BaseModel

class CodeExecResult(BaseModel):
    """Defines a code execution result when a language model is configured to execute code.

    Attributes:
        id (str): The ID of the code execution. Defaults to an empty string.
        code (str): The executed code. Defaults to an empty string.
        output (list[str | Attachment]): The output of the executed code. Defaults to an empty list.
    """
    id: str
    code: str
    output: list[str | Attachment]
