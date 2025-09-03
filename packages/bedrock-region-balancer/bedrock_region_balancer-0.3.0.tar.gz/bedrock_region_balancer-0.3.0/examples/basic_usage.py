"""
Basic usage example for Bedrock Region Balancer.

This example demonstrates:
1. Using default credentials and .env file
2. Using different authentication methods
3. Custom regions and models
4. Basic error handling
"""

import asyncio
import json
import os
from bedrock_region_balancer import (
    BedrockRegionBalancer, 
    AuthType,
    ConverseAPIHelper,
    MessageRole
)


async def basic_example():
    """Basic example using default credentials and .env file."""
    print("=== Basic Example (.env file + Environment Variables) ===")
    
    # Initialize balancer - automatically loads .env file and checks environment variables
    async with BedrockRegionBalancer(
        default_model="claude-3.7-sonnet"  # Set default model (use available model)
    ) as balancer:
        
        # Use the configured default model
        model_id = balancer.get_default_model()
        print(f"Using default model: {model_id}")
        
        # Prepare request body
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": "Tell me a short joke about programming."
                }
            ],
            "max_tokens": 100,
            "temperature": 0.8,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            print("\n--- Using invoke_model API (Single Request) ---")
            # Invoke model using traditional API
            response = await balancer.invoke_model(model_id, body)
            
            print(f"Region used: {response['region']}")
            print(f"Model ID: {response['model_id']}")
            print(f"Response: {response['response']['content'][0]['text']}")
            
            print("\n--- Using invoke_model API (Batch Processing) ---")
            # Demonstrate batch processing with multiple messages
            batch_bodies = [
                {
                    "messages": [{"role": "user", "content": "What is 2+2?"}],
                    "max_tokens": 50,
                    "temperature": 0,
                    "anthropic_version": "bedrock-2023-05-31"
                },
                {
                    "messages": [{"role": "user", "content": "What is the capital of France?"}],
                    "max_tokens": 50,
                    "temperature": 0,
                    "anthropic_version": "bedrock-2023-05-31"
                },
                {
                    "messages": [{"role": "user", "content": "Name a primary color."}],
                    "max_tokens": 50,
                    "temperature": 0,
                    "anthropic_version": "bedrock-2023-05-31"
                }
            ]
            
            batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies)
            
            for i, response in enumerate(batch_responses, 1):
                print(f"Batch {i} - Region: {response['region']} - Response: {response['response']['content'][0]['text']}")
            
            print("\n--- Using converse API (Single Request) ---")
            # Same request using Converse API
            messages = [
                ConverseAPIHelper.create_message(
                    MessageRole.USER, 
                    "Tell me a short joke about programming."
                )
            ]
            
            inference_config = ConverseAPIHelper.create_inference_config(
                max_tokens=1000,
                temperature=0.8
            )
            
            converse_response = await balancer.converse_model(
                model_id=model_id,
                messages=messages,
                inference_config=inference_config
            )
            
            print(f"Region used: {converse_response['region']}")
            print(f"Model ID: {converse_response['model_id']}")
            
            # Parse converse response
            parsed = ConverseAPIHelper.parse_converse_response(converse_response['response'])
            print(f"Response: {parsed['content'][0]['text']}")
            print(f"Stop reason: {parsed['stop_reason']}")
            print(f"Usage: {parsed['usage']}")
            
            print("\n--- Using converse API (Batch Processing) ---")
            # Demonstrate batch processing with multiple message lists
            batch_message_lists = [
                [ConverseAPIHelper.create_message(MessageRole.USER, "What is 2+2?")],
                [ConverseAPIHelper.create_message(MessageRole.USER, "What is the capital of France?")],
                [ConverseAPIHelper.create_message(MessageRole.USER, "Name a primary color.")]
            ]
            
            batch_inference_config = ConverseAPIHelper.create_inference_config(
                max_tokens=50,
                temperature=0
            )
            
            batch_converse_responses = await balancer.converse_model_batch(
                model_id=model_id,
                message_lists=batch_message_lists,
                inference_config=batch_inference_config
            )
            
            for i, response in enumerate(batch_converse_responses, 1):
                parsed = ConverseAPIHelper.parse_converse_response(response['response'])
                print(f"Batch {i} - Region: {response['region']} - Response: {parsed['content'][0]['text']}")
            
            # Show availability report
            report = balancer.get_model_availability_report()
            print(f"\nDefault model: {report['default_model']}")
            print(f"Available regions: {report['available_regions']}")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Note: Make sure you have credentials configured via .env file, environment variables, or AWS credentials")


async def bedrock_api_key_example():
    """Example using Bedrock API Key authentication."""
    print("\n=== Bedrock API Key Example ===")
    
    # Check if API key is available
    api_key = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
    
    if not api_key:
        print("Skipping Bedrock API Key example - no API key found in environment")
        print("Set AWS_BEARER_TOKEN_BEDROCK environment variable to test this")
        return
    
    async with BedrockRegionBalancer(
        credentials={'bedrock_api_key': api_key},
        auth_type=AuthType.BEDROCK_API_KEY,  # Explicitly specify auth type
        default_model="claude-3.7-sonnet"
    ) as balancer:
        
        model_id = balancer.get_default_model()
        
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": "What is the capital of France?"
                }
            ],
            "max_tokens": 50,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            print("Testing both APIs with Bedrock API Key authentication...")
            
            print("\n--- invoke_model API ---")
            response = await balancer.invoke_model(model_id, body)
            print(f"Authentication successful with Bedrock API Key")
            print(f"Response from {response['region']}: {response['response']['content'][0]['text']}")
            
            print("\n--- converse API ---")
            # Same request using Converse API
            messages = [
                ConverseAPIHelper.create_message(MessageRole.USER, "What is the capital of France?")
            ]
            
            converse_response = await balancer.converse_model(
                model_id=model_id,
                messages=messages,
                inference_config={"maxTokens": 50, "temperature": 0}
            )
            
            parsed = ConverseAPIHelper.parse_converse_response(converse_response['response'])
            print(f"Converse API successful with Bedrock API Key")
            print(f"Response from {converse_response['region']}: {parsed['content'][0]['text']}")
            
        except Exception as e:
            print(f"Error with Bedrock API Key: {e}")


async def aws_credentials_example():
    """Example using AWS access key credentials."""
    print("\n=== AWS Credentials Example ===")
    
    # Check if AWS credentials are available
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    session_token = os.getenv('AWS_SESSION_TOKEN')
    
    if not (access_key and secret_key):
        print("Skipping AWS Credentials example - no AWS credentials found")
        print("Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables to test this")
        return
    
    # Prepare credentials dictionary
    credentials = {
        'aws_access_key_id': access_key,
        'aws_secret_access_key': secret_key
    }
    
    # Add session token if available
    if session_token:
        credentials['aws_session_token'] = session_token
        print("Using AWS Session Credentials")
    else:
        print("Using AWS Access Keys")
    
    async with BedrockRegionBalancer(
        credentials=credentials,
        default_model="claude-3.7-sonnet"
    ) as balancer:
        
        model_id = balancer.get_default_model()
        
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": "What is 2 + 2?"
                }
            ],
            "max_tokens": 50,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            response = await balancer.invoke_model(model_id, body)
            auth_type = "Session" if session_token else "Access Key"
            print(f"Authentication successful with AWS {auth_type}")
            print(f"Response from {response['region']}: {response['response']['content'][0]['text']}")
        except Exception as e:
            print(f"Error with AWS credentials: {e}")


async def custom_regions_example():
    """Example using custom regions."""
    print("\n=== Custom Regions Example ===")
    
    # Initialize with custom regions
    async with BedrockRegionBalancer(
        regions=["us-east-1", "us-west-2"]
    ) as balancer:
        # Example with Claude 3.7 Sonnet (native region model)
        model_id = "claude-3.7-sonnet"
        
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": "What is 2 + 2?"
                }
            ],
            "max_tokens": 50,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            response = await balancer.invoke_model(model_id, body)
            print(f"Response from {response['region']}: {response['response']['content'][0]['text']}")
        except Exception as e:
            print(f"Error: {e}")


async def multi_region_example():
    """Example invoking model in all regions."""
    print("\n=== Multi-Region Example ===")
    
    async with BedrockRegionBalancer() as balancer:
        model_id = "claude-3.7-sonnet"
        
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Hello from [region]' where [region] is your AWS region."
                }
            ],
            "max_tokens": 50,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            # Invoke in all regions (traditional method)
            print("\n--- All Regions (Traditional Method) ---")
            responses = await balancer.invoke_model_all_regions(model_id, body)
            
            for response in responses:
                if 'error' in response:
                    print(f"Error in {response['region']}: {response['error']}")
                else:
                    print(f"Response from {response['region']}: "
                          f"{response['response']['content'][0]['text']}")
            
            # Demonstrate batch processing advantage
            print("\n--- Batch Processing (Round-Robin Distribution) ---")
            batch_bodies = [body] * 3  # Same message, sent to different regions via round-robin
            batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies)
            
            for i, response in enumerate(batch_responses, 1):
                print(f"Batch {i} from {response['region']}: {response['response']['content'][0]['text']}")
                          
        except Exception as e:
            print(f"Error: {e}")


async def availability_check_example():
    """Example checking model availability."""
    print("\n=== Model Availability Check ===")
    
    async with BedrockRegionBalancer() as balancer:
        # Get availability report
        report = balancer.get_model_availability_report()
        
        print(f"Configured regions: {report['regions']}")
        print(f"Available regions: {report['available_regions']}")
        print(f"Current round-robin index: {report['current_region_index']}")
        
        # Show sample of available models per region
        for region, models in report['models_by_region'].items():
            if models:
                print(f"\n{region}: {len(models)} models available")
                print(f"  Sample models: {models[:3]}...")


async def round_robin_demonstration():
    """Demonstrate round-robin behavior."""
    print("\n=== Round-Robin Demonstration ===")
    
    async with BedrockRegionBalancer() as balancer:
        model_id = "claude-3.7-sonnet"
        
        print("\n--- Sequential Requests (Traditional) ---")
        # Make multiple requests to see round-robin in action
        for i in range(6):
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Request {i+1}: What region are you in?"
                    }
                ],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            try:
                response = await balancer.invoke_model(model_id, body)
                print(f"Request {i+1} -> Region: {response['region']}")
            except Exception as e:
                print(f"Request {i+1} failed: {e}")
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        print("\n--- Batch Requests (Parallel with Round-Robin) ---")
        # Demonstrate batch processing with round-robin distribution
        batch_bodies = []
        for i in range(6):
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Batch request {i+1}: What region are you in?"
                    }
                ],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            batch_bodies.append(body)
        
        try:
            batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies)
            for i, response in enumerate(batch_responses, 1):
                print(f"Batch Request {i} -> Region: {response['region']}")
        except Exception as e:
            print(f"Batch requests failed: {e}")


async def api_comparison_example():
    """Compare invoke_model vs converse API performance and features."""
    print("\n=== API Comparison: invoke_model vs converse ===")
    
    async with BedrockRegionBalancer() as balancer:
        model_id = balancer.get_default_model()
        
        # Test 1: Basic text generation comparison
        print("\nTest 1: Basic text generation")
        print("-" * 30)
        
        prompt = "Explain machine learning in one sentence."
        
        # invoke_model API
        print("invoke_model API:")
        try:
            invoke_body = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.3,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            import time
            start_time = time.time()
            invoke_response = await balancer.invoke_model(model_id, invoke_body)
            invoke_time = time.time() - start_time
            
            print(f"  Region: {invoke_response['region']}")
            print(f"  Time: {invoke_time:.2f}s")
            print(f"  Response: {invoke_response['response']['content'][0]['text']}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        # converse API
        print("\nconverse API:")
        try:
            messages = [ConverseAPIHelper.create_message(MessageRole.USER, prompt)]
            inference_config = {"maxTokens": 50, "temperature": 0.3}
            
            start_time = time.time()
            converse_response = await balancer.converse_model(
                model_id=model_id,
                messages=messages,
                inference_config=inference_config
            )
            converse_time = time.time() - start_time
            
            parsed = ConverseAPIHelper.parse_converse_response(converse_response['response'])
            
            print(f"  Region: {converse_response['region']}")
            print(f"  Time: {converse_time:.2f}s")
            print(f"  Response: {parsed['content'][0]['text']}")
            print(f"  Stop reason: {parsed['stop_reason']}")
            print(f"  Usage info: {parsed['usage']}")
            
        except Exception as e:
            print(f"  Error: {e}")
        
        # Test 2: Multimodal content (converse only)
        print("\nTest 2: Multimodal content support")
        print("-" * 35)
        
        print("invoke_model API: Limited multimodal support")
        print("converse API: Native multimodal support")
        
        # Demonstrate multimodal message creation (without actual image)
        try:
            multimodal_content = [
                ConverseAPIHelper.create_text_content("If I had an image of a cat, what would you tell me about it?"),
                # ConverseAPIHelper.create_image_content(source={"bytes": image_bytes}, format="png")
            ]
            
            multimodal_messages = [
                ConverseAPIHelper.create_message(MessageRole.USER, multimodal_content)
            ]
            
            multimodal_response = await balancer.converse_model(
                model_id=model_id,
                messages=multimodal_messages,
                inference_config={"maxTokens": 100}
            )
            
            parsed = ConverseAPIHelper.parse_converse_response(multimodal_response['response'])
            print(f"  Multimodal response: {parsed['content'][0]['text']}")
            
        except Exception as e:
            print(f"  Multimodal test error: {e}")
        
        # Test 3: Format conversion
        print("\nTest 3: Format conversion")
        print("-" * 25)
        
        try:
            # Original invoke_model format
            original_body = {
                "messages": [{"role": "user", "content": "What is 2+2?"}],
                "max_tokens": 20,
                "temperature": 0,
                "system": "You are a helpful math tutor."
            }
            
            print("Original invoke_model format:")
            print(f"  {original_body}")
            
            # Convert to converse format
            converted = ConverseAPIHelper.convert_invoke_model_to_converse(original_body)
            print("\nConverted to converse format:")
            print(f"  messages: {converted['messages']}")
            print(f"  inferenceConfig: {converted.get('inferenceConfig')}")
            print(f"  system: {converted.get('system')}")
            
            # Use converted format
            conversion_response = await balancer.converse_model(
                model_id=model_id,
                messages=converted['messages'],
                inference_config=converted.get('inferenceConfig'),
                system=converted.get('system')
            )
            
            parsed = ConverseAPIHelper.parse_converse_response(conversion_response['response'])
            print(f"  Converted format works: {parsed['content'][0]['text']}")
            
        except Exception as e:
            print(f"  Format conversion error: {e}")


async def batch_processing_example():
    """Example demonstrating batch processing capabilities."""
    print("\n=== Batch Processing Capabilities ===")
    
    async with BedrockRegionBalancer() as balancer:
        model_id = "claude-3.7-sonnet"
        
        print("\n--- Performance Comparison: Sequential vs Batch ---")
        
        # Sequential processing
        print("Sequential processing (3 requests):")
        import time
        start_time = time.time()
        
        for i in range(3):
            body = {
                "messages": [{"role": "user", "content": f"Count to {i+1}"}],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            response = await balancer.invoke_model(model_id, body)
            print(f"  Request {i+1}: Region {response['region']}")
        
        sequential_time = time.time() - start_time
        print(f"  Sequential time: {sequential_time:.2f}s")
        
        # Batch processing
        print("\nBatch processing (3 requests):")
        start_time = time.time()
        
        batch_bodies = [
            {
                "messages": [{"role": "user", "content": "Count to 1"}],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            },
            {
                "messages": [{"role": "user", "content": "Count to 2"}],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            },
            {
                "messages": [{"role": "user", "content": "Count to 3"}],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
        ]
        
        batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies)
        
        for i, response in enumerate(batch_responses, 1):
            print(f"  Batch {i}: Region {response['region']}")
        
        batch_time = time.time() - start_time
        print(f"  Batch time: {batch_time:.2f}s")
        
        if sequential_time > 0:
            speedup = sequential_time / batch_time
            print(f"  Speedup: {speedup:.2f}x faster with batch processing")
        
        print("\n--- Converse API Batch Processing ---")
        # Demonstrate converse API batch processing
        batch_message_lists = [
            [ConverseAPIHelper.create_message(MessageRole.USER, "What is 1+1?")],
            [ConverseAPIHelper.create_message(MessageRole.USER, "What is 2+2?")],
            [ConverseAPIHelper.create_message(MessageRole.USER, "What is 3+3?")]
        ]
        
        batch_converse_responses = await balancer.converse_model_batch(
            model_id=model_id,
            message_lists=batch_message_lists,
            inference_config={"maxTokens": 50, "temperature": 0}
        )
        
        for i, response in enumerate(batch_converse_responses, 1):
            parsed = ConverseAPIHelper.parse_converse_response(response['response'])
            print(f"  Converse Batch {i}: Region {response['region']} - {parsed['content'][0]['text']}")


async def main():
    """Run all examples."""
    print("Bedrock Region Balancer - Basic Usage Examples with Batch Processing")
    print("=" * 70)
    print()
    print("Note: Examples will use different authentication methods based on available credentials.")
    print("Priority: Bedrock API Key > AWS Session > AWS Access Keys > Default AWS Chain")
    print()
    print("Default regions: us-west-2, eu-central-1, ap-northeast-2")
    print("Override with BEDROCK_REGIONS environment variable or .env file")
    print()
    print("NEW: Batch processing support for improved performance and region distribution")
    print()

    # Run authentication examples
    print("=" * 50)
    print("Basic Examples")
    print("=" * 50)
    await basic_example()
    await asyncio.sleep(10)
    print("=" * 50)
    print("Bedrock API Key Example")
    print("=" * 50)
    await bedrock_api_key_example()
    await asyncio.sleep(10)
    print("=" * 50)
    print("AWS Credentials Example")
    print("=" * 50)
    await aws_credentials_example()
    await asyncio.sleep(10)
    print("=" * 50)

    # Run feature examples
    print("=" * 50)
    print("Custom Regions Example")
    print("=" * 50)
    await custom_regions_example()
    await asyncio.sleep(10)
    print("=" * 50)
    print("Multi-Region Example")
    print("=" * 50)
    await multi_region_example()
    await asyncio.sleep(10)
    print("=" * 50)
    print("Batch Processing Example")
    print("=" * 50)
    await batch_processing_example()  # New batch processing example
    await asyncio.sleep(10)
    print("=" * 50)
    print("Availability Check Example")
    print("=" * 50)
    await availability_check_example()
    await asyncio.sleep(10)
    print("=" * 50)
    print("API Comparison Example")
    print("=" * 50)
    await api_comparison_example()  # New API comparison
    await asyncio.sleep(10)
    print("=" * 50)
    print("Round-Robin Demonstration")
    print("=" * 50)
    await round_robin_demonstration()
    await asyncio.sleep(10)

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo set up credentials:")
    print("1. Copy .env.example to .env and fill in your credentials")
    print("2. Or set environment variables directly")
    print("3. Or use AWS Secrets Manager with secret_name parameter")
    print("4. Or rely on default AWS credential chain (IAM roles, etc.)")


if __name__ == "__main__":
    asyncio.run(main())
