from pydantic import BaseModel

class InputTokenDetails(BaseModel):
    """Defines the input token details schema.

    Attributes:
        cached_tokens (int): The number of cached tokens. Defaults to 0.
        uncached_tokens (int): The number of uncached tokens. Defaults to 0.
    """
    cached_tokens: int
    uncached_tokens: int
    def __add__(self, other: InputTokenDetails) -> InputTokenDetails:
        """Add two InputTokenDetails objects together.

        Args:
            other (InputTokenDetails): The other InputTokenDetails object to add.

        Returns:
            InputTokenDetails: A new InputTokenDetails object with summed values.
        """

class OutputTokenDetails(BaseModel):
    """Defines the output token details schema.

    Attributes:
        reasoning_tokens (int): The number of reasoning tokens. Defaults to 0.
        response_tokens (int): The number of response tokens. Defaults to 0.
    """
    reasoning_tokens: int
    response_tokens: int
    def __add__(self, other: OutputTokenDetails) -> OutputTokenDetails:
        """Add two OutputTokenDetails objects together.

        Args:
            other (OutputTokenDetails): The other OutputTokenDetails object to add.

        Returns:
            OutputTokenDetails: A new OutputTokenDetails object with summed values.
        """

class TokenUsage(BaseModel):
    """Defines the token usage data structure of a language model.

    Attributes:
        input_tokens (int): The number of input tokens. Defaults to 0.
        output_tokens (int): The number of output tokens. Defaults to 0.
        input_token_details (InputTokenDetails | None): The details of the input tokens. Defaults to None.
        output_token_details (OutputTokenDetails | None): The details of the output tokens. Defaults to None.
    """
    input_tokens: int
    output_tokens: int
    input_token_details: InputTokenDetails | None
    output_token_details: OutputTokenDetails | None
    @classmethod
    def from_token_details(cls, input_tokens: int | None = None, output_tokens: int | None = None, cached_tokens: int | None = None, reasoning_tokens: int | None = None) -> TokenUsage:
        """Creates a TokenUsage from token details.

        Args:
            input_tokens (int | None): The number of input tokens. Defaults to None.
            output_tokens (int | None): The number of output tokens. Defaults to None.
            cached_tokens (int | None): The number of cached tokens. Defaults to None.
            reasoning_tokens (int | None): The number of reasoning tokens. Defaults to None.

        Returns:
            TokenUsage: The instantiated TokenUsage.
        """
    def __add__(self, other: TokenUsage) -> TokenUsage:
        """Add two TokenUsage objects together.

        Args:
            other (TokenUsage): The other TokenUsage object to add.

        Returns:
            TokenUsage: A new TokenUsage object with summed values.
        """
