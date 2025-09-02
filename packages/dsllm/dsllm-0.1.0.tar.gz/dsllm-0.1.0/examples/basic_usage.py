"""
Basic usage examples for dsllm library.
"""

import asyncio
import os
from dsllm import DSLLMGenerator, OpenAIProvider, SQLGenerator


async def basic_sql_example():
    """Basic SQL generation example."""
    
    # Initialize provider and generator
    provider = OpenAIProvider(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4",
        temperature=0.1
    )
    
    sql_generator = SQLGenerator()
    
    # Create the main generator
    generator = DSLLMGenerator(
        provider=provider,
        dsl_generator=sql_generator
    )
    
    # Generate SQL from natural language
    result = await generator.generate(
        natural_language="Find all users who registered in the last 30 days and have made at least one purchase",
        context={
            "schema": """
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    total_amount DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        },
        constraints={
            "max_rows": 100
        }
    )
    
    print("Generated SQL:")
    print(result.dsl_statement)
    print(f"\nValidation errors: {result.validation_errors}")
    print(f"Metadata: {result.metadata}")


async def read_only_example():
    """Example with read-only SQL generation."""
    
    provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Enable read-only mode for safety
    sql_generator = SQLGenerator(enforce_read_only=True)
    
    generator = DSLLMGenerator(
        provider=provider,
        dsl_generator=sql_generator
    )
    
    # This will work - SELECT statement
    try:
        result = await generator.generate(
            "Show me the top 10 products by sales volume"
        )
        print("✅ Read-only SELECT generated successfully")
        print(result.dsl_statement)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # This will fail - trying to delete data
    try:
        result = await generator.generate(
            "Delete all inactive users from the database"
        )
        print("✅ DELETE statement generated:", result.dsl_statement)
    except Exception as e:
        print(f"❌ Expected error for DELETE in read-only mode: {e}")


async def context_injection_example():
    """Example showing context injection with DDL."""
    
    provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    sql_generator = SQLGenerator()
    generator = DSLLMGenerator(provider=provider, dsl_generator=sql_generator)
    
    # Complex schema with relationships
    schema = """
    CREATE TABLE customers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        price DECIMAL(10,2),
        category_id INTEGER,
        stock_quantity INTEGER DEFAULT 0
    );
    
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(id),
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'pending'
    );
    
    CREATE TABLE order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(id),
        product_id INTEGER REFERENCES products(id),
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10,2)
    );
    """
    
    result = await generator.generate(
        natural_language="Find customers who have spent more than $500 total and show their order history",
        context={
            "schema": schema,
            "tables": ["customers", "orders", "order_items", "products"]
        },
        constraints={
            "required_columns": ["customer_name", "total_spent", "order_count"],
            "max_rows": 50
        }
    )
    
    print("Complex query with context:")
    print(result.dsl_statement)


if __name__ == "__main__":
    # Make sure to set your OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    print("=== Basic SQL Example ===")
    asyncio.run(basic_sql_example())
    
    print("\n=== Read-Only Example ===")
    asyncio.run(read_only_example())
    
    print("\n=== Context Injection Example ===")
    asyncio.run(context_injection_example())
