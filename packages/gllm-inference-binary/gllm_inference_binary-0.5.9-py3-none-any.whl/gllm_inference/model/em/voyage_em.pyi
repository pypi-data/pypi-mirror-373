class VoyageEM:
    '''Defines Voyage embedding model names constants.

    Usage example:
    ```python
    from gllm_inference.model import VoyageEM
    from gllm_inference.em_invoker import VoyageEMInvoker

    em_invoker = VoyageEMInvoker(VoyageEM.VOYAGE_3_5_LITE)
    result = await em_invoker.invoke("Hello, world!")
    ```
    '''
    VOYAGE_3_5: str
    VOYAGE_3_5_LITE: str
    VOYAGE_3_LARGE: str
    VOYAGE_CODE_3: str
    VOYAGE_FINANCE_2: str
    VOYAGE_LAW_2: str
    VOYAGE_CODE_2: str
    VOYAGE_MULTIMODAL_3: str
