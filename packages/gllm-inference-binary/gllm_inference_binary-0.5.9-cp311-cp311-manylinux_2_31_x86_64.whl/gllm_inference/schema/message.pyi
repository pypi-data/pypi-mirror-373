from gllm_inference.schema.enums import MessageRole as MessageRole
from gllm_inference.schema.type_alias import MessageContent as MessageContent
from pydantic import BaseModel
from typing import Any

class Message(BaseModel):
    """Defines a message schema to be used as inputs for a language model.

    Attributes:
        role (MessageRole): The role of the message.
        contents (list[MessageContent]): The contents of the message.
        metadata (dict[str, Any]): The metadata of the message.
    """
    role: MessageRole
    contents: list[MessageContent]
    metadata: dict[str, Any]
    @classmethod
    def system(cls, contents: MessageContent | list[MessageContent], metadata: dict[str, Any] | None = None) -> Message:
        """Create a system message.

        Args:
            contents (MessageContent | list[MessageContent]): The message contents.
                If a single content is provided, it will be wrapped in a list.
            metadata (dict[str, Any], optional): Additional metadata for the message. Defaults to None.

        Returns:
            Message: A new message with SYSTEM role.
        """
    @classmethod
    def user(cls, contents: MessageContent | list[MessageContent], metadata: dict[str, Any] | None = None) -> Message:
        """Create a user message.

        Args:
            contents (MessageContent | list[MessageContent]): The message contents.
                If a single content is provided, it will be wrapped in a list.
            metadata (dict[str, Any], optional): Additional metadata for the message. Defaults to None.

        Returns:
            Message: A new message with USER role.
        """
    @classmethod
    def assistant(cls, contents: MessageContent | list[MessageContent], metadata: dict[str, Any] | None = None) -> Message:
        """Create an assistant message.

        Args:
            contents (MessageContent | list[MessageContent]): The message contents.
                If a single content is provided, it will be wrapped in a list.
            metadata (dict[str, Any], optional): Additional metadata for the message. Defaults to None.

        Returns:
            Message: A new message with ASSISTANT role.
        """
