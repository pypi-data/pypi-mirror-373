from enum import StrEnum
from gllm_inference.utils import validate_string_enum as validate_string_enum
from pydantic import BaseModel

PROVIDER_SEPARATOR: str
PATH_SEPARATOR: str
URL_NAME_REGEX_PATTERN: str

class ModelProvider(StrEnum):
    """Defines the supported model providers."""
    ANTHROPIC = 'anthropic'
    AZURE_OPENAI = 'azure-openai'
    BEDROCK = 'bedrock'
    DATASAUR = 'datasaur'
    GOOGLE = 'google'
    LANGCHAIN = 'langchain'
    LITELLM = 'litellm'
    OPENAI = 'openai'
    OPENAI_COMPATIBLE = 'openai-compatible'
    TWELVELABS = 'twelvelabs'
    VOYAGE = 'voyage'

class ModelId(BaseModel):
    '''Defines a representation of a valid model id.

    Attributes:
        provider (ModelProvider): The provider of the model.
        name (str | None): The name of the model.
        path (str | None): The path of the model.

    Provider-specific examples:
        # Using Anthropic
        ```python
        model_id = ModelId.from_string("anthropic/claude-3-5-sonnet-latest")
        ```

        # Using Bedrock
        ```python
        model_id = ModelId.from_string("bedrock/us.anthropic.claude-sonnet-4-20250514-v1:0")
        ```

        # Using Datasaur
        ```python
        model_id = ModelId.from_string("datasaur/https://deployment.datasaur.ai/api/deployment/teamId/deploymentId/")
        ```

        # Using Google
        ```python
        model_id = ModelId.from_string("google/gemini-1.5-flash")
        ```

        # Using OpenAI
        ```python
        model_id = ModelId.from_string("openai/gpt-4o-mini")
        ```

        # Using Azure OpenAI
        ```python
        model_id = ModelId.from_string("azure-openai/https://my-resource.openai.azure.com:my-deployment")
        ```

        # Using OpenAI compatible endpoints (e.g. Groq)
        ```python
        model_id = ModelId.from_string("openai-compatible/https://api.groq.com/openai/v1:llama3-8b-8192")
        ```

        # Using Voyage
        ```python
        model_id = ModelId.from_string("voyage/voyage-3.5-lite")
        ```

        # Using TwelveLabs
        ```python
        model_id = ModelId.from_string("twelvelabs/Marengo-retrieval-2.7")
        ```

        # Using LangChain
        ```python
        model_id = ModelId.from_string("langchain/langchain_openai.ChatOpenAI:gpt-4o-mini")
        ```
        For the list of supported providers, please refer to the following table:
        https://python.langchain.com/docs/integrations/chat/#featured-providers

        # Using LiteLLM
        ```python
        model_id = ModelId.from_string("litellm/openai/gpt-4o-mini")
        ```
        For the list of supported providers, please refer to the following page:
        https://docs.litellm.ai/docs/providers/

    Custom model name validation example:
        ```python
        validation_map = {
            ModelProvider.ANTHROPIC: {"claude-3-5-sonnet-latest"},
            ModelProvider.GOOGLE: {"gemini-1.5-flash", "gemini-1.5-pro"},
            ModelProvider.OPENAI: {"gpt-4o", "gpt-4o-mini"},

        model_id = ModelId.from_string("...", validation_map)
        ```
    '''
    provider: ModelProvider
    name: str | None
    path: str | None
    @classmethod
    def from_string(cls, model_id: str, validation_map: dict[str, set[str]] | None = None) -> ModelId:
        """Parse a model id string into a ModelId object.

        Args:
            model_id (str): The model id to parse. Must be in the the following format:
                1. For `azure-openai` provider: `azure-openai/azure-endpoint:azure-deployment`.
                2. For `openai-compatible` provider: `openai-compatible/base-url:model-name`.
                3. For `langchain` provider: `langchain/<package>.<class>:model-name`.
                4. For `litellm` provider: `litellm/provider/model-name`.
                5. For `datasaur` provider: `datasaur/base-url`.
                6. For other providers: `provider/model-name`.
            validation_map (dict[str, set[str]] | None, optional): An optional dictionary that maps provider names to
                sets of valid model names. For the defined model providers, the model names will be validated against
                the set of valid model names. For the undefined model providers, the model name will not be validated.
                Defaults to None.

        Returns:
            ModelId: The parsed ModelId object.

        Raises:
            ValueError: If the provided model id is invalid or if the model name is not valid for the provider.
        """
    def to_string(self) -> str:
        """Convert the ModelId object to a string.

        Returns:
            str: The string representation of the ModelId object. The format is as follows:
                1. For `azure-openai` provider: `azure-openai/azure-endpoint:azure-deployment`.
                2. For `openai-compatible` provider: `openai-compatible/base-url:model-name`.
                3. For `langchain` provider: `langchain/<package>.<class>:model-name`.
                4. For `litellm` provider: `litellm/provider/model-name`.
                5. For `datasaur` provider: `datasaur/base-url`.
                6. For other providers: `provider/model-name`.
        """
