from _typeshed import Incomplete
from langchain_core.embeddings import Embeddings as Embeddings
from langchain_core.language_models import BaseChatModel as BaseChatModel
from typing import Any

MODEL_NAME_KEYS: Incomplete

def load_langchain_model(model_class_path: str, model_name: str, model_kwargs: dict[str, Any]) -> BaseChatModel | Embeddings:
    '''Loads the LangChain\'s model instance.

    Args:
        model_class_path (str): The path to the LangChain\'s class, e.g. "langchain_openai.ChatOpenAI".
        model_name (str): The model name.
        model_kwargs (dict[str, Any]): The additional keyword arguments.

    Returns:
        BaseChatModel | Embeddings: The LangChain\'s model instance.
    '''
def parse_model_data(model: BaseChatModel | Embeddings) -> dict[str, str]:
    """Parses the model data from LangChain's BaseChatModel or Embeddings instance.

    Args:
        model (BaseChatModel | Embeddings): The LangChain's BaseChatModel or Embeddings instance.

    Returns:
        dict[str, str]: The dictionary containing the model name and path.

    Raises:
        ValueError: If the model name is not found in the model data.
    """
