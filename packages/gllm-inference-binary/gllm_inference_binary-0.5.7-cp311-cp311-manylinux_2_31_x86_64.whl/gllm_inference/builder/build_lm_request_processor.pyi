from _typeshed import Incomplete
from gllm_inference.builder.build_lm_invoker import build_lm_invoker as build_lm_invoker
from gllm_inference.builder.build_output_parser import build_output_parser as build_output_parser
from gllm_inference.prompt_builder import PromptBuilder as PromptBuilder
from gllm_inference.request_processor.lm_request_processor import LMRequestProcessor as LMRequestProcessor
from gllm_inference.schema.model_id import ModelId as ModelId
from typing import Any

logger: Incomplete

def build_lm_request_processor(model_id: str | ModelId, credentials: str | dict[str, Any] | None = None, config: dict[str, Any] | None = None, system_template: str = '', user_template: str = '', key_defaults: dict[str, Any] | None = None, output_parser_type: str = 'none') -> LMRequestProcessor:
    '''Build a language model invoker based on the provided configurations.

    Args:
        model_id (str | ModelId): The model id, can either be a ModelId instance or a string in the following format:
            1. For `azure-openai` provider: `azure-openai/azure-endpoint:azure-deployment`.
            2. For `openai-compatible` provider: `openai-compatible/base-url:model-name`.
            3. For `langchain` provider: `langchain/<package>.<class>:model-name`.
            4. For `litellm` provider: `litellm/provider/model-name`.
            5. For `datasaur` provider: `datasaur/base-url`.
            6. For other providers: `provider/model-name`.
        credentials (str | dict[str, Any] | None, optional): The credentials for the language model. Can either be:
            1. An API key.
            2. A path to a credentials JSON file, currently only supported for Google Vertex AI.
            3. A dictionary of credentials, currently supported for Bedrock and LangChain.
            Defaults to None, in which case the credentials will be loaded from the appropriate environment variables.
        config (dict[str, Any] | None, optional): Additional configuration for the language model. Defaults to None.
        system_template (str): The system prompt template. May contain placeholders enclosed in curly braces `{}`.
            Defaults to an empty string.
        user_template (str): The user prompt template. May contain placeholders enclosed in curly braces `{}`.
            Defaults to an empty string.
        key_defaults (dict[str, str] | None, optional): Default values for the keys in the prompt templates.
            Applied when the corresponding keys are not provided in the runtime input.
            Defaults to None, in which case no default values will be assigned to the keys.
        output_parser_type (str, optional): The type of output parser to use. Supports "json" and "none".
            Defaults to "none".

    Returns:
        LMRequestProcessor: The initialized language model request processor.

    Raises:
        ValueError: If the provided configuration is invalid.

    Usage examples:
        ```python
        # Basic usage
        lm_request_processor = build_lm_request_processor(
            model_id="openai/gpt-4o-mini",
            credentials="sk-...",
            user_template="{query}",
        )
        ```

        # With custom LM invoker configuration
        ```python
        config = {
            "default_hyperparameters": {"temperature": 0.5},
            "tools": [tool_1, tool_2],
        }

        lm_request_processor = build_lm_request_processor(
            model_id="openai/gpt-4o-mini",
            credentials="sk-...",
            config=config,
            user_template="{query}",
        )
        ```

        # With custom prompt builder configuration
        ```python
        lm_request_processor = build_lm_request_processor(
            model_id="openai/gpt-4o-mini",
            credentials="sk-...",
            system_template="Talk like a {role}.",
            user_template="{query}",
            key_defaults={"role": "pirate"},
        )
        ```

        # With output parser
        ```python
        lm_request_processor = build_lm_request_processor(
            model_id="openai/gpt-4o-mini",
            credentials="sk-...",
            user_template="{query}",
            output_parser_type="json",
        )
        ```

    Security warning:
        Please provide the LM invoker credentials ONLY to the `credentials` parameter. Do not put any kind of
        credentials in the `config` parameter as the content of the `config` parameter will be logged.
    '''
