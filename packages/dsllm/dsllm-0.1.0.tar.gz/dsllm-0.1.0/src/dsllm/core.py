"""
Core functionality for dsllm library.
"""

import logging
from typing import Any, Dict, Optional

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .types import (
    DSLGenerator,
    GenerationRequest,
    GenerationResult,
    LLMProvider,
)
from .exceptions import GenerationError, ValidationError, RetryExhaustedError

logger = logging.getLogger(__name__)


class DSLLMGenerator:
    """Main generator class that orchestrates DSL generation."""
    
    def __init__(
        self,
        provider: LLMProvider,
        dsl_generator: DSLGenerator,
        enable_validation: bool = True,
    ):
        """
        Initialize the DSLLM generator.
        
        Args:
            provider: LLM provider instance
            dsl_generator: DSL-specific generator instance
            enable_validation: Whether to enable validation checks
        """
        self.provider = provider
        self.dsl_generator = dsl_generator
        self.enable_validation = enable_validation
    
    async def generate(
        self, 
        natural_language: str,
        context: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> GenerationResult:
        """
        Generate DSL statement from natural language input.
        
        Args:
            natural_language: Natural language description
            context: Additional context (e.g., DDL schemas)
            constraints: Generation constraints
            max_retries: Maximum retry attempts
            
        Returns:
            GenerationResult with the generated DSL statement
        """
        request = GenerationRequest(
            natural_language=natural_language,
            context=context,
            constraints=constraints,
            max_retries=max_retries,
        )
        
        # Pre-flight validation
        if self.enable_validation:
            pre_flight = self.dsl_generator.pre_flight_check(request)
            if not pre_flight.is_valid:
                raise ValidationError(f"Pre-flight validation failed: {pre_flight.errors}")
        
        # Generate with retries
        try:
            result = await self._generate_with_retries(request)
            return result
        except Exception as e:
            logger.error(f"Generation failed after retries: {e}")
            raise RetryExhaustedError(f"Failed to generate valid DSL after {max_retries} attempts") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(GenerationError),
    )
    async def _generate_with_retries(self, request: GenerationRequest) -> GenerationResult:
        """Generate DSL with retry logic."""
        
        # Format prompts
        system_prompt = self.dsl_generator.get_system_prompt()
        user_prompt = self.dsl_generator.format_user_prompt(request)
        
        # Generate using LLM
        try:
            dsl_statement = await self.provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise GenerationError(f"LLM generation failed: {e}") from e
        
        # Clean up the generated statement
        dsl_statement = self._clean_generated_statement(dsl_statement)
        
        # Validation checks
        validation_errors = []
        
        if self.enable_validation:
            # Syntax validation
            syntax_result = self.dsl_generator.validate_syntax(dsl_statement)
            if not syntax_result.is_valid:
                validation_errors.extend(syntax_result.errors)
            
            # Post-flight validation
            post_flight = self.dsl_generator.post_flight_check(request, dsl_statement)
            if not post_flight.is_valid:
                validation_errors.extend(post_flight.errors)
            
            # If validation failed, raise error to trigger retry
            if validation_errors:
                raise GenerationError(f"Validation failed: {validation_errors}")
        
        return GenerationResult(
            dsl_statement=dsl_statement,
            validation_errors=validation_errors,
            metadata={
                "provider": self.provider.__class__.__name__,
                "generator": self.dsl_generator.__class__.__name__,
            }
        )
    
    def _clean_generated_statement(self, statement: str) -> str:
        """Clean up the generated DSL statement."""
        # Remove common LLM artifacts
        statement = statement.strip()
        
        # Remove markdown code blocks if present
        if statement.startswith("```"):
            lines = statement.split("\n")
            if len(lines) > 1:
                # Remove first line (```sql or similar)
                lines = lines[1:]
                # Remove last line if it's just ```
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                statement = "\n".join(lines).strip()
        
        return statement
