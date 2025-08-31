# Azure OpenAI Setup Guide for wraipperz

This guide explains how to use Azure OpenAI models with the wraipperz library.

## Prerequisites

1. An Azure account with an active subscription
2. An Azure OpenAI resource deployed in your Azure subscription
3. At least one model deployment in your Azure OpenAI resource

## Environment Variables

Set the following environment variables:

### Required

```bash
# Your Azure OpenAI endpoint URL
export AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com"

# Your Azure OpenAI API key
export AZURE_OPENAI_API_KEY="your-api-key-here"
```

### Optional

```bash
# API version (defaults to "2024-10-01-preview")
export AZURE_OPENAI_API_VERSION="2024-10-01-preview"

# Comma-separated list of your deployment names (for documentation/discovery)
export AZURE_OPENAI_DEPLOYMENTS="gpt-4,gpt-35-turbo,gpt-4-vision"

# Default deployment name for testing
export AZURE_OPENAI_DEPLOYMENT="gpt-4"
```

## Finding Your Endpoint and API Key

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. In the left menu, click on "Keys and Endpoint"
4. Copy one of the keys and the endpoint URL

## Usage Examples

### Basic Usage

```python
from wraipperz.api.llm import call_ai
from wraipperz.api.messages import MessageBuilder

# Create messages
messages = (
    MessageBuilder()
    .add_system("You are a helpful assistant.")
    .add_user("What is the capital of France?")
    .build()
)

# Call Azure OpenAI using your deployment name
response, cost = call_ai(
    model="azure/gpt-4",  # Replace 'gpt-4' with your deployment name
    messages=messages,
    temperature=0.7,
    max_tokens=100
)

print(response)
```

### Async Usage

```python
import asyncio
from wraipperz.api.llm import call_ai_async

async def main():
    messages = [
        {"role": "user", "content": "Hello, Azure!"}
    ]
    
    response, cost = await call_ai_async(
        model="azure/gpt-35-turbo",  # Your deployment name
        messages=messages,
        temperature=0.7,
        max_tokens=100
    )
    
    print(response)

asyncio.run(main())
```

### With Vision Models

If you have a vision-capable deployment (like GPT-4 Vision):

```python
from wraipperz.api.llm import call_ai
from wraipperz.api.messages import MessageBuilder

messages = (
    MessageBuilder()
    .add_system("You are a helpful assistant.")
    .add_user("What's in this image?")
    .add_image("path/to/image.jpg")
    .build()
)

response, cost = call_ai(
    model="azure/gpt-4-vision",  # Your vision deployment name
    messages=messages,
    temperature=0.7,
    max_tokens=200
)

print(response)
```

## Model Naming Convention

In wraipperz, Azure OpenAI models are specified using the format:
```
azure/<deployment-name>
```

Where `<deployment-name>` is the name you gave to your deployment in Azure OpenAI Studio.

## Common Deployment Names

Here are some common deployment names you might use:

- `gpt-4` - GPT-4 model
- `gpt-35-turbo` - GPT-3.5 Turbo model
- `gpt-4-turbo` - GPT-4 Turbo model
- `gpt-4-vision` - GPT-4 with vision capabilities
- `gpt-5-chat` - Your custom GPT-5 deployment (if available)

## Testing Your Setup

Run the included test script to verify your Azure OpenAI setup:

```bash
python test_azure_openai.py
```

This will test:
- Basic text generation
- Async calls
- Custom deployment names

## Running Tests

To run the Azure OpenAI tests in the test suite:

```bash
# Run only Azure OpenAI tests
pytest tests/test_llm.py -k "azure_openai" -v

# Run a specific test
pytest tests/test_llm.py::test_call_ai_azure_openai_basic -v
```

## Troubleshooting

### "Deployment not found" Error

If you get a 404 or "deployment not found" error:
1. Verify the deployment name in Azure OpenAI Studio
2. Ensure the deployment is in the same region as your endpoint
3. Check that the deployment status is "Succeeded"

### Authentication Errors

If you get authentication errors:
1. Verify your API key is correct
2. Check that the key corresponds to the correct resource
3. Ensure your resource is not in a suspended state

### API Version Errors

If you get API version errors:
1. Try updating to a newer API version
2. Check [Azure OpenAI API versions](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning) for the latest versions

## Advanced Configuration

### Using Different API Versions

```python
from wraipperz.api.llm import AzureOpenAIProvider

# Create provider with custom API version
provider = AzureOpenAIProvider(
    endpoint="https://your-resource.cognitiveservices.azure.com",
    api_key="your-api-key",
    api_version="2024-02-15-preview"
)

# Use it directly
response = provider.call_ai(
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.7,
    max_tokens=100,
    model="azure/gpt-4"
)
```

### Dynamic Deployments

The Azure OpenAI provider accepts any deployment name with the `azure/` prefix, so you don't need to pre-configure all your deployments. Just use them directly:

```python
# These all work without pre-configuration
response1, _ = call_ai(model="azure/my-custom-deployment", ...)
response2, _ = call_ai(model="azure/experimental-model", ...)
response3, _ = call_ai(model="azure/production-gpt4", ...)
```

## Support

For issues or questions about Azure OpenAI integration in wraipperz:
1. Check this documentation
2. Review the test files in `tests/test_llm.py`
3. Check Azure OpenAI service status
4. Open an issue on the wraipperz repository
