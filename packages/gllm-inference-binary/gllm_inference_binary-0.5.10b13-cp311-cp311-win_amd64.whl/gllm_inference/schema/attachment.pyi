from _typeshed import Incomplete
from gllm_inference.constants import HEX_REPR_LENGTH as HEX_REPR_LENGTH
from pydantic import BaseModel

logger: Incomplete

class Attachment(BaseModel):
    """Defines a file attachment schema.

    Attributes:
        data (bytes): The content data of the file attachment.
        filename (str): The filename of the file attachment.
        mime_type (str): The mime type of the file attachment.
        extension (str): The extension of the file attachment.
        url (str | None): The URL of the file attachment. Defaults to None.
    """
    data: bytes
    filename: str
    mime_type: str
    extension: str
    url: str | None
    @classmethod
    def from_bytes(cls, bytes: bytes, filename: str | None = None) -> Attachment:
        """Creates an Attachment from bytes.

        Args:
            bytes (bytes): The bytes of the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the extension.

        Returns:
            Attachment: The instantiated Attachment.
        """
    @classmethod
    def from_base64(cls, base64_data: str, filename: str | None = None) -> Attachment:
        """Creates an Attachment from a base64 string.

        Args:
            base64_data (str): The base64 string of the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the mime type.

        Returns:
            Attachment: The instantiated Attachment.
        """
    @classmethod
    def from_data_url(cls, data_url: str, filename: str | None = None) -> Attachment:
        """Creates an Attachment from a data URL (data:[mime/type];base64,[bytes]).

        Args:
            data_url (str): The data URL of the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the mime type.

        Returns:
            Attachment: The instantiated Attachment.
        """
    @classmethod
    def from_url(cls, url: str, filename: str | None = None) -> Attachment:
        """Creates an Attachment from a URL.

        Args:
            url (str): The URL of the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the URL.

        Returns:
            Attachment: The instantiated Attachment.
        """
    @classmethod
    def from_path(cls, path: str, filename: str | None = None) -> Attachment:
        """Creates an Attachment from a path.

        Args:
            path (str): The path to the file.
            filename (str | None, optional): The filename of the file. Defaults to None,
                in which case the filename will be derived from the path.

        Returns:
            Attachment: The instantiated Attachment.
        """
    def write_to_file(self, path: str | None = None) -> None:
        """Writes the Attachment to a file.

        Args:
            path (str | None, optional): The path to the file. Defaults to None,
                in which case the filename will be used as the path.
        """
