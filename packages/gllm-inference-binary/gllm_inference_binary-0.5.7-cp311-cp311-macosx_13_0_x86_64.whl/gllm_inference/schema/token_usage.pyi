from pydantic import BaseModel

class TokenUsage(BaseModel):
    """Defines the token usage data structure of a language model.

    Attributes:
        input_tokens (int): The number of input tokens.
        output_tokens (int): The number of output tokens.
    """
    input_tokens: int
    output_tokens: int
