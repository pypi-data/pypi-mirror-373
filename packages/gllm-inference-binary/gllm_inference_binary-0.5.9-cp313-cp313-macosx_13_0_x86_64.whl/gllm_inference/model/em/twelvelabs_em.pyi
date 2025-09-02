class TwelveLabsEM:
    '''Defines TwelveLabs embedding model names constants.

    Usage example:
    ```python
    from gllm_inference.model import TwelveLabsEM
    from gllm_inference.em_invoker import TwelveLabsEMInvoker

    em_invoker = TwelveLabsEMInvoker(TwelveLabsEM.MARENGO_RETRIEVAL_2_7)
    result = await em_invoker.invoke("Hello, world!")
    ```
    '''
    MARENGO_RETRIEVAL_2_7: str
