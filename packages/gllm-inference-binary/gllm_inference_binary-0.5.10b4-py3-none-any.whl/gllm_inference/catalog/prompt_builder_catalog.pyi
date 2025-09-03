from _typeshed import Incomplete
from gllm_inference.catalog.catalog import BaseCatalog as BaseCatalog
from gllm_inference.prompt_builder.prompt_builder import PromptBuilder as PromptBuilder

PROMPT_BUILDER_REQUIRED_COLUMNS: Incomplete
logger: Incomplete

class PromptBuilderCatalog(BaseCatalog[PromptBuilder]):
    '''Loads multiple prompt builders from certain sources.

    Attributes:
        components (dict[str, PromptBuilder]): Dictionary of the loaded prompt builders.

    Initialization:
        # Example 1: Load from Google Sheets using client email and private key
        ```python
        catalog = PromptBuilderCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            client_email="...",
            private_key="...",
        )
        prompt_builder = catalog.name
        ```

        # Example 2: Load from Google Sheets using credential file
        ```python
        catalog = PromptBuilderCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            credential_file_path="...",
        )
        prompt_builder = catalog.name
        ```

        # Example 3: Load from CSV
        ```python
        catalog = PromptBuilderCatalog.from_csv(csv_path="...")
        prompt_builder = catalog.name
        ```

        # Example 4: Load from records
        ```python
        records=[
            {
                "name": "answer_question",
                "system": (
                    "You are helpful assistant.\\n"
                    "Answer the following question based on the provided context.\\n"
                    "```{context}```"
                ),
                "user": "{query}",
                "key_defaults": \'{"context": "<default context>"}\',
            },
        ]
        catalog = PromptBuilderCatalog.from_records(records=records)
        prompt_builder = catalog.answer_question
        ```

    Template Example:
        # Example 1: Google Sheets
        For an example of how a Google Sheets file can be formatted to be loaded using PromptBuilderCatalog, see:
        https://docs.google.com/spreadsheets/d/12IwSKv8hMhyWXSQnLx9LgCj0cxaR1f9gOmbEDGleurE/edit?usp=drive_link

        # Example 2: CSV
        For an example of how a CSV file can be formatted to be loaded using PromptBuilderCatalog, see:
        https://drive.google.com/file/d/1KQgddMdbcZBZmroQFtjSl-TKLohq84Fz/view?usp=drive_link


    Template explanation:
        The required columns are:
        1. name (str): The name of the prompt builder.
        2. system (str): The system template of the prompt builder.
        3. user (str): The user template of the prompt builder.
        4. key_defaults (json_str): The default values for the prompt template keys.

        Important Notes:
        1. At least one of the `system` and `user` columns must be filled.
        2. `key_defaults` is optional. If filled, must be a dictionary containing the default values for the
            prompt template keys. These default values will be applied when the corresponding keys are not provided
            in the runtime input. If it is empty, the prompt template keys will not have default values.
    '''
