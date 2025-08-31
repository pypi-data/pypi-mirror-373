#!/usr/bin/env python3
"""
Simple test script for Azure OpenAI integration with wraipperz.

Before running, set these environment variables:
- AZURE_OPENAI_ENDPOINT: Your Azure OpenAI endpoint URL
- AZURE_OPENAI_API_KEY: Your Azure OpenAI API key
- AZURE_OPENAI_DEPLOYMENT: Your deployment name (optional, defaults to 'gpt-4')
- AZURE_OPENAI_API_VERSION: API version (optional, defaults to '2024-10-01-preview')
- AZURE_OPENAI_DEPLOYMENTS: Comma-separated list of deployments (optional)

Example usage:
    export AZURE_OPENAI_ENDPOINT="https://your-resource.cognitiveservices.azure.com"
    export AZURE_OPENAI_API_KEY="your-api-key"
    export AZURE_OPENAI_DEPLOYMENT="gpt-5-chat"
    python test_azure_openai.py
"""

import asyncio
import os

from wraipperz.api.llm import call_ai, call_ai_async
from wraipperz.api.messages import MessageBuilder


def test_basic_call():
    """Test basic Azure OpenAI call"""
    print("\n🔍 Testing basic Azure OpenAI call...")

    # Get deployment name from environment
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    print(f"   Using deployment: {deployment}")

    # Create messages using MessageBuilder
    messages = (
        MessageBuilder()
        .add_system("You are a helpful assistant.")
        .add_user("What is the capital of France? Answer in one word.")
        .build()
    )

    try:
        # Call Azure OpenAI
        response, cost = call_ai(
            model=f"azure/{deployment}",
            messages=messages,
            temperature=0.7,
            max_tokens=100,
        )

        print(f"✅ Response: {response}")
        print(f"   Cost estimate: ${cost:.6f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_async_call():
    """Test async Azure OpenAI call"""
    print("\n🔍 Testing async Azure OpenAI call...")

    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    print(f"   Using deployment: {deployment}")

    messages = [{"role": "user", "content": "Count from 1 to 5"}]

    try:
        # Async call to Azure OpenAI
        response, cost = await call_ai_async(
            model=f"azure/{deployment}", messages=messages, temperature=0, max_tokens=50
        )

        print(f"✅ Response: {response}")
        print(f"   Cost estimate: ${cost:.6f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_custom_deployment():
    """Test with a specific deployment name"""
    print("\n🔍 Testing with custom deployment...")

    # You can specify any deployment name
    deployment = "gpt-5-chat"  # Replace with your actual deployment name
    print(f"   Using deployment: {deployment}")

    messages = [
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Write a Python hello world in one line."},
    ]

    try:
        response, cost = call_ai(
            model=f"azure/{deployment}", messages=messages, temperature=0, max_tokens=50
        )

        print(f"✅ Response: {response}")
        print(f"   Cost estimate: ${cost:.6f}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        # Check if it's a deployment not found error
        if "404" in str(e) or "not found" in str(e).lower():
            print(
                f"   Deployment '{deployment}' not found. Make sure it exists in your Azure OpenAI resource."
            )
        return False


def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")

    required = {
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
    }

    optional = {
        "AZURE_OPENAI_API_VERSION": os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-10-01-preview"
        ),
        "AZURE_OPENAI_DEPLOYMENT": os.getenv(
            "AZURE_OPENAI_DEPLOYMENT",
            "Not set - will use deployment name in model param",
        ),
        "AZURE_OPENAI_DEPLOYMENTS": os.getenv(
            "AZURE_OPENAI_DEPLOYMENTS", "Not set - will accept any deployment"
        ),
    }

    all_set = True
    for key, value in required.items():
        if value:
            # Mask sensitive data
            if "KEY" in key:
                display_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                display_value = value
            print(f"   ✅ {key}: {display_value}")
        else:
            print(f"   ❌ {key}: Not set (REQUIRED)")
            all_set = False

    print("\n   Optional variables:")
    for key, value in optional.items():
        print(f"   ℹ️  {key}: {value}")

    return all_set


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Azure OpenAI Integration Test for wraipperz")
    print("=" * 60)

    # Check environment
    if not check_environment():
        print("\n❌ Missing required environment variables!")
        print("Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
        return

    print("\n" + "=" * 60)

    # Run tests
    results = []

    # Test 1: Basic call
    results.append(("Basic call", test_basic_call()))

    # Test 2: Async call
    results.append(("Async call", await test_async_call()))

    # Test 3: Custom deployment
    results.append(("Custom deployment", test_with_custom_deployment()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("-" * 60)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print("-" * 60)
    print(f"Results: {total_passed}/{total_tests} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
