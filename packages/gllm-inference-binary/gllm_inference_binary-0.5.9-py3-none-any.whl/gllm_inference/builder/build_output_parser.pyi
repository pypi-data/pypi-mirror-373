from _typeshed import Incomplete
from gllm_inference.output_parser import JSONOutputParser as JSONOutputParser
from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser

OUTPUT_PARSER_TYPE_MAP: Incomplete

def build_output_parser(output_parser_type: str) -> BaseOutputParser | None:
    '''Build an output parser based on the provided configurations.

    Args:
        output_parser_type (str): The type of output parser to use. Supports "json" and "none".

    Returns:
        BaseOutputParser: The initialized output parser.

    Raises:
        ValueError: If the provided type is not supported.

    Usage examples:
        # Using JSON output parser
        ```python
        output_parser = build_output_parser(output_parser_type="json")
        ```

        # Not using output parser
        ```python
        output_parser = build_output_parser(output_parser_type="none")
        ```
    '''
