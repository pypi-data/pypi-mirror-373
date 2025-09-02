# dsllm - Domain Specific Language from LLM

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate Domain Specific Language (DSL) statements from Natural Language input using Large Language Models (LLMs).

## Overview

`dsllm` is a Python library that converts natural language descriptions into structured DSL statements. Currently supports SQL generation with OpenAI models, designed to be extensible to other DSLs and LLM providers.

## Features

- **SQL Generation**: Convert natural language to SQL queries
- **OpenAI Integration**: Built-in support for GPT-3.5/4 models
- **Context Injection**: Support for database schemas and constraints
- **Validation**: Pre-flight and post-flight validation checks
- **Safety Features**: Read-only mode, dangerous operation detection
- **Retry Mechanism**: Automatic retries with exponential backoff

## Installation

```bash
pip install dsllm
```

## Quick Start

```python
import asyncio
import os
from dsllm import DSLLMGenerator, OpenAIProvider, SQLGenerator

async def main():
    # Initialize components
    provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    sql_generator = SQLGenerator()
    generator = DSLLMGenerator(provider=provider, dsl_generator=sql_generator)
    
    # Generate SQL from natural language
    result = await generator.generate(
        natural_language="Find all active users who registered this month",
        context={
            "schema": '''
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP
                );
            '''
        }
    )
    
    print("Generated SQL:")
    print(result.dsl_statement)

# Run the example
asyncio.run(main())
```

## Basic Usage

### Simple Query Generation

```python
result = await generator.generate("Show me all users")
print(result.dsl_statement)  # SELECT * FROM users;
```

### With Context and Constraints

```python
result = await generator.generate(
    "Find recent orders with high values",
    context={"tables": ["orders", "customers"]},
    constraints={"max_rows": 50}
)
```

### Read-Only Mode

```python
# Enable read-only mode for safety
sql_generator = SQLGenerator(enforce_read_only=True)
generator = DSLLMGenerator(provider=provider, dsl_generator=sql_generator)

# Only SELECT statements will be generated
result = await generator.generate("Get user data")  # ✅ Works
result = await generator.generate("Delete old records")  # ❌ Fails validation
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key

### Provider Options

```python
provider = OpenAIProvider(
    model="gpt-4",           # Model to use
    temperature=0.1,         # Generation temperature
    max_tokens=500          # Maximum tokens
)
```

## Roadmap

- **Additional DSLs**: GraphQL, MongoDB queries, Elasticsearch DSL
- **More LLM Providers**: Anthropic Claude, Google PaLM, Azure OpenAI
- **Advanced Features**: Agentic loops, automated testing, observability
- **Enhanced Validation**: Semantic validation, performance analysis

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Frenk Dragar** ([@frenkd](https://github.com/frenkd))