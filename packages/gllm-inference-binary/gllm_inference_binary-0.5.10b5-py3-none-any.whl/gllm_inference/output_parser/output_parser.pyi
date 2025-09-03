import abc
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class BaseOutputParser(ABC, Generic[T], metaclass=abc.ABCMeta):
    """A base class for output parsers used in Gen AI applications.

    The `BaseOutputParser` class defines the interface for parsing the output of language models.
    Subclasses must implement the `parse` method to process and extract meaningful data from the raw output.
    """
    @abstractmethod
    def parse(self, result: str) -> T:
        """Parses the raw output string from the language model.

        This abstract method must be implemented by subclasses to define how the result is parsed and processed.

        Args:
            result (str): The raw output string from the language model.

        Returns:
            T: The parsed result of type T.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
