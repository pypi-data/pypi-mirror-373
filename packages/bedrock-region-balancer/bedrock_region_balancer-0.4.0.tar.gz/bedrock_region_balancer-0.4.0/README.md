# Bedrock Region Balancer

AWS Bedrock region load balancer with round-robin distribution across multiple regions.

## Features

- **Dual API Support**: Both traditional invoke_model and modern Converse API
- **NEW: Batch Processing**: Process multiple messages simultaneously with round-robin distribution
- **Round-robin load balancing** across AWS regions (default: us-west-2, eu-central-1, ap-northeast-2)
- **Async execution** for optimal performance
- **Automatic model availability checking** across regions
- **AWS Secrets Manager integration** for secure credential management
- **Intelligent caching** of model availability data
- **Error handling and automatic failover**
- **Support for Claude 3.7 Sonnet and Opus 4.x models** 
- **Short model name support** (e.g., `claude-3.7-sonnet` → full model ID)
- **Multimodal content support** via Converse API (text, images, documents, video)
- **Tool use and function calling** with native Converse API integration
- **Guardrail support** for content filtering and safety
- **Environment variable configuration** for custom regions

## Installation

```bash
pip install bedrock-region-balancer
```

## Quick Start

### Authentication Methods

Bedrock Region Balancer supports 3 authentication methods:

1. **AWS Session Credentials** (access_key_id, secret_access_key, session_token)
2. **AWS Access Keys** (access_key_id, secret_access_key)  
3. **Bedrock API Key** (aws_bearer_token_bedrock)

### Method 1: Using Bedrock API Key

```python
import asyncio
import json
from bedrock_region_balancer import BedrockRegionBalancer

async def main():
    # Method 1a: Direct parameter
    async with BedrockRegionBalancer(
        credentials={'bedrock_api_key': 'your-bedrock-api-key'},
        default_model="claude-3.7-sonnet"
    ) as balancer:
        
        model_id = balancer.get_default_model()
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": "Hello!"}],
            "max_tokens": 100
        }
        
        # Using invoke_model API (Single Request)
        response = await balancer.invoke_model(model_id, body)
        print(f"invoke_model response from {response['region']}: {response['response']['content'][0]['text']}")
        
        # Using invoke_model API (Batch Processing) - NEW!
        batch_bodies = [
            {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": "What is 2+2?"}],
                "max_tokens": 50
            },
            {
                "anthropic_version": "bedrock-2023-05-31", 
                "messages": [{"role": "user", "content": "What is the capital of France?"}],
                "max_tokens": 50
            }
        ]
        batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies)
        for i, response in enumerate(batch_responses, 1):
            print(f"Batch {i} from {response['region']}: {response['response']['content'][0]['text']}")
        
        # Using converse API (modern approach - Single Request)
        from bedrock_region_balancer import ConverseAPIHelper, MessageRole
        messages = [ConverseAPIHelper.create_message(MessageRole.USER, "Hello!")]
        converse_response = await balancer.converse_model(
            model_id=model_id,
            messages=messages,
            inference_config={"maxTokens": 100}
        )
        parsed = ConverseAPIHelper.parse_converse_response(converse_response['response'])
        print(f"converse response from {converse_response['region']}: {parsed['content'][0]['text']}")
        
        # Using converse API (Batch Processing) - NEW!
        batch_message_lists = [
            [ConverseAPIHelper.create_message(MessageRole.USER, "What is 2+2?")],
            [ConverseAPIHelper.create_message(MessageRole.USER, "What is the capital of France?")]
        ]
        batch_converse_responses = await balancer.converse_model_batch(
            model_id=model_id,
            message_lists=batch_message_lists,
            inference_config={"maxTokens": 50}
        )
        for i, response in enumerate(batch_converse_responses, 1):
            parsed = ConverseAPIHelper.parse_converse_response(response['response'])
            print(f"Converse Batch {i} from {response['region']}: {parsed['content'][0]['text']}")

    # Method 1b: Environment variable (preferred)
    # Set: export AWS_BEARER_TOKEN_BEDROCK="your-api-key"
    async with BedrockRegionBalancer() as balancer:  # Auto-detects from environment
        # Use balancer as above
        pass

    # Method 1c: Using .env file (most convenient)
    # Create .env file with: AWS_BEARER_TOKEN_BEDROCK=your-api-key
    async with BedrockRegionBalancer(use_dotenv=True) as balancer:  # Auto-loads .env
        # Use balancer as above
        pass

    # Method 1d: Custom .env file path
    async with BedrockRegionBalancer(
        dotenv_path='/path/to/your/.env',
        use_dotenv=True
    ) as balancer:
        # Use balancer as above
        pass

asyncio.run(main())
```

### Method 2: Using AWS Session Credentials

```python
import asyncio
from bedrock_region_balancer import BedrockRegionBalancer

async def main():
    # Method 2a: Direct credentials
    credentials = {
        'aws_access_key_id': 'your-access-key-id',
        'aws_secret_access_key': 'your-secret-access-key',
        'aws_session_token': 'your-session-token'
    }
    
    async with BedrockRegionBalancer(
        credentials=credentials,
        default_model="claude-3.7-sonnet"
    ) as balancer:
        model_id = balancer.get_default_model()
        # Use balancer as shown above

    # Method 2b: Environment variables
    # Set: export AWS_ACCESS_KEY_ID="..." AWS_SECRET_ACCESS_KEY="..." AWS_SESSION_TOKEN="..."
    async with BedrockRegionBalancer() as balancer:  # Auto-detects from environment
        # Use balancer as above
        pass

asyncio.run(main())
```

### Method 3: Using AWS Access Keys

```python
import asyncio
from bedrock_region_balancer import BedrockRegionBalancer

async def main():
    # Method 3a: Direct credentials  
    credentials = {
        'aws_access_key_id': 'your-access-key-id',
        'aws_secret_access_key': 'your-secret-access-key'
    }
    
    async with BedrockRegionBalancer(
        credentials=credentials,
        default_model="claude-3.7-sonnet"
    ) as balancer:
        model_id = balancer.get_default_model()
        # Use balancer as shown above

asyncio.run(main())
```

### Method 4: Using AWS Secrets Manager

AWS Secrets Manager now supports multiple credential formats:

#### 4a. Bedrock API Key in Secrets Manager
```json
{
  "bedrock_api_key": "your-bedrock-api-key"
}
```
or
```json
{
  "aws_bearer_token_bedrock": "your-bedrock-api-key"
}
```

#### 4b. AWS Access Keys in Secrets Manager
```json
{
  "access_key_id": "AKIA...",
  "secret_access_key": "your-secret-key"
}
```
or
```json
{
  "aws_access_key_id": "AKIA...",
  "aws_secret_access_key": "your-secret-key"
}
```

#### 4c. AWS Session Credentials in Secrets Manager
```json
{
  "access_key_id": "ASIA...",
  "secret_access_key": "your-secret-key",
  "session_token": "your-session-token"
}
```

```python
import asyncio
import json
from bedrock_region_balancer import BedrockRegionBalancer

async def main():
    # Initialize balancer with credentials from Secrets Manager
    # Supports all credential formats above
    async with BedrockRegionBalancer(
        secret_name="bedrock-credentials",  # Your secret name
        secret_region="us-west-2",
        default_model="claude-3.7-sonnet"
    ) as balancer:
        
        model_id = balancer.get_default_model()
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": "What is the capital of France?"}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = await balancer.invoke_model(model_id, json.dumps(body))
        
        print(f"Response from region: {response['region']}")
        response_body = json.loads(response['response'])
        print(f"Model response: {response_body['content'][0]['text']}")

asyncio.run(main())
```

### Method 5: Using Default AWS Credentials

```python
import asyncio
from bedrock_region_balancer import BedrockRegionBalancer

async def main():
    # Initialize with default AWS credential chain
    # (IAM role, instance profile, etc.)
    async with BedrockRegionBalancer(
        default_model="claude-3.7-sonnet"  # Optional: set default model
    ) as balancer:
        model_id = balancer.get_default_model()
        # Use balancer as shown above

asyncio.run(main())
```

## .env File Configuration

For convenience and security, you can use .env files to store your credentials:

### Step 1: Install python-dotenv (included as dependency)
```bash
pip install bedrock-region-balancer  # python-dotenv is included
```

### Step 2: Create .env file
Copy the provided `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Example `.env` file content:
```bash
# Choose ONE authentication method

# Option 1: Bedrock API Key (Recommended)
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key

# Option 2: AWS Session Credentials
# AWS_ACCESS_KEY_ID=ASIA...
# AWS_SECRET_ACCESS_KEY=your-secret-key
# AWS_SESSION_TOKEN=your-session-token

# Option 3: AWS Access Keys
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=your-secret-key

# Optional: Configuration
BEDROCK_REGIONS=us-west-2,eu-central-1,ap-northeast-2
DEFAULT_MODEL=claude-3.7-sonnet
```

### Step 3: Use in your code
```python
import asyncio
from bedrock_region_balancer import BedrockRegionBalancer

async def main():
    # Automatically loads .env file from current directory
    async with BedrockRegionBalancer() as balancer:
        model_id = balancer.get_default_model()
        
        body = {
            "anthropic_version": "bedrock-2023-05-31", 
            "messages": [{"role": "user", "content": "Hello!"}],
            "max_tokens": 100
        }
        
        response = await balancer.invoke_model(model_id, body)
        print(f"Response from {response['region']}")

asyncio.run(main())
```

### Custom .env file location
```python
async with BedrockRegionBalancer(
    dotenv_path="/path/to/your/.env",
    use_dotenv=True
) as balancer:
    # Your code here
    pass
```

### Security Best Practices for .env files
- **Never commit .env files** to version control
- Add `.env` to your `.gitignore` file
- Use different .env files for development, staging, and production
- Set appropriate file permissions: `chmod 600 .env`

## Advanced Usage

### Custom Regions

```python
# Method 1: Use custom regions via parameter
balancer = BedrockRegionBalancer(
    regions=['us-east-1', 'us-west-2', 'eu-west-1'],
    default_model="claude-3.7-sonnet"  # Optional: set custom default model
)

# Method 2: Use environment variable
import os
os.environ['BEDROCK_REGIONS'] = 'us-west-2,eu-central-1,ap-northeast-2'
balancer = BedrockRegionBalancer(
    default_model="claude-3.7-sonnet"  # Optional: set default model
)  # Will use regions from environment
```

### Custom Endpoints

The balancer now supports custom endpoint configuration for each region. By default, it uses official AWS Bedrock endpoints, but you can specify custom endpoints for testing or specific requirements:

```python
from bedrock_region_balancer import BedrockRegionBalancer

# Method 1: Use default endpoints (automatic)
# Default endpoints are automatically used for us-west-2, eu-central-1, ap-northeast-2
balancer = BedrockRegionBalancer()  # Uses official AWS endpoints

# Method 2: Use custom endpoints (must match number of regions)
custom_regions = ['us-west-2', 'eu-central-1', 'ap-northeast-2']
custom_endpoints = [
    'https://custom-bedrock.us-west-2.example.com',
    'https://custom-bedrock.eu-central-1.example.com',
    'https://custom-bedrock.ap-northeast-2.example.com'
]

balancer = BedrockRegionBalancer(
    regions=custom_regions,
    endpoints=custom_endpoints,
    default_model="claude-3.7-sonnet"
)

# Method 3: Mixed configuration with custom regions and endpoints
mixed_regions = ['us-east-1', 'eu-west-1']
mixed_endpoints = [
    'https://bedrock.us-east-1.amazonaws.com',
    'https://bedrock.eu-west-1.amazonaws.com'
]

balancer = BedrockRegionBalancer(
    regions=mixed_regions,
    endpoints=mixed_endpoints
)
```

#### Default Endpoints

The following official AWS Bedrock endpoints are used by default:

| Region | Bedrock Control Plane | Bedrock Runtime |
|--------|----------------------|-----------------|
| **us-west-2** | `https://bedrock.us-west-2.amazonaws.com` | `https://bedrock-runtime.us-west-2.amazonaws.com` |
| **eu-central-1** | `https://bedrock.eu-central-1.amazonaws.com` | `https://bedrock-runtime.eu-central-1.amazonaws.com` |
| **ap-northeast-2** | `https://bedrock.ap-northeast-2.amazonaws.com` | `https://bedrock-runtime.ap-northeast-2.amazonaws.com` |

#### Important Notes

- **Endpoint Count**: Number of custom endpoints must exactly match the number of regions
- **Service Separation**: The balancer automatically handles separate endpoints for Bedrock control plane and runtime services
- **HTTPS Required**: All endpoints must use HTTPS protocol
- **Validation**: Connection is tested during initialization to ensure endpoint accessibility

### Invoke Model in All Regions

```python
# Get responses from all available regions simultaneously
responses = await balancer.invoke_model_all_regions(model_id, body)

for response in responses:
    if 'error' in response:
        print(f"Error in region {response['region']}: {response['error']}")
    else:
        print(f"Success in region {response['region']}")
```

### Check Model Availability

```python
# Get model availability report
report = balancer.get_model_availability_report()
print(f"Available regions: {report['available_regions']}")
print(f"Models by region: {report['models_by_region']}")
print(f"Default model: {report['default_model']}")

# Get just the default model
default_model = balancer.get_default_model()
print(f"Using default model: {default_model}")
```

### Disable Availability Checking

```python
# Skip availability check for faster execution
# (useful when you know the model is available)
response = await balancer.invoke_model(
    model_id, 
    body, 
    check_availability=False
)
```

## Batch Processing vs Sequential Processing (NEW)

Bedrock Region Balancer now supports batch processing for both APIs, allowing you to send multiple messages simultaneously with round-robin distribution across regions for improved performance and load balancing.

### Processing Methods Comparison

| Aspect | Sequential Processing | Batch Processing |
|--------|----------------------|------------------|
| **Execution Model** | One request at a time | Multiple requests in parallel |
| **Performance** | Slower (cumulative latency) | **2-10x faster** (parallel execution) |
| **Load Distribution** | Single region per request | **Round-robin across regions** |
| **Resource Usage** | Low memory, high latency | Higher memory, low latency |
| **Error Handling** | Fail-fast, simple | Partial failures, more complex |
| **Use Case** | Simple, low-volume requests | **High-throughput, performance-critical** |

### Batch Processing Benefits

- **Performance**: **2-10x faster** execution time through parallel processing
- **Load Distribution**: Automatic round-robin distribution across available regions
- **Resource Efficiency**: Better utilization of concurrent connections and network bandwidth
- **Simplified Code**: Handle multiple requests with a single API call
- **Scalability**: Better handling of high-volume scenarios

### Basic Batch Usage

```python
from bedrock_region_balancer import BedrockRegionBalancer

async def batch_example():
    async with BedrockRegionBalancer() as balancer:
        model_id = "claude-3.7-sonnet"
        
        # Prepare multiple request bodies
        batch_bodies = [
            {
                "messages": [{"role": "user", "content": "What is 2+2?"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            },
            {
                "messages": [{"role": "user", "content": "What is the capital of France?"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
        ]
        
        # Process all requests in parallel with round-robin distribution
        batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies)
        
        for i, response in enumerate(batch_responses, 1):
            print(f"Response {i} from {response['region']}: {response['response']['content'][0]['text']}")

# Converse API batch processing
async def converse_batch_example():
    async with BedrockRegionBalancer() as balancer:
        from bedrock_region_balancer import ConverseAPIHelper, MessageRole
        
        # Prepare multiple message lists
        batch_message_lists = [
            [ConverseAPIHelper.create_message(MessageRole.USER, "What is 2+2?")],
            [ConverseAPIHelper.create_message(MessageRole.USER, "What is the capital of France?")]
        ]
        
        # Process all conversations in parallel
        batch_responses = await balancer.converse_model_batch(
            model_id="claude-3.7-sonnet",
            message_lists=batch_message_lists,
            inference_config={"maxTokens": 50}
        )
        
        for i, response in enumerate(batch_responses, 1):
            parsed = ConverseAPIHelper.parse_converse_response(response['response'])
            print(f"Conversation {i} from {response['region']}: {parsed['content'][0]['text']}")
```

### Sequential vs Batch Performance Comparison Example

```python
import time
from bedrock_region_balancer import BedrockRegionBalancer

async def performance_comparison():
    async with BedrockRegionBalancer() as balancer:
        model_id = "claude-3.7-sonnet"
        
        # Prepare 5 requests
        requests = [
            {
                "messages": [{"role": "user", "content": f"What is {i+1} + {i+1}?"}],
                "max_tokens": 30,
                "anthropic_version": "bedrock-2023-05-31"
            }
            for i in range(5)
        ]
        
        # Sequential processing (traditional approach)
        print("Sequential Processing:")
        start_time = time.time()
        sequential_responses = []
        for i, body in enumerate(requests):
            response = await balancer.invoke_model(model_id, body)
            sequential_responses.append(response)
            print(f"  Request {i+1}: {response['region']}")
        sequential_time = time.time() - start_time
        
        # Batch processing (new approach)
        print("\nBatch Processing:")
        start_time = time.time()
        batch_responses = await balancer.invoke_model_batch(model_id, requests)
        batch_time = time.time() - start_time
        
        for i, response in enumerate(batch_responses, 1):
            print(f"  Request {i}: {response['region']}")
        
        # Performance comparison
        speedup = sequential_time / batch_time if batch_time > 0 else 0
        print(f"\nPerformance Results:")
        print(f"  Sequential: {sequential_time:.2f}s")
        print(f"  Batch:      {batch_time:.2f}s")
        print(f"  Speedup:    {speedup:.1f}x faster with batch processing")

# Run comparison
asyncio.run(performance_comparison())
```

### When to Use Each Method

**Use Sequential Processing when:**
- Processing single requests or very few requests
- Memory constraints are critical
- Simple error handling is preferred
- Interactive applications requiring immediate feedback

**Use Batch Processing when:**
- Processing multiple similar requests
- Performance and throughput are critical
- You want automatic load distribution across regions
- Handling high-volume scenarios

## Converse API Support

Bedrock Region Balancer supports both the traditional **invoke_model** API and the new **Converse API**. The Converse API provides a unified interface across different foundation models with enhanced features like multimodal content, tool use, and guardrail integration.

### Basic Converse API Usage

```python
from bedrock_region_balancer import BedrockRegionBalancer, ConverseAPIHelper, MessageRole

async def converse_example():
    async with BedrockRegionBalancer() as balancer:
        # Create messages using ConverseAPIHelper
        messages = [
            ConverseAPIHelper.create_message(
                MessageRole.USER, 
                "Hello! Explain the benefits of the Converse API."
            )
        ]
        
        # Create inference configuration
        inference_config = ConverseAPIHelper.create_inference_config(
            max_tokens=200,
            temperature=0.7,
            top_p=0.9
        )
        
        # Use Converse API
        response = await balancer.converse_model(
            model_id="claude-3.7-sonnet",
            messages=messages,
            inference_config=inference_config
        )
        
        # Parse response
        parsed = ConverseAPIHelper.parse_converse_response(response['response'])
        print(f"Response: {parsed['content'][0]['text']}")
```

### Multimodal Content Support

```python
# Create multimodal message with text and images
content_blocks = [
    ConverseAPIHelper.create_text_content("Analyze this image:"),
    ConverseAPIHelper.create_image_content(
        source={"bytes": image_bytes}, 
        format="png"
    )
]

messages = [
    ConverseAPIHelper.create_message(MessageRole.USER, content_blocks)
]

response = await balancer.converse_model(
    model_id="claude-3.7-sonnet",
    messages=messages
)
```

### Tool Use and Function Calling

```python
# Define tools for the model to use
tools = [
    {
        "toolSpec": {
            "name": "get_weather",
            "description": "Get weather information for a city",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                    },
                    "required": ["city"]
                }
            }
        }
    }
]

# Create tool configuration
tool_config = ConverseAPIHelper.create_tool_config(
    tools=tools,
    tool_choice="auto"  # Let model decide when to use tools
)

response = await balancer.converse_model(
    model_id="claude-3.7-sonnet",
    messages=messages,
    tool_config=tool_config
)
```

### Converse API in All Regions

```python
# Use Converse API across all regions
responses = await balancer.converse_model_all_regions(
    model_id="claude-3.7-sonnet",
    messages=messages,
    inference_config={"maxTokens": 100, "temperature": 0.5}
)

for response in responses:
    if 'error' in response:
        print(f"Error in region {response['region']}: {response['error']}")
    else:
        parsed = ConverseAPIHelper.parse_converse_response(response['response'])
        print(f"Region {response['region']}: {parsed['content'][0]['text']}")
```

### Format Conversion

Convert between invoke_model and Converse API formats:

```python
# Original invoke_model format
invoke_body = {
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100,
    "temperature": 0.7,
    "system": "You are a helpful assistant."
}

# Convert to Converse format
converse_format = ConverseAPIHelper.convert_invoke_model_to_converse(invoke_body)

# Use with Converse API
response = await balancer.converse_model(
    model_id="claude-3.7-sonnet",
    messages=converse_format['messages'],
    inference_config=converse_format.get('inferenceConfig'),
    system=converse_format.get('system')
)
```

### API Comparison

| Feature | invoke_model | Converse API |
|---------|-------------|--------------|
| **Interface** | Model-specific formats | Unified across all models |
| **Batch Processing** | ✅ `invoke_model_batch()` | ✅ `converse_model_batch()` |
| **Multimodal** | Limited support | Native support (text, images, documents, video) |
| **Tool Use** | Model-dependent | Built-in function calling |
| **Guardrails** | External integration | Native integration |
| **Response Format** | Model-specific | Standardized structure |
| **Parameter Validation** | Basic | Enhanced validation |
| **Round-Robin Distribution** | ✅ Automatic in batch mode | ✅ Automatic in batch mode |

Both APIs are fully supported with batch processing capabilities for improved performance and load distribution.

## AWS Secrets Manager Configuration

The balancer supports multiple secret formats in AWS Secrets Manager:

### Format 1: Bedrock API Key (Recommended)
```json
{
    "bedrock_api_key": "your-bedrock-api-key"
}
```
or
```json
{
    "aws_bearer_token_bedrock": "your-bedrock-api-key"
}
```

### Format 2: AWS Access Keys
```json
{
    "access_key_id": "AKIA...",
    "secret_access_key": "your-secret-access-key"
}
```
or using full AWS naming:
```json
{
    "aws_access_key_id": "AKIA...",
    "aws_secret_access_key": "your-secret-access-key"
}
```

### Format 3: AWS Session Credentials
```json
{
    "access_key_id": "ASIA...",
    "secret_access_key": "your-secret-access-key",
    "session_token": "your-session-token"
}
```

The credential format is automatically detected when the secret is retrieved.

## Configuration Options

### Constructor Parameters

- **credentials**: Direct credentials dictionary (optional)
  - Bedrock API Key: `{'bedrock_api_key': 'key'}` or `{'aws_bearer_token_bedrock': 'key'}`
  - AWS Access Keys: `{'aws_access_key_id': 'id', 'aws_secret_access_key': 'key'}`  
  - AWS Session: `{'aws_access_key_id': 'id', 'aws_secret_access_key': 'key', 'aws_session_token': 'token'}`
- **secret_name**: Name of secret in AWS Secrets Manager (optional, cannot use with credentials)
- **secret_region**: AWS region where secret is stored (default: us-west-2)
- **regions**: List of AWS regions to use for load balancing (default: us-west-2, eu-central-1, ap-northeast-2)
- **endpoints**: List of custom endpoint URLs for each region (optional, uses default AWS endpoints if not provided)
  - Must match the number of regions if specified
  - Uses HTTPS protocol and official AWS Bedrock endpoints by default
- **max_workers**: Maximum number of worker threads for parallel processing (default: 10)
  - **Important for batch processing**: Higher values allow more concurrent requests
- **default_model**: Default model to use (default: claude-3.7-sonnet)
- **auth_type**: Force specific authentication type (optional, auto-detected from credentials)
- **use_environment**: Whether to check environment variables for credentials (default: True)
- **dotenv_path**: Path to .env file (optional, defaults to .env in current directory)
- **use_dotenv**: Whether to load .env file (default: True)

### New Batch Processing Methods

- **`invoke_model_batch(model_id, bodies, check_availability=True)`**: Process multiple invoke_model requests in parallel
  - `bodies`: List of request body dictionaries
  - Returns: List of responses in same order as input
  - Uses round-robin distribution across available regions

- **`converse_model_batch(model_id, message_lists, inference_config=None, ...)`**: Process multiple converse requests in parallel
  - `message_lists`: List of message lists (each list is one conversation)
  - Returns: List of responses in same order as input
  - Uses round-robin distribution across available regions

### Environment Variables

#### Region Configuration
- **BEDROCK_REGIONS**: Comma-separated list of AWS regions (e.g., `us-west-2,eu-central-1,ap-northeast-2`)

#### Authentication (Auto-detected in priority order)
1. **AWS_BEARER_TOKEN_BEDROCK**: Bedrock API key (highest priority)
2. **BEDROCK_API_KEY**: Alternative Bedrock API key name (supported for flexibility)
3. **AWS_ACCESS_KEY_ID** + **AWS_SECRET_ACCESS_KEY** + **AWS_SESSION_TOKEN**: AWS session credentials
4. **AWS_ACCESS_KEY_ID** + **AWS_SECRET_ACCESS_KEY**: AWS access keys
5. Default AWS credential chain (IAM role, instance profile, etc.)

## Error Handling

The package includes custom exceptions for better error handling:

```python
from bedrock_region_balancer import (
    BedrockBalancerError,
    ModelNotAvailableError,
    RegionNotAvailableError,
    SecretsManagerError,
    AuthType
)

try:
    # Example with explicit auth type
    balancer = BedrockRegionBalancer(
        credentials={'bedrock_api_key': 'your-key'},
        auth_type=AuthType.BEDROCK_API_KEY  # Optional: force auth type
    )
    response = await balancer.invoke_model(model_id, body)
except ModelNotAvailableError as e:
    print(f"Model not available: {e}")
except RegionNotAvailableError as e:
    print(f"Region not available: {e}")
except SecretsManagerError as e:
    print(f"Secrets Manager error: {e}")
except ValueError as e:
    print(f"Authentication error: {e}")
except BedrockBalancerError as e:
    print(f"General error: {e}")
```

## Supported Models

The balancer supports all AWS Bedrock models with automatic ID mapping:

### Short Names to Cross Region Inference Profile IDs

**US West 2 (us-west-2):**
- `claude-3.7-sonnet` → `us.anthropic.claude-3-7-sonnet-20250219-v1:0`
- `claude-opus-4` → `us.anthropic.claude-opus-4-20250514-v1:0`
- `claude-opus-4.1` → `us.anthropic.claude-opus-4-1-20250805-v1:0`
- `claude-sonnet-4` → `us.anthropic.claude-sonnet-4-20250514-v1:0`

**EU Central 1 (eu-central-1):**
- `claude-3.7-sonnet` → `eu.anthropic.claude-3-7-sonnet-20250219-v1:0`
- `claude-sonnet-4` → `eu.anthropic.claude-sonnet-4-20250514-v1:0`

**Asia Pacific Northeast 2 (ap-northeast-2):**
- `claude-3.7-sonnet` → `apac.anthropic.claude-3-7-sonnet-20250219-v1:0`
- `claude-sonnet-4` → `apac.anthropic.claude-sonnet-4-20250514-v1:0`

## Performance Considerations

### Batch Processing Performance

Batch processing can provide significant performance improvements:

- **Parallel Execution**: Multiple requests processed simultaneously instead of sequentially
- **Round-Robin Distribution**: Automatic load balancing across available regions
- **Reduced Latency**: Lower overall response time for multiple requests
- **Better Resource Utilization**: More efficient use of network connections

### Recommended Settings

```python
# For high-throughput batch processing
balancer = BedrockRegionBalancer(
    max_workers=20,  # Increase for more concurrent requests
    regions=['us-west-2', 'eu-central-1', 'ap-northeast-2']  # Use all available regions
)

# Process large batches
batch_size = 10  # Adjust based on your needs
batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies)
```

## Requirements

- Python 3.8+
- boto3>=1.40.0 (for Bedrock support)
- botocore>=1.40.0

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/bedrock-region-balancer.git
cd bedrock-region-balancer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### Run Tests

```bash
# Run mock tests (no AWS credentials required)
python test_round_robin_mock.py

# Run connection test (requires AWS credentials)
python simple_bedrock_test.py

# Run basic functionality test
python test_basic.py

# Run round-robin test with actual API
python test_round_robin.py

# Test batch processing capabilities
python examples/basic_usage.py      # Includes batch processing examples
python examples/advanced_usage.py   # Advanced batch processing demos
python examples/batch_vs_sequential.py  # Performance comparison between batch and sequential processing
```

### Code Quality

```bash
# Format code
black bedrock_region_balancer

# Lint code
flake8 bedrock_region_balancer

# Type checking
mypy bedrock_region_balancer
```

### Publishing to PyPI

#### Prerequisites

1. Create an account on [PyPI](https://pypi.org/) and [Test PyPI](https://test.pypi.org/)
2. Install build and upload tools:
   ```bash
   pip install build twine
   ```
3. Configure PyPI credentials in `~/.pypirc`:
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-your-api-token-here

   [testpypi]
   username = __token__
   password = pypi-your-test-api-token-here
   ```

#### Build and Upload

1. **Clean previous builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

2. **Build the package**:
   ```bash
   python -m build
   ```

3. **Test upload to Test PyPI** (recommended):
   ```bash
   python -m twine upload --repository testpypi dist/*
   
   # Test installation from Test PyPI
   pip install --index-url https://test.pypi.org/simple/ bedrock-region-balancer
   ```

4. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

5. **Verify installation**:
   ```bash
   pip install bedrock-region-balancer
   ```

#### Version Management

1. Update version in `setup.py`:
   ```python
   version="0.1.1"  # Increment version number
   ```

2. Create a git tag:
   ```bash
   git tag -a v0.1.1 -m "Release version 0.1.1"
   git push origin v0.1.1
   ```

3. Update CHANGELOG.md with release notes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/yourusername/bedrock-region-balancer/issues).