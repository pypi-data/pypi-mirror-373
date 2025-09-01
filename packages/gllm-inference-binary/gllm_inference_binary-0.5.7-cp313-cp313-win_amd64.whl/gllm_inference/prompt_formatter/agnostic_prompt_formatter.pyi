from _typeshed import Incomplete
from gllm_inference.prompt_formatter.prompt_formatter import BasePromptFormatter as BasePromptFormatter
from gllm_inference.schema import MessageRole as MessageRole

class AgnosticPromptFormatter(BasePromptFormatter):
    '''A prompt formatter that formats prompt without any specific model formatting.

    The `AgnosticPromptFormatter` class formats a prompt by joining the content of the prompt templates using a
    specified separator. It is designed to work independently of specific model types.

    Attributes:
        content_separator (str): A string used to separate each content in a message.
        message_separator (str): A string used to separate each message.

    Usage:
        The `AgnosticPromptFormatter` can be used to format a prompt for any model.
        The `content_separator` and `message_separator` can be customized to define the format of the prompt.

        Usage example:
        ```python
        prompt = [
            (MessageRole.USER, ["Hello", "how are you?"]),
            (MessageRole.ASSISTANT, ["I\'m fine", "thank you!"]),
            (MessageRole.USER, ["What is the capital of France?"]),
        ]
        prompt_formatter = AgnosticPromptFormatter(
            message_separator="\\n###\\n",
            content_separator="---"
        )
        print(prompt_formatter.format(prompt))
        ```

        Output example:
        ```
        Hello---how are you?
        ###
        I\'m fine---thank you!
        ###
        What is the capital of France?
        ```
    '''
    message_separator: Incomplete
    def __init__(self, message_separator: str = '\n', content_separator: str = '\n') -> None:
        '''Initializes a new instance of the AgnosticPromptFormatter class.

        Args:
            message_separator (str, optional): A string used to separate each message. Defaults to "\\n".
            content_separator (str, optional): A string used to separate each content in a message. Defaults to "\\n".
        '''
