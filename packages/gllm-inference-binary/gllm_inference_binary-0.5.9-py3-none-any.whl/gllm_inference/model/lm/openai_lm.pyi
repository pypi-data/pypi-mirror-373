class OpenAILM:
    '''Defines OpenAI language model names constants.

    Usage example:
    ```python
    from gllm_inference.model import OpenAILM
    from gllm_inference.lm_invoker import OpenAILMInvoker

    lm_invoker = OpenAILMInvoker(OpenAILM.GPT_5_NANO)
    response = await lm_invoker.invoke("Hello, world!")
    ```
    '''
    GPT_5: str
    GPT_5_MINI: str
    GPT_5_NANO: str
    GPT_4_1: str
    GPT_4_1_MINI: str
    GPT_4_1_NANO: str
    GPT_4O: str
    GPT_4O_MINI: str
    O4_MINI: str
    O4_MINI_DEEP_RESEARCH: str
    O3: str
    O3_PRO: str
    O3_DEEP_RESEARCH: str
    O1: str
    O1_PRO: str
