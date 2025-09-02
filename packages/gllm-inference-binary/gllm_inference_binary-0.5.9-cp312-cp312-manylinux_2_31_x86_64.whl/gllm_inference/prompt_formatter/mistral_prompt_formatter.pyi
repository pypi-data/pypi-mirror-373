from gllm_inference.prompt_formatter import HuggingFacePromptFormatter as HuggingFacePromptFormatter

class MistralPromptFormatter(HuggingFacePromptFormatter):
    '''A prompt formatter that formats prompt using Mistral model\'s specific formatting.

    The `MistralPromptFormatter` class is designed to format prompt using a Mistral model\'s specific formatting.
    It does so by using the model\'s tokenizer\'s `apply_chat_template` method.

    Attributes:
        content_separator (str): A string used to separate each content in a message.
        tokenizer (PreTrainedTokenizer): The HuggingFace model tokenizer used for chat templating.

    Usage:
        The `MistralPromptFormatter` can be used to format a prompt using a Mistral model\'s specific formatting.
        The `content_separator` and `model_name` can be customized to define the format of the prompt.
        The `model_name` defines the name of the HuggingFace model whose tokenizer will be used to format
        the prompt using the `apply_chat_template` method.

        Usage example:
        ```python
        prompt = [
            (MessageRole.USER, ["Hello", "how are you?"]),
            (MessageRole.ASSISTANT, ["I\'m fine", "thank you!"]),
            (MessageRole.USER, ["What is the capital of France?"]),
        ]
        prompt_formatter = MistralPromptFormatter(
            model_name_or_path="mistralai/Mistral-7B-Instruct-v0.1",
            content_separator="---"
        )
        print(prompt_formatter.format(prompt))
        ```

        Output example:
        ```
        <s>[INST] Hello---how are you? [/INST]I\'m fine---thank you!</s> [INST] What is the capital of France? [/INST]
        ```

    Using a gated model:
        If you\'re trying to access the prompt builder template of a gated model, you\'d need to:
        1. Request access to the gated repo using your HuggingFace account.
        2. Login to HuggingFace in your system. This can be done as follows:
           2.1. Install huggingface-hub: ```pip install huggingface-hub```
           2.2. Login to HuggingFace: ```huggingface-cli login```
           2.3. Enter your HuggingFace token.
    '''
    def __init__(self, model_name: str = 'Mistral-7B-Instruct-v0.3', content_separator: str = '\n') -> None:
        '''Initializes a new instance of the MistralPromptFormatter class.

        Args:
            model_name (str, optional): The name of the Mistral model tokenizer to be loaded. Defaults to
                `Mistral-7B-Instruct-v0.3`.
            content_separator (str, optional): A string used to separate each content in a message. Defaults to "\\n".
        '''
