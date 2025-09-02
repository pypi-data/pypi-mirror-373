"""
SQL generation logic and prompt formatting.
"""

import logging

from ...types import GenerationRequest

logger = logging.getLogger(__name__)


class SQLPromptGenerator:
    """Handles SQL prompt generation and formatting."""
    
    def __init__(self) -> None:
        """Initialize the SQL prompt generator."""
        pass
    
    def get_system_prompt(self, enforce_read_only: bool = False) -> str:
        """
        Generate the system prompt for SQL generation.
        
        Args:
            enforce_read_only: If True, restrict to SELECT statements only
            
        Returns:
            System prompt string
        """
        read_only_info = ""
        if enforce_read_only:
            read_only_info = " ONLY generate SELECT statements. Do not generate any data modification statements."
        
        return f"""You are an expert SQL developer. Generate syntactically correct SQL statements based on natural language descriptions.{read_only_info}

Rules:
1. Generate ONLY the SQL statement, no explanations or markdown
2. Use proper SQL syntax and formatting
3. Include appropriate JOINs when multiple tables are referenced
4. Use meaningful aliases for tables when needed
5. Consider performance implications (use LIMIT when appropriate)
6. Handle NULL values appropriately
7. Use parameterized query patterns when user input is involved

If the request is ambiguous, make reasonable assumptions based on common SQL patterns."""
    
    def format_user_prompt(self, request: GenerationRequest) -> str:
        """
        Format the user prompt for SQL generation.
        
        Args:
            request: The generation request containing natural language and context
            
        Returns:
            Formatted user prompt string
        """
        prompt_parts = [
            f"Generate a SQL statement for: {request.natural_language}"
        ]
        
        # Add context if provided
        if request.context:
            if "schema" in request.context:
                prompt_parts.append(f"\nDatabase schema:\n{request.context['schema']}")
            
            if "tables" in request.context:
                tables_info = "\n".join([f"- {table}" for table in request.context["tables"]])
                prompt_parts.append(f"\nAvailable tables:\n{tables_info}")
            
            if "sample_data" in request.context:
                prompt_parts.append(f"\nSample data:\n{request.context['sample_data']}")
        
        # Add constraints if provided
        if request.constraints:
            constraints_text = []
            
            if "max_rows" in request.constraints:
                constraints_text.append(f"Limit results to {request.constraints['max_rows']} rows")
            
            if "required_columns" in request.constraints:
                cols = ", ".join(request.constraints["required_columns"])
                constraints_text.append(f"Must include columns: {cols}")
            
            if "exclude_columns" in request.constraints:
                cols = ", ".join(request.constraints["exclude_columns"])
                constraints_text.append(f"Exclude columns: {cols}")
            
            if constraints_text:
                prompt_parts.append("\nConstraints:\n" + "\n".join(f"- {c}" for c in constraints_text))
        
        return "\n".join(prompt_parts)
