from pydantic import BaseModel

class Reasoning(BaseModel):
    """Defines a reasoning output when a language model is configured to use reasoning.

    Attributes:
        id (str): The ID of the reasoning output. Defaults to an empty string.
        reasoning (str): The reasoning text. Defaults to an empty string.
        type (str): The type of the reasoning output. Defaults to an empty string.
        data (str): The additional data of the reasoning output. Defaults to an empty string.
    """
    id: str
    reasoning: str
    type: str
    data: str
