"""
Tests for SQL generator.
"""

from dsllm.generators.sql import SQLGenerator
from dsllm.types import GenerationRequest


class TestSQLGenerator:
    
    def setup_method(self):
        self.generator = SQLGenerator()
        self.read_only_generator = SQLGenerator(enforce_read_only=True)
    
    def test_system_prompt_generation(self):
        """Test system prompt generation."""
        prompt = self.generator.get_system_prompt()
        assert "SQL" in prompt
        assert "syntactically correct" in prompt
    
    def test_read_only_system_prompt(self):
        """Test read-only system prompt."""
        prompt = self.read_only_generator.get_system_prompt()
        assert "ONLY generate SELECT statements" in prompt
    
    def test_user_prompt_formatting(self):
        """Test user prompt formatting."""
        request = GenerationRequest(
            natural_language="Find all users",
            context={"schema": "CREATE TABLE users (id INT)"}
        )
        
        prompt = self.generator.format_user_prompt(request)
        assert "Find all users" in prompt
        assert "CREATE TABLE users" in prompt
    
    def test_syntax_validation_valid_sql(self):
        """Test syntax validation with valid SQL."""
        valid_sql = "SELECT * FROM users WHERE id = 1;"
        result = self.generator.validate_syntax(valid_sql)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_syntax_validation_invalid_sql(self):
        """Test syntax validation with invalid SQL."""
        invalid_sql = "not a sql statement"
        result = self.generator.validate_syntax(invalid_sql)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_read_only_validation(self):
        """Test read-only mode validation."""
        dangerous_sql = "DELETE FROM users WHERE id = 1;"
        result = self.read_only_generator.validate_syntax(dangerous_sql)
        
        assert not result.is_valid
        assert any("DELETE" in error for error in result.errors)
    
    def test_pre_flight_check_valid(self):
        """Test pre-flight check with valid input."""
        request = GenerationRequest(natural_language="Find all active users")
        result = self.generator.pre_flight_check(request)
        
        assert result.is_valid
    
    def test_pre_flight_check_empty_input(self):
        """Test pre-flight check with empty input."""
        request = GenerationRequest(natural_language="")
        result = self.generator.pre_flight_check(request)
        
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_pre_flight_check_read_only_warning(self):
        """Test pre-flight check in read-only mode (simplified stub)."""
        request = GenerationRequest(natural_language="Delete old users")
        result = self.read_only_generator.pre_flight_check(request)
        
        # With simplified stub, it just checks basic input validation
        assert result.is_valid
        # TODO: Add read-only warnings when validation is expanded
