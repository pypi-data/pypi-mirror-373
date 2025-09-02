"""
Exception classes for dsllm library.
"""


class DSLLMError(Exception):
    """Base exception class for dsllm library."""
    pass


class GenerationError(DSLLMError):
    """Raised when DSL generation fails."""
    pass


class ValidationError(DSLLMError):
    """Raised when validation checks fail."""
    pass


class ProviderError(DSLLMError):
    """Raised when LLM provider encounters an error."""
    pass


class RetryExhaustedError(DSLLMError):
    """Raised when all retry attempts are exhausted."""
    pass
