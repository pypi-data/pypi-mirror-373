"""
Type definitions for dsllm library.
"""

from typing import Any, Dict, List, Optional, Protocol
from abc import ABC, abstractmethod
from pydantic import BaseModel


class GenerationRequest(BaseModel):
    """Request object for DSL generation."""
    natural_language: str
    context: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None
    max_retries: int = 3


class GenerationResult(BaseModel):
    """Result object for DSL generation."""
    dsl_statement: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = []
    retry_count: int = 0


class ValidationResult(BaseModel):
    """Result of validation checks."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class LLMProvider(Protocol):
    """Protocol for LLM providers."""
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate text using the LLM."""
        ...


class DSLGenerator(ABC):
    """Abstract base class for DSL generators."""
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this DSL type."""
        pass
    
    @abstractmethod
    def format_user_prompt(self, request: GenerationRequest) -> str:
        """Format the user prompt for generation."""
        pass
    
    @abstractmethod
    def validate_syntax(self, dsl_statement: str) -> ValidationResult:
        """Validate the syntax of generated DSL."""
        pass
    
    @abstractmethod
    def pre_flight_check(self, request: GenerationRequest) -> ValidationResult:
        """Perform pre-flight validation checks."""
        pass
    
    @abstractmethod
    def post_flight_check(
        self, 
        request: GenerationRequest, 
        result: str
    ) -> ValidationResult:
        """Perform post-flight validation checks."""
        pass
