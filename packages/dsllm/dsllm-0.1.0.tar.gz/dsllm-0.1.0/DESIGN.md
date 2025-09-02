# dsllm Design Document

## Vision

`dsllm` aims to be the definitive library for converting natural language into Domain Specific Language (DSL) statements using Large Language Models. The library prioritizes extensibility, safety, and reliability while maintaining a simple, intuitive API.

## Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  DSLLMGenerator  │───▶│  Generated DSL  │
│ (Natural Lang)  │    │   (Orchestrator) │    │   (Validated)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
            ┌─────────────┐ ┌─────────┐ ┌──────────────┐
            │ LLM Provider│ │DSL Gen. │ │ Validation   │
            │  (OpenAI)   │ │ (SQL)   │ │   System     │
            └─────────────┘ └─────────┘ └──────────────┘
```

### Core Components

1. **DSLLMGenerator** (Orchestrator)
   - Coordinates the entire generation pipeline
   - Manages retries and error handling
   - Enforces validation policies

2. **LLM Providers** (Pluggable)
   - Abstract interface for different LLM services
   - Currently: OpenAI (GPT-3.5/4)
   - Planned: Anthropic, Google, Azure, Local models

3. **DSL Generators** (Extensible)
   - Domain-specific logic for each DSL type
   - Currently: SQL with multiple dialects
   - Planned: GraphQL, MongoDB, Elasticsearch, YAML

4. **Validation System**
   - Pre-flight: Input validation
   - Syntax: DSL syntax checking
   - Post-flight: Semantic validation
   - Safety: Dangerous operation detection

5. **Context Injection**
   - Schema information (DDL)
   - Sample data
   - Constraints and requirements

## Design Principles

### 1. Extensibility First
- Plugin architecture for providers and generators
- Abstract base classes define clear contracts
- Minimal coupling between components

### 2. Safety by Default
- Validation at multiple stages
- Read-only modes for sensitive operations
- Dangerous keyword detection
- Configurable safety policies

### 3. Reliability
- Automatic retry with exponential backoff
- Comprehensive error handling
- Graceful degradation

### 4. Developer Experience
- Simple, intuitive API
- Rich error messages
- Comprehensive documentation
- Type safety with Pydantic

## Component Details

### DSLLMGenerator (Core Orchestrator)

**Responsibilities:**
- Coordinate generation pipeline
- Manage validation lifecycle
- Handle retries and failures
- Provide unified API

**Key Methods:**
```python
async def generate(
    natural_language: str,
    context: Optional[Dict[str, Any]] = None,
    constraints: Optional[Dict[str, Any]] = None,
    max_retries: int = 3
) -> GenerationResult
```

**Pipeline Flow:**
1. Pre-flight validation
2. Prompt formatting
3. LLM generation
4. Response cleaning
5. Syntax validation
6. Post-flight validation
7. Result packaging

### LLM Provider Interface

**Abstract Contract:**
```python
class LLMProvider(Protocol):
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str
```

**Implementation Requirements:**
- Async/await support
- Error handling and retries
- Rate limiting compliance
- Token management

**Current Implementation: OpenAI**
- GPT-3.5/4 support
- Configurable temperature/tokens
- Built-in error handling

### DSL Generator Interface

**Abstract Contract:**
```python
class DSLGenerator(ABC):
    def get_system_prompt(self) -> str
    def format_user_prompt(self, request: GenerationRequest) -> str
    def validate_syntax(self, dsl_statement: str) -> ValidationResult
    def pre_flight_check(self, request: GenerationRequest) -> ValidationResult
    def post_flight_check(self, request: GenerationRequest, result: str) -> ValidationResult
```

**SQL Generator Implementation:**
- Multi-dialect support (PostgreSQL, MySQL, SQLite)
- Syntax validation with regex patterns
- Read-only mode enforcement
- Context-aware prompt generation

### Validation System

**Three-Stage Validation:**

1. **Pre-flight** (Input Validation)
   - Natural language quality checks
   - Context validation
   - Safety policy enforcement

2. **Syntax** (DSL Structure)
   - Grammar and syntax checking
   - Basic semantic validation
   - Security pattern detection

3. **Post-flight** (Semantic Validation)
   - Context consistency checks
   - Performance considerations
   - Business rule validation

### Context Injection System

**Context Types:**
- **Schema Context**: DDL definitions, table structures
- **Data Context**: Sample data, value ranges
- **Constraint Context**: Requirements, limitations
- **Business Context**: Domain-specific rules

**Implementation:**
```python
context = {
    "schema": "CREATE TABLE users (...)",
    "tables": ["users", "orders", "products"],
    "sample_data": "...",
    "constraints": {"max_rows": 100}
}
```

## Error Handling Strategy

### Exception Hierarchy
```
DSLLMError (Base)
├── GenerationError (LLM failures)
├── ValidationError (Validation failures)
├── ProviderError (Provider-specific errors)
└── RetryExhaustedError (All retries failed)
```

### Retry Strategy
- Exponential backoff with jitter
- Configurable max attempts
- Different strategies per error type
- Comprehensive logging

## Extensibility Points

### Adding New LLM Providers

1. Implement `LLMProvider` protocol
2. Handle provider-specific authentication
3. Implement error mapping
4. Add to provider registry

Example:
```python
class AnthropicProvider:
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        # Implementation
        pass
```

### Adding New DSL Generators

1. Inherit from `DSLGenerator` ABC
2. Implement required methods
3. Define validation rules
4. Create prompt templates

Example:
```python
class GraphQLGenerator(DSLGenerator):
    def get_system_prompt(self) -> str:
        return "Generate GraphQL queries..."
    
    # ... other methods
```

## Future Architecture Considerations

### Agentic Loops (Planned)
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Generation  │───▶│ Execution    │───▶│ Validation  │
│   Attempt   │    │   (Optional) │    │   Results   │
└─────────────┘    └──────────────┘    └─────────────┘
       ▲                                       │
       │            ┌──────────────┐          │
       └────────────│ Error        │◀─────────┘
                    │ Analysis     │
                    └──────────────┘
```

### Observability Integration
- Structured logging with correlation IDs
- Metrics collection (generation time, success rate)
- Tracing for complex pipelines
- Integration with monitoring systems

### Caching Strategy
- Response caching by input hash
- Context-aware cache invalidation
- Configurable TTL policies
- Cache warming strategies

## Performance Considerations

### Optimization Strategies
1. **Prompt Optimization**: Minimize token usage
2. **Batch Processing**: Multiple generations in parallel
3. **Caching**: Avoid redundant LLM calls
4. **Streaming**: Real-time response processing

### Scalability
- Async/await throughout
- Connection pooling
- Rate limiting compliance
- Resource management

## Security Considerations

### Input Validation
- SQL injection prevention
- Dangerous keyword detection
- Input sanitization
- Size limits

### Output Validation
- Syntax verification
- Semantic checks
- Security pattern detection
- Business rule enforcement

### Access Control
- Provider authentication
- Usage tracking
- Rate limiting
- Audit logging

## Testing Strategy

### Unit Testing
- Component isolation
- Mock LLM responses
- Validation logic testing
- Error condition coverage

### Integration Testing
- End-to-end pipeline testing
- Provider integration
- Real LLM interaction (limited)
- Performance benchmarks

### Validation Testing
- DSL correctness verification
- Security vulnerability testing
- Edge case handling
- Regression prevention

## Documentation Strategy

### API Documentation
- Comprehensive docstrings
- Type annotations
- Usage examples
- Error scenarios

### User Guides
- Getting started tutorial
- Advanced usage patterns
- Best practices
- Troubleshooting

### Developer Documentation
- Architecture overview
- Extension guides
- Contributing guidelines
- Design decisions

## Roadmap Priorities

### Phase 1 (Current - v0.1.0)
- ✅ Core architecture
- ✅ OpenAI provider
- ✅ SQL generator
- ✅ Basic validation
- ✅ Documentation

### Phase 2 (v0.2.0)
- Additional LLM providers (Anthropic, Google)
- GraphQL generator
- Enhanced validation
- Performance optimizations

### Phase 3 (v0.3.0)
- Agentic loops
- Automated testing
- Observability integration
- Advanced caching

### Phase 4 (v1.0.0)
- Production readiness
- Comprehensive DSL support
- Enterprise features
- Ecosystem integrations

## Success Metrics

### Developer Experience
- Time to first successful generation
- API usability scores
- Documentation completeness
- Community adoption

### Technical Performance
- Generation accuracy
- Response time
- Success rate
- Error recovery

### Safety and Reliability
- Validation effectiveness
- Security vulnerability detection
- Uptime and availability
- Error handling coverage
