"""
Post-flight validation for SQL generation.
"""

import re
import logging

from ...types import GenerationRequest, ValidationResult

logger = logging.getLogger(__name__)


class SQLPostflightValidator:
    """Handles post-flight validation checks for SQL generation."""
    
    def __init__(self, enforce_read_only: bool = False):
        """
        Initialize the postflight validator.
        
        Args:
            enforce_read_only: If True, reject dangerous SQL operations
        """
        self.enforce_read_only = enforce_read_only
        self.dangerous_keywords = {
            "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"
        }
    
    def validate(self, request: GenerationRequest, result: str) -> ValidationResult:
        """
        Perform post-flight validation checks.
        
        Args:
            request: The original generation request
            result: The generated SQL statement
            
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors: list[str] = []
        warnings: list[str] = []
        
        # Basic validation
        if not result or len(result.strip()) == 0:
            errors.append("Generated SQL statement is empty")
            return ValidationResult(is_valid=False, errors=errors)
        
        statement = result.strip().upper()
        
        # Check for dangerous operations if read-only mode
        if self.enforce_read_only:
            for keyword in self.dangerous_keywords:
                if keyword in statement:
                    errors.append(f"Read-only mode: {keyword} statements are not allowed")
        
        # Check for basic SQL command
        if not re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b', statement):
            errors.append("No valid SQL command found")
        
        # TODO: Add more sophisticated validation later
        # - Syntax validation (parentheses, quotes)
        # - SQL injection detection
        # - Semantic validation
        # - Context consistency checks
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)