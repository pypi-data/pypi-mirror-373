# LLM Wrapper - Universal Large Language Model Library

A comprehensive, modular Python library for seamless integration with multiple Large Language Model providers. Built with enterprise-grade features including token tracking, usage analytics, and robust error handling.

## 🚀 Features

- **Multi-Provider Support**: Azure OpenAI, OpenAI, Anthropic Claude, and extensible for more
- **Unified API**: Single interface for all LLM providers
- **Token Tracking**: Comprehensive token usage logging with PostgreSQL backend
- **Usage Analytics**: Detailed statistics and monitoring capabilities
- **Enterprise Ready**: Connection pooling, error handling, and production-grade logging
- **Type Safety**: Full type hints and data validation
- **Modular Architecture**: Clean separation of concerns with factory pattern
- **Backward Compatible**: Legacy API support for existing integrations

## 📦 Installation

```bash
pip install hibiz-any-llm
```

## 🏗️ Architecture

```
llm_wrapper/
├── core/           # Core functionality and factory
├── providers/      # LLM provider implementations
├── models/         # Data models and schemas
├── database/       # Database management
└──utils/          # Token Calculation and validators
```

## 🛠️ Quick Start

### 1. Basic Setup

```python
from hibiz_any_llm import LLMWrapper, LLMProvider

# Configure your provider
azure_config = {
    'service_url': 'https://your-resource.openai.azure.com',
    'api_key': 'your-api-key',
    'deployment_name': 'gpt-4',
    'api_version': '2023-12-01-preview'
}

# Database configuration
db_config = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'llm_usage',
    'user': 'username',
    'password': 'password'
}

# Initialize wrapper
wrapper = LLMWrapper(
    provider_type=LLMProvider.AZURE_OPENAI,
    provider_config=azure_config,
    db_config=db_config,
    enable_logging=True
)
```

### 2. Chat Completion

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"}
]

response = wrapper.send_request(
    prompt_payload=messages,
    customer_id="customer_123",
    organization_id="org_456",
    app_name="chatbot",
    module_name="education",
    function_name="explain_concepts",
    model="gpt-4",
    temperature=0.7,
    max_tokens=500
)

print(f"Response: {response['output_text']}")
print(f"Tokens used: {response['total_tokens']}")
```

### 3. Embeddings

```python
embedding_response = wrapper.create_embeddings(
    input_texts=["Machine learning is amazing", "AI will change the world"],
    customer_id="customer_123",
    organization_id="org_456",
    app_name="search_engine",
    module_name="vectorization",
    function_name="create_embeddings",
    model="text-embedding-3-small"
)

print(f"Embeddings: {embedding_response['embeddings']}")
```

## 🔧 Provider Configurations

### Azure OpenAI

```python
azure_config = {
    'service_url': 'https://your-resource.openai.azure.com',
    'api_key': 'your-api-key',
    'deployment_name': 'gpt-4',
    'api_version': '2023-12-01-preview',
    'timeout': 600
}

wrapper = LLMWrapper(LLMProvider.AZURE_OPENAI, azure_config, db_config)
```

### OpenAI

```python
openai_config = {
    'api_key': 'sk-your-openai-api-key',
    'organization_id': 'org-your-org-id',  # Optional
    'timeout': 600
}

wrapper = LLMWrapper(LLMProvider.OPENAI, openai_config, db_config)
```

### Anthropic Claude

```python
anthropic_config = {
    'api_key': 'sk-ant-your-anthropic-api-key',
    'default_model': 'claude-opus-4-20250514',
    'timeout': 300
}

wrapper = LLMWrapper(LLMProvider.ANTHROPIC, anthropic_config, db_config)
```
### Google Gemini

```python
google_config = {
    'api_key': 'your-gemini-api-key',
    'default_model': 'gemini-2.0-flash',
    'timeout': 300
}

wrapper = LLMWrapper(LLMProvider.GOOGLE, google_config, db_config)
```
### Twitter GROK

```python
grok_config = {
    'api_key': 'your-grok-api-key',
    'default_model': 'grok-4',
    'timeout': 300
}

wrapper = LLMWrapper(LLMProvider.GROK, grok_config, db_config)
```
### Alibaba QWEN

```python
qwen_config = {
    'api_key': 'your-qwen-api-key',
    'default_model': 'qwen-plus',
    'timeout': 300
}

wrapper = LLMWrapper(LLMProvider.QWEN, qwen_config, db_config)
```
### DeepSeek

```python
deepseek_config = {
    'api_key': 'your-deepseek-api-key',
    'default_model': 'deepseek-chat',
    'timeout': 300
}

wrapper = LLMWrapper(LLMProvider.DEEP_SEEK, deepseek_config, db_config)
```

## 📊 Usage Analytics

### Get Usage Statistics

```python
stats = wrapper.get_usage_stats(
    customer_id="customer_123",
    start_date="2024-01-01T00:00:00",
    end_date="2024-12-31T23:59:59",
    app_name="chatbot"
)

print(f"Total requests: {stats['summary']['total_requests']}")
print(f"Total tokens: {stats['summary']['total_tokens']}")
print(f"Success rate: {stats['summary']['success_rate']}")
```

### Filter by Different Dimensions

```python
# By application
app_stats = wrapper.get_usage_stats(app_name="chatbot")

# By model
model_stats = wrapper.get_usage_stats(filters={"model_name": "gpt-4"})

# By request type
embedding_stats = wrapper.get_usage_stats(request_type="embedding")
```

## 🎯 Advanced Features

### JSON Response Format

```python
response = wrapper.send_request(
    prompt_payload=[
        {"role": "user", "content": "List 3 benefits of exercise in JSON format"}
    ],
    customer_id="customer_789",
    organization_id="org_456",
    app_name="health_app",
    module_name="exercise",
    function_name="get_benefits",
    response_type="json"  # Automatically ensures JSON output
)

# Access parsed JSON
json_data = response['processed_output']
```

### Context Manager Support

```python
with LLMWrapper(LLMProvider.AZURE_OPENAI, azure_config, db_config) as wrapper:
    response = wrapper.send_request(
        prompt_payload=messages,
        customer_id="customer_123",
        organization_id="org_456",
        app_name="temp_app",
        module_name="test",
        function_name="context_test"
    )
    # Automatic cleanup on exit
```

### Multi-Provider Switching

```python
providers = {
    LLMProvider.AZURE_OPENAI: azure_config,
    LLMProvider.OPENAI: openai_config,
    LLMProvider.ANTHROPIC: anthropic_config
}

for provider_type, config in providers.items():
    wrapper = LLMWrapper(provider_type, config, db_config)
    response = wrapper.send_request(
        prompt_payload=[{"role": "user", "content": "Hello!"}],
        customer_id="multi_test",
        organization_id="org_test",
        app_name="provider_comparison",
        module_name="testing",
        function_name="hello_test"
    )
    print(f"{provider_type.value}: {response['output_text']}")
    wrapper.close()
```

## 🗄️ Database Schema

The library automatically creates the following PostgreSQL table:

```sql
CREATE TABLE token_usage_log (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    organization_id VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    app_name VARCHAR(255),
    module_name VARCHAR(255),
    function_name VARCHAR(255),
    request_type VARCHAR(50) NOT NULL,
    request_params JSONB,
    response_params JSONB,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    request_timestamp TIMESTAMP DEFAULT NOW(),
    response_time_ms INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'success',
    request_id VARCHAR(255),
    cost FLOAT
);
```

### Indexes for Performance

- `idx_customer_date` on (customer_id, request_timestamp)
- `idx_org_model` on (organization_id, model_name)
- `idx_app_module` on (app_name, module_name)

## 🧪 Error Handling

```python
from llm_wrapper import APIError, DatabaseError, ConfigurationError

try:
    response = wrapper.send_request(...)
except APIError as e:
    print(f"API Error: {e}")
except DatabaseError as e:
    print(f"Database Error: {e}")
except ConfigurationError as e:
    print(f"Configuration Error: {e}")
```

## 🔒 Security Best Practices

1. **Environment Variables**: Store API keys in environment variables
```python
import os

config = {
    'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
    'service_url': os.getenv('AZURE_OPENAI_SERVICE_URL'),
    # ...
}
```

2. **Database Security**: Use connection pooling and proper credentials
```python
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'pool_size': 10,
    'max_overflow': 20
}
```

## 📈 Performance Optimization

### Connection Pooling

The library uses SQLAlchemy's connection pooling:

```python
db_config = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'llm_usage',
    'user': 'username',
    'password': 'password',
    'pool_size': 10,        # Number of persistent connections
    'max_overflow': 20,     # Additional connections when needed
    'pool_pre_ping': True   # Validate connections before use
}
```

### Batch Processing

For multiple requests, use connection reuse:

```python
with LLMWrapper(provider_type, config, db_config) as wrapper:
    for request_data in batch_requests:
        response = wrapper.send_request(**request_data)
        # Process response
```

## 📝 Logging

Configure logging for production:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_wrapper.log'),
        logging.StreamHandler()
    ]
)
```

## 🔄 Migration from Legacy Version

### Old API (v0.1.x)

```python
# Old way
wrapper = LLMWrapper(service_url, api_key, deployment_name, api_version, db_config)
response = wrapper.send_request(messages, customer_id, ...)
```

### New API (v0.2.x)

```python
# New way
wrapper = LLMWrapper(LLMProvider.AZURE_OPENAI, provider_config, db_config)
response = wrapper.send_request(messages, customer_id, ...)
```

The response format remains the same for backward compatibility.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-provider`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Submit a pull request

### Adding New Providers

1. Create a new provider class inheriting from `BaseLLMProvider`
2. Implement required methods: `send_chat_completion`, `create_embeddings`, `validate_config`
3. Add the provider to `LLMProviderFactory`
4. Add provider-specific configuration in constants
5. Write tests


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Email**: akilan@hibizsolutions.com

## 🏷️ Changelog

### v0.2.0 (Latest)
- ✅ Multi-provider support (Azure OpenAI, OpenAI, Anthropic)
- ✅ Modular architecture with factory pattern
- ✅ Enhanced token tracking and analytics
- ✅ Improved error handling and validation
- ✅ Type safety with full type hints
- ✅ Performance optimizations
- ✅ Backward compatibility

### v0.1.0
- ✅ Basic Azure OpenAI support
- ✅ Token tracking
- ✅ PostgreSQL logging

## 🎯 Roadmap

- [ ] Google PaLM/Gemini support
- [ ] Cost calculation and tracking
- [ ] Rate limiting and retry mechanisms
- [ ] Async support
- [ ] Streaming responses
- [ ] Fine-tuning integration
- [ ] Monitoring dashboard

---

**Made with ❤️ by [Hibiz Solutions](https://hibizsolutions.com)**