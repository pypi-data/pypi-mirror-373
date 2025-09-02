from gllm_inference.em_invoker.em_invoker import BaseEMInvoker as BaseEMInvoker
from gllm_inference.schema import Vector as Vector
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel
from typing import Any

class EMInvokerEmbeddings(BaseModel, Embeddings, arbitrary_types_allowed=True):
    """An adapter class that enables an `EMInvoker` to be used as a LangChain `Embeddings`.

    Attributes:
        em_invoker (BaseEMInvoker): The `EMInvoker` instance to be interacted with.

    Usage example:
    ```python
    from gllm_inference.em_invoker.langchain import EMInvokerEmbeddings
    from gllm_inference.em_invoker import OpenAIEMInvoker

    em_invoker = OpenAIEMInvoker(...)
    embeddings = EMInvokerEmbeddings(em_invoker=em_invoker)
    ```
    """
    em_invoker: BaseEMInvoker
    async def aembed_documents(self, texts: list[str], **kwargs: Any) -> list[Vector]:
        """Asynchronously embed documents using the `EMInvoker`.

        Args:
            texts (list[str]): The list of texts to embed.
            **kwargs (Any): Additional keyword arguments to pass to the EMInvoker's `invoke` method.

        Returns:
            list[Vector]: List of embeddings, one for each text.
        """
    async def aembed_query(self, text: str, **kwargs: Any) -> Vector:
        """Asynchronously embed query using the `EMInvoker`.

        Args:
            text (str): The text to embed.
            **kwargs (Any): Additional keyword arguments to pass to the EMInvoker's `invoke` method.

        Returns:
            Vector: Embeddings for the text.
        """
    def embed_documents(self, texts: list[str], **kwargs: Any) -> list[Vector]:
        """Embed documents using the `EMInvoker`.

        Args:
            texts (list[str]): The list of texts to embed.
            **kwargs (Any): Additional keyword arguments to pass to the EMInvoker's `invoke` method.

        Returns:
            list[Vector]: List of embeddings, one for each text.
        """
    def embed_query(self, text: str, **kwargs: Any) -> Vector:
        """Embed query using the `EMInvoker`.

        Args:
            text (str): The text to embed.
            **kwargs (Any): Additional keyword arguments to pass to the EMInvoker's `invoke` method.

        Returns:
            Vector: Embeddings for the text.
        """
