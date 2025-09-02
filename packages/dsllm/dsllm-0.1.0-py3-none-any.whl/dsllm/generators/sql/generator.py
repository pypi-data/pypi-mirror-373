"""
Main SQL generator that orchestrates preflight, generation, and postflight.
"""

import logging

from ...types import DSLGenerator, GenerationRequest, ValidationResult
from .validation import SQLPreflightValidator
from .postflight import SQLPostflightValidator
from .prompt import SQLPromptGenerator

logger = logging.getLogger(__name__)


class SQLGenerator(DSLGenerator):
    """
    SQL DSL generator implementation.
    
    This class orchestrates the three main components:
    - Preflight validation (input validation)
    - Generation (prompt formatting and LLM interaction)
    - Postflight validation (output validation)
    """
    
    def __init__(self, enforce_read_only: bool = False):
        """
        Initialize SQL generator.
        
        Args:
            enforce_read_only: If True, only allow SELECT statements
        """
        self.enforce_read_only = enforce_read_only
        
        # Initialize component modules
        self.preflight_validator = SQLPreflightValidator(enforce_read_only=enforce_read_only)
        self.postflight_validator = SQLPostflightValidator(enforce_read_only=enforce_read_only)
        self.prompt_generator = SQLPromptGenerator()
        
        logger.info(f"Initialized SQLGenerator with read_only={enforce_read_only}")
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for SQL generation.
        
        Returns:
            System prompt string
        """
        return self.prompt_generator.get_system_prompt(enforce_read_only=self.enforce_read_only)
    
    def format_user_prompt(self, request: GenerationRequest) -> str:
        """
        Format the user prompt for SQL generation.
        
        Args:
            request: Generation request containing natural language and context
            
        Returns:
            Formatted user prompt with context and constraints
        """
        return self.prompt_generator.format_user_prompt(request)
    
    def validate_syntax(self, dsl_statement: str) -> ValidationResult:
        """
        Validate the syntax of generated SQL.
        
        Args:
            dsl_statement: The generated SQL statement
            
        Returns:
            ValidationResult with syntax validation status
        """
        # Create a dummy request for the postflight validator
        dummy_request = GenerationRequest(natural_language="")
        return self.postflight_validator.validate(dummy_request, dsl_statement)
    
    def pre_flight_check(self, request: GenerationRequest) -> ValidationResult:
        """
        Perform pre-flight validation checks.
        
        Args:
            request: The generation request to validate
            
        Returns:
            ValidationResult with pre-flight validation status
        """
        return self.preflight_validator.validate(request)
    
    def post_flight_check(
        self, 
        request: GenerationRequest, 
        result: str
    ) -> ValidationResult:
        """
        Perform post-flight validation checks.
        
        Args:
            request: The original generation request
            result: The generated SQL statement
            
        Returns:
            ValidationResult with post-flight validation status
        """
        return self.postflight_validator.validate(request, result)
    
    # Convenience methods for accessing component functionality
    
    def get_generator_info(self) -> dict:
        """
        Get information about the current SQL generator.
        
        Returns:
            Dictionary with generator information
        """
        return {
            "enforce_read_only": self.enforce_read_only,
        }
