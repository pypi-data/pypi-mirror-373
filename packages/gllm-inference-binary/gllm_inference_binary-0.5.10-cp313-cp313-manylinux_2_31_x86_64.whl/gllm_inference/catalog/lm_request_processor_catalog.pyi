from _typeshed import Incomplete
from gllm_inference.builder import build_lm_request_processor as build_lm_request_processor
from gllm_inference.catalog.catalog import BaseCatalog as BaseCatalog
from gllm_inference.request_processor import LMRequestProcessor as LMRequestProcessor

MODEL_ID_ENV_VAR_REGEX_PATTERN: str
LM_REQUEST_PROCESSOR_REQUIRED_COLUMNS: Incomplete
CONFIG_SCHEMA_MAP: Incomplete
logger: Incomplete

class LMRequestProcessorCatalog(BaseCatalog[LMRequestProcessor]):
    '''Loads multiple LM request processors from certain sources.

    Attributes:
        components (dict[str, LMRequestProcessor]): Dictionary of the loaded LM request processors.

    Initialization:
        # Example 1: Load from Google Sheets using client email and private key
        ```python
        catalog = LMRequestProcessorCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            client_email="...",
            private_key="...",
        )

        lm_request_processor = catalog.name
        ```

        # Example 2: Load from Google Sheets using credential file
        ```python
        catalog = LMRequestProcessorCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            credential_file_path="...",
        )

        lm_request_processor = catalog.name
        ```

        # Example 3: Load from CSV
        ```python
        catalog = LMRequestProcessorCatalog.from_csv(csv_path="...")

        lm_request_processor = catalog.name
        ```

        # Example 4: Load from record
        ```python
        records=[
            {
                "name": "answer_question",
                "system_template": (
                    "You are helpful assistant.\\n"
                    "Answer the following question based on the provided context.\\n"
                    "```{context}```"
                ),
                "user_template": "{query}",
                "key_defaults": \'{"context": "<default context>"}\',
                "model_id": "openai/gpt-4.1-nano",
                "credentials": "OPENAI_API_KEY",
                "config": "",
                "output_parser_type": "none",
            },
        ]
        catalog = LMRequestProcessorCatalog.from_records(records=records)
        lm_request_processor = catalog.answer_question
        ```

    Template Format Example:
        # Example 1: Google Sheets
        For an example of how a Google Sheets file can be formatted to be loaded using LMRequestProcessorCatalog, see:
        https://docs.google.com/spreadsheets/d/1CX9i45yEinv1UdB3s6uHNMj7mxr2-s1NFHfFDvMsq0E/edit?usp=drive_link

        # Example 2: CSV
        For an example of how a CSV file can be formatted to be loaded using LMRequestProcessorCatalog, see:
        https://drive.google.com/file/d/1_2rSoxh3CR2KZxIyUmpowMrt0Lm0YqAb/view?usp=drive_link

    Template Explanation:
        The required columns are:
        1. name (str): The name of the LM request processor.
        2. system_template (str): The system template of the prompt builder.
        3. user_template (str): The user template of the prompt builder.
        4. key_defaults (json_str): The default values for the prompt template keys.
        5. model_id (str): The model ID of the LM invoker.
        6. credentials (str | json_str): The credentials of the LM invoker.
        7. config (json_str): The additional configuration of the LM invoker.
        8. output_parser_type (str): The type of the output parser.

        Important Notes:
        1. At least one of `system_template` or `user_template` must be filled.
        2. `key_defaults` is optional. If filled, must be a dictionary containing the default values for the
            prompt template keys. These default values will be applied when the corresponding keys are not provided
            in the runtime input. If it is empty, the prompt template keys will not have default values.
        3. The `model_id`:
            3.1. Must be filled with the model ID of the LM invoker, e.g. "openai/gpt-4.1-nano".
            3.2. Can be partially loaded from the environment variable using the "${ENV_VAR_KEY}" syntax,
                e.g. "azure-openai/${AZURE_ENDPOINT}/${AZURE_DEPLOYMENT}".
            3.3. For the available model ID formats, see: https://gdplabs.gitbook.io/sdk/resources/supported-models
        4. `credentials` is optional. If it is filled, it can either be:
            4.1. An environment variable name containing the API key (e.g. OPENAI_API_KEY).
            4.2. An environment variable name containing the path to a credentials JSON file
                (e.g. GOOGLE_CREDENTIALS_FILE_PATH). Currently only supported for Google Vertex AI.
            4.3. A dictionary of credentials, with each value being an environment variable name corresponding to the
                credential (e.g. {"api_key": "OPENAI_API_KEY"}). Currently supported for Bedrock and LangChain.
            If it is empty, the LM invoker will use the default credentials loaded from the environment variables.
        5. `config` is optional. If filled, must be a dictionary containing the configuration for the LM invoker.
            If it is empty, the LM invoker will use the default configuration.
        6. `output_parser_type` can either be:
            6.1. none: No output parser will be used.
            6.2. json: The JSONOutputParser will be used.
    '''
