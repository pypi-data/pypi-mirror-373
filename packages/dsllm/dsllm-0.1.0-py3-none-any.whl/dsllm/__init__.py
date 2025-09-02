"""
dsllm - Generate Domain Specific Language statements from Natural Language input using LLMs

A Python library for converting natural language descriptions into structured DSL statements
with support for multiple LLM providers, syntax validation, and context injection.
"""

from .core import DSLLMGenerator
from .providers import OpenAIProvider
from .generators import SQLGenerator
from .exceptions import DSLLMError, GenerationError, ValidationError

__version__ = "0.1.0"
__author__ = "Frenk Dragar"
__email__ = "frenkd@users.noreply.github.com"

__all__ = [
    "DSLLMGenerator",
    "OpenAIProvider", 
    "SQLGenerator",
    "DSLLMError",
    "GenerationError",
    "ValidationError",
]
