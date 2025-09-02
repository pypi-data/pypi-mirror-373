from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser
from gllm_inference.prompt_builder.prompt_builder import PromptBuilder as PromptBuilder
from gllm_inference.request_processor.lm_request_processor import LMRequestProcessor as LMRequestProcessor
from typing import Any

class UsesLM:
    '''A mixin to initialize classes that use LMRequestProcessor by providing the components directly.

    This mixin should be extended by classes that use LMRequestProcessor. Extending this mixin allows the class to
    create an instance of itself by providing the LMRequestProcessor components directly.

    For example:
    ```python
    class LMBasedComponent(BaseComponent, UsesLM):
        def __init__(self, lm_request_processor: LMRequestProcessor, custom_kwarg: str):
            self.lm_request_processor = lm_request_processor
            self.custom_kwarg = custom_kwarg
    ```

    Then, the class can be instantiated with the following:
    ```python
    component = LMBasedComponent.from_lm_components(
        prompt_builder,
        lm_invoker,
        output_parser,
        **{"custom_kwarg": "custom_value"},
    )
    ```

    Note:
        Classes that extend this mixin must have a constructor that accepts the LMRequestProcessor instance as its
        first argument.
    '''
    @classmethod
    def from_lm_components(cls, prompt_builder: PromptBuilder, lm_invoker: BaseLMInvoker, output_parser: BaseOutputParser | None = None, **kwargs: Any):
        """Creates an instance by initializing LMRequestProcessor with given components.

        This method is a shortcut to initialize the class by providing the LMRequestProcessor components directly.

        Args:
            prompt_builder (PromptBuilder): The prompt builder used to format the prompt.
            lm_invoker (BaseLMInvoker): The language model invoker that handles the model inference.
            output_parser (BaseOutputParser, optional): An optional parser to process the model's output.
                Defaults to None.
            **kwargs (Any): Additional keyword arguments to be passed to the class constructor.

        Returns:
            An instance of the class that mixes in this mixin.
        """
