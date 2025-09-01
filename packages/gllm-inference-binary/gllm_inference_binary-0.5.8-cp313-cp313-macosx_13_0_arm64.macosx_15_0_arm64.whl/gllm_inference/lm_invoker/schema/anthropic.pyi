class Key:
    """Defines valid keys in Anthropic."""
    BUDGET_TOKENS: str
    CONTENT: str
    DATA: str
    DESCRIPTION: str
    ID: str
    INPUT: str
    INPUT_SCHEMA: str
    MAX_RETRIES: str
    MEDIA_TYPE: str
    MAX_TOKENS: str
    NAME: str
    PARAMETERS: str
    ROLE: str
    SIGNATURE: str
    SOURCE: str
    STOP_REASON: str
    SYSTEM: str
    TIMEOUT: str
    THINKING: str
    TOOLS: str
    TOOL_CHOICE: str
    TOOL_USE_ID: str
    TEXT: str
    TYPE: str

class InputType:
    """Defines valid input types in Anthropic."""
    BASE64: str
    ENABLED: str
    REDACTED_THINKING: str
    TEXT: str
    THINKING: str
    TOOL: str
    TOOL_RESULT: str
    TOOL_USE: str

class OutputType:
    """Defines valid output types in Anthropic."""
    CONTENT_BLOCK_DELTA: str
    CONTENT_BLOCK_START: str
    CONTENT_BLOCK_STOP: str
    MESSAGE_STOP: str
    REDACTED_THINKING: str
    TEXT: str
    TEXT_DELTA: str
    THINKING: str
    THINKING_DELTA: str
    TOOL_USE: str
