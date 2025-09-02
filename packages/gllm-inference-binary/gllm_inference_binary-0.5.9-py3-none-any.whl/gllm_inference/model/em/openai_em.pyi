class OpenAIEM:
    '''Defines OpenAI embedding model names constants.

    Usage example:
    ```python
    from gllm_inference.model import OpenAIEM
    from gllm_inference.em_invoker import OpenAIEMInvoker

    em_invoker = OpenAIEMInvoker(OpenAIEM.TEXT_EMBEDDING_3_SMALL)
    result = await em_invoker.invoke("Hello, world!")
    ```
    '''
    TEXT_EMBEDDING_3_SMALL: str
    TEXT_EMBEDDING_3_LARGE: str
    TEXT_EMBEDDING_ADA_002: str
