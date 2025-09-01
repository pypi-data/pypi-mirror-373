from enum import StrEnum

class Key:
    """Defines valid keys in OpenAI."""
    ARGUMENTS: str
    CALL_ID: str
    CONTAINER: str
    CONTENT: str
    DEFAULT: str
    DEFS: str
    EFFORT: str
    FILE_DATA: str
    FILENAME: str
    FORMAT: str
    FUNCTION: str
    ID: str
    IMAGE_URL: str
    INCLUDE: str
    INCOMPLETE_DETAILS: str
    INSTRUCTIONS: str
    JSON_SCHEMA: str
    MAX_RETRIES: str
    NAME: str
    OUTPUT: str
    PARAMETERS: str
    REASON: str
    REASONING: str
    ROLE: str
    SCHEMA: str
    REQUIRED: str
    STATUS: str
    STRICT: str
    SUMMARY: str
    TEXT: str
    TIMEOUT: str
    TITLE: str
    TOOLS: str
    TYPE: str

class InputType:
    """Defines valid input types in OpenAI."""
    AUTO: str
    CODE_INTERPRETER: str
    CODE_INTERPRETER_CALL_OUTPUTS: str
    FUNCTION: str
    FUNCTION_CALL: str
    FUNCTION_CALL_OUTPUT: str
    INPUT_FILE: str
    INPUT_IMAGE: str
    INPUT_TEXT: str
    JSON_SCHEMA: str
    NULL: str
    OUTPUT_TEXT: str
    REASONING: str
    SUMMARY_TEXT: str

class OutputType:
    """Defines valid output types in OpenAI."""
    CODE_INTERPRETER_CALL: str
    CODE_INTERPRETER_CALL_DELTA: str
    CODE_INTERPRETER_CALL_DONE: str
    CODE_INTERPRETER_CALL_IN_PROGRESS: str
    COMPLETED: str
    CONTAINER_FILE_CITATION: str
    FIND_IN_PAGE: str
    FUNCTION_CALL: str
    IMAGE: str
    INCOMPLETE: str
    ITEM_DONE: str
    MESSAGE: str
    OPEN_PAGE: str
    REASONING: str
    REASONING_ADDED: str
    REASONING_DELTA: str
    REASONING_DONE: str
    REFUSAL: str
    SEARCH: str
    TEXT_DELTA: str
    WEB_SEARCH_CALL: str

class ReasoningEffort(StrEnum):
    """Defines the reasoning effort for reasoning models."""
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class ReasoningSummary(StrEnum):
    """Defines the reasoning summary for reasoning models."""
    AUTO = 'auto'
    DETAILED = 'detailed'
