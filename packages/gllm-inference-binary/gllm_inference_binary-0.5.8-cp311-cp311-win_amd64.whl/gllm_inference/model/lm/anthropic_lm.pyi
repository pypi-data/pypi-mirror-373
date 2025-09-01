class AnthropicLM:
    '''Defines Anthropic language model names constants.

    Usage example:
    ```python
    from gllm_inference.model import AnthropicLM
    from gllm_inference.lm_invoker import AnthropicLMInvoker

    lm_invoker = AnthropicLMInvoker(AnthropicLM.CLAUDE_SONNET_4)
    response = await lm_invoker.invoke("Hello, world!")
    ```
    '''
    CLAUDE_OPUS_4_1: str
    CLAUDE_OPUS_4: str
    CLAUDE_SONNET_4: str
    CLAUDE_SONNET_3_7: str
    CLAUDE_SONNET_3_5: str
    CLAUDE_HAIKU_3_5: str
    CLAUDE_OPUS_3: str
    CLAUDE_HAIKU_3: str
