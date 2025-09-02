class GoogleEM:
    '''Defines Google embedding model names constants.

    Usage example:
    ```python
    from gllm_inference.model import GoogleEM
    from gllm_inference.em_invoker import GoogleEMInvoker

    em_invoker = GoogleEMInvoker(GoogleEM.GEMINI_EMBEDDING_001)
    result = await em_invoker.invoke("Hello, world!")
    ```
    '''
    GEMINI_EMBEDDING_001: str
    TEXT_EMBEDDING_004: str
    TEXT_EMBEDDING_005: str
    TEXT_MULTILINGUAL_EMBEDDING_002: str
