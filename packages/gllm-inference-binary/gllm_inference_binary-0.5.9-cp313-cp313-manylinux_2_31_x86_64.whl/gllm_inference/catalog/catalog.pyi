import abc
from _typeshed import Incomplete
from abc import ABC
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')
logger: Incomplete

class BaseCatalog(ABC, BaseModel, Generic[T], arbitrary_types_allowed=True, metaclass=abc.ABCMeta):
    '''A base class for catalogs used for loading and managing various components in GLLM Inference.

    Attributes:
        components (dict[str, T]): A dictionary containing the components.

    Initialization:
        # Example 1: Load from Google Sheets using client email and private key
        ```python
        catalog = BaseCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            client_email="...",
            private_key="...",
        )
        component = catalog.name
        ```

        # Example 2: Load from Google Sheets using credential file
        ```python
        catalog = BaseCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            credential_file_path="...",
        )
        component = catalog.name
        ```

        # Example 3: Load from CSV
        ```python
        catalog = BaseCatalog.from_csv(csv_path="...")
        component = catalog.name
        ```

        # Example 4: Load from records
        ```python
        records = [
            {"name": "...", "col_1": "...", "col_2": "..."},
            {"name": "...", "col_1": "...", "col_2": "..."},
        ]
        catalog = BaseCatalog.from_records(records=records)
        component = catalog.name
    ```
    '''
    components: dict[str, T]
    def __getattr__(self, name: str) -> T:
        """Fetches a component by attribute name.

        This method attempts to retrieve a component from the `components` dictionary using the provided
        attribute name. If the attribute is not found, it raises an `AttributeError`.

        Args:
            name (str): The name of the attribute to fetch.

        Returns:
            T: The component associated with the given attribute name.

        Raises:
            AttributeError: If the attribute name does not exist in the `components` dictionary.
        """
    @classmethod
    def from_gsheets(cls, sheet_id: str, worksheet_id: str = '0', credential_file_path: str = None, client_email: str = None, private_key: str = None) -> BaseCatalog[T]:
        '''Creates a `BaseCatalog[T]` instance from Google Sheets data.

        This class method reads component data from a Google Sheets worksheet and initializes components
        based on the provided data. Authentication can be provided either by specifying the path to a `credential.json`
        file or by directly supplying the `client_email` and `private_key`.

        Args:
            sheet_id (str): The ID of the Google Sheet.
            worksheet_id (str): The ID of the worksheet within the Google Sheet. Defaults to "0"
            credential_file_path (str): The file path to the `credential.json` file. If provided, `client_email` and
                `private_key` are extracted from this file, effectively ignoring the `client_email` and `private_key`
                arguments. Defaults to None.
            client_email (str): The client email associated with the service account. This is ignored if
                `credential_file_path` is provided. Defaults to None.
            private_key (str): The private key used for authentication. This is ignored if `credential_file_path`
                is provided. Defaults to None.

        Returns:
            BaseCatalog[T]: An instance of `BaseCatalog[T]` initialized with components based on the
                Google Sheets data.

        Raises:
            ValueError: If authentication credentials are not provided or are invalid.
        '''
    @classmethod
    def from_csv(cls, csv_path: str) -> BaseCatalog[T]:
        """Creates a `BaseCatalog[T]` instance from CSV data.

        This class method reads component data from a CSV file and initializes components based on the provided data.

        Args:
            csv_path (str): The file path to the CSV containing component data.

        Returns:
            BaseCatalog[T]: An instance of `BaseCatalog[T]` initialized with components based on the
                CSV data.
        """
    @classmethod
    def from_records(cls, records: list[dict[str, str]]) -> BaseCatalog[T]:
        """Creates a `BaseCatalog[T]` instance from a list of records.

        This class method builds a catalog from the provided records.

        Args:
            records (list[dict[str, str]]): A list of records containing component data.

        Returns:
            BaseCatalog[T]: An instance of `BaseCatalog[T]` initialized with components based on the
                list of records.
        """
