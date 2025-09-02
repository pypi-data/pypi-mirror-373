from gllm_inference.output_parser.output_parser import BaseOutputParser as BaseOutputParser
from typing import Any

class JSONOutputParser(BaseOutputParser[dict[str, Any]]):
    '''An output parser that parses a json object from the language model output.

    The `JSONOutputParser` class searches for the first opening curly brace `{` and the last closing curly brace `}`
    in the language model\'s output to identify and extract a JSON object. It then parses the extracted substring into
    a Python dictionary. This method relies on finding a well-formed JSON structure enclosed by the first and last
    curly braces in the string. If the result contains additional curly braces outside the JSON object, or if there
    are multiple JSON objects, this parser will not function correctly and will raise a `ValueError`.

    Example:
    If the result is:
    ```
    "Here is the data: {\\"key\\": \\"value\\"} and some other text."
    ```
    The parser will extract the `{"key": "value"}` JSON object.

    However, if the result contains multiple JSON objects or nested data, such as:
    ```
    "Here are two JSONs: {\\"key1\\": \\"value1\\"} and {\\"key2\\": \\"value2\\"}"
    ```
    The parser will not handle this correctly, as it only extracts the content between the first `{` and the last `}`.
    '''
    def parse(self, result: str) -> dict[str, Any]:
        '''Parses the raw output string to extract and decode a JSON object.

        This method searches the provided string for the first opening curly brace `{` and the last closing curly
        brace `}` to identify a JSON object. It extracts the substring between these braces and attempts to parse it
        as a JSON object. The method raises a `ValueError` if no valid JSON structure is found or if the JSON is
        malformed.

        Note:
            This approach relies on the first `{` and the last `}` in the string. It will fail if:
            - The result contains curly braces outside the intended JSON object.
            - There are multiple JSON objects within the string, as it only processes the first and last braces.

        Example:
            If the result is:
            ```
            "Here is the data: {\\"key\\": \\"value\\"} and some other text."
            ```
            The parser will extract and return the `{"key": "value"}` object.

            However, if the result is:
            ```
            "Here are two JSONs: {\\"key1\\": \\"value1\\"} and {\\"key2\\": \\"value2\\"}"
            ```
            The parser will incorrectly attempt to parse everything between the first `{` and the last `}`.

        Args:
            result (str): The raw output string from the language model.

        Returns:
            dict[str, Any]: The parsed JSON object as a Python dictionary.

        Raises:
            ValueError: If no valid JSON object is found or if the JSON string is invalid.
        '''
