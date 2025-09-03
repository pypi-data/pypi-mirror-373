"""
Advanced usage examples for Bedrock Region Balancer.

This example demonstrates:
1. AWS Secrets Manager integration with multiple credential formats
2. Custom .env file locations and configurations
3. Advanced error handling and recovery
4. Performance optimization techniques
5. Concurrent processing patterns
6. NEW: Batch processing for improved performance and load distribution
"""

import asyncio
import json
import time
import os
from bedrock_region_balancer import (
    BedrockRegionBalancer,
    ModelNotAvailableError,
    RegionNotAvailableError,
    SecretsManagerError,
    AuthType,
    ConverseAPIHelper,
    MessageRole
)


async def secrets_manager_example():
    """Example using AWS Secrets Manager with different credential formats."""
    print("=== AWS Secrets Manager Example ===")
    
    # This example shows how to use different credential formats in Secrets Manager
    # You would need to create these secrets in your AWS account
    
    secret_names = [
        "bedrock-api-key-secret",      # For Bedrock API keys
        "aws-access-key-secret",       # For AWS access keys
        "aws-session-secret"           # For AWS session credentials
    ]
    
    for secret_name in secret_names:
        print(f"\nTrying secret: {secret_name}")
        try:
            async with BedrockRegionBalancer(
                secret_name=secret_name,
                secret_region="us-west-2",
                default_model="claude-3.7-sonnet"
            ) as balancer:
                
                model_id = balancer.get_default_model()
                body = {
                    "messages": [{"role": "user", "content": f"Hello from {secret_name}!"}],
                    "max_tokens": 30,
                    "temperature": 0,
                    "anthropic_version": "bedrock-2023-05-31"
                }
                
                response = await balancer.invoke_model(model_id, body)
                print(f"✓ Success with {secret_name}")
                print(f"  Region: {response['region']}")
                print(f"  Response: {response['response']['content'][0]['text']}")
                
        except SecretsManagerError as e:
            print(f"✗ Secrets Manager error: {e}")
        except Exception as e:
            print(f"✗ Other error: {e}")


async def custom_dotenv_example():
    """Example using custom .env file locations."""
    print("\n=== Custom .env File Example ===")
    
    # Example with different .env file locations
    env_files = [
        ".env.development",
        ".env.staging", 
        ".env.production",
        "/path/to/custom/.env"
    ]
    
    for env_file in env_files:
        print(f"\nTrying .env file: {env_file}")
        
        # Check if file exists (for demonstration)
        if not os.path.exists(env_file) and not env_file.startswith("/path/"):
            print(f"  File {env_file} not found, skipping...")
            continue
            
        try:
            async with BedrockRegionBalancer(
                dotenv_path=env_file if env_file != "/path/to/custom/.env" else None,
                use_dotenv=True,
                default_model="claude-3.7-sonnet"
            ) as balancer:
                
                print(f"✓ Successfully loaded {env_file}")
                
                # Show configuration
                report = balancer.get_model_availability_report()
                print(f"  Default model: {report['default_model']}")
                print(f"  Available regions: {report['available_regions']}")
                
        except Exception as e:
            print(f"✗ Error loading {env_file}: {e}")


async def custom_regions_example():
    """Example with custom regions and Cross Region Inference."""
    print("\n=== Custom Regions with Cross Region Inference ===")
    
    # Use only specific regions with Cross Region Inference model IDs
    custom_regions = ['us-west-2', 'eu-central-1', 'ap-northeast-2']
    
    async with BedrockRegionBalancer(
        regions=custom_regions,
        default_model="claude-3.7-sonnet"  # Will be converted to region-specific ID
    ) as balancer:
        print(f"Using custom regions: {custom_regions}")
        print(f"Available regions: {balancer.bedrock_client.get_available_regions()}")
        
        model_id = balancer.get_default_model()
        body = {
            "messages": [{"role": "user", "content": "Tell me which region you're running in!"}],
            "max_tokens": 50,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            response = await balancer.invoke_model(model_id, body)
            print(f"✓ Response from {response['region']}")
            print(f"  Model ID: {response['model_id']}")
            print(f"  Content: {response['response']['content'][0]['text']}")
        except Exception as e:
            print(f"✗ Error: {e}")


async def error_handling_example():
    """Example demonstrating error handling."""
    print("\n=== Error Handling Example ===")
    
    async with BedrockRegionBalancer() as balancer:
        # Try with a non-existent model
        fake_model_id = "non-existent-model-id"
        body = {
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 10,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            await balancer.invoke_model(fake_model_id, body)
        except ModelNotAvailableError as e:
            print(f"Model not available error (expected): {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        # Try with check_availability=False to skip the check
        print("\nSkipping availability check...")
        try:
            await balancer.invoke_model(fake_model_id, body, check_availability=False)
        except Exception as e:
            print(f"Error when invoking non-existent model: {type(e).__name__}")


async def performance_comparison():
    """Compare performance with and without availability checking."""
    print("\n=== Performance Comparison ===")
    
    async with BedrockRegionBalancer() as balancer:
        model_id = "claude-3.7-sonnet"  # Use Cross Region Inference model
        body = {
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            # With availability check
            start_time = time.time()
            await balancer.invoke_model(model_id, body, check_availability=True)
            with_check_time = time.time() - start_time
            
            # Without availability check (using cache)
            start_time = time.time()
            await balancer.invoke_model(model_id, body, check_availability=False)
            without_check_time = time.time() - start_time
            
            print(f"✓ With availability check: {with_check_time:.3f}s")
            print(f"✓ Without availability check: {without_check_time:.3f}s")
            print(f"✓ Speed improvement: {(with_check_time/without_check_time):.1f}x")
            
        except Exception as e:
            print(f"✗ Performance comparison failed: {e}")
            print("This is expected if you don't have access to the model")


async def batch_processing_advanced_example():
    """Advanced example demonstrating batch processing performance benefits."""
    print("\n=== Advanced Batch Processing Example ===")
    
    async with BedrockRegionBalancer() as balancer:
        model_id = "claude-3.7-sonnet"
        
        print("\n--- Comparing Sequential vs Batch Processing ---")
        
        # Prepare multiple requests
        num_requests = 10
        
        # Sequential processing with individual calls
        print(f"\nSequential processing ({num_requests} individual requests):")
        start_time = time.time()
        sequential_results = []
        
        for i in range(num_requests):
            body = {
                "messages": [{"role": "user", "content": f"Question {i+1}: What is {i+1} + {i+1}?"}],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            try:
                response = await balancer.invoke_model(model_id, body, check_availability=False)
                sequential_results.append({
                    'id': i+1,
                    'region': response['region'],
                    'success': True
                })
            except Exception as e:
                sequential_results.append({
                    'id': i+1,
                    'error': str(e),
                    'success': False
                })
        
        sequential_time = time.time() - start_time
        sequential_success = len([r for r in sequential_results if r['success']])
        
        # Batch processing with new batch API
        print(f"\nBatch processing ({num_requests} requests in single batch):")
        start_time = time.time()
        
        batch_bodies = []
        for i in range(num_requests):
            body = {
                "messages": [{"role": "user", "content": f"Question {i+1}: What is {i+1} + {i+1}?"}],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            batch_bodies.append(body)
        
        try:
            batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies, check_availability=False)
            batch_results = []
            for i, response in enumerate(batch_responses):
                batch_results.append({
                    'id': i+1,
                    'region': response['region'],
                    'success': True
                })
        except Exception as e:
            print(f"Batch processing failed: {e}")
            batch_results = []
        
        batch_time = time.time() - start_time
        batch_success = len([r for r in batch_results if r['success']])
        
        # Results comparison
        print(f"\nResults Comparison:")
        print(f"Sequential: {sequential_success}/{num_requests} successful in {sequential_time:.2f}s")
        print(f"Batch:      {batch_success}/{num_requests} successful in {batch_time:.2f}s")
        
        if batch_time > 0 and sequential_time > 0:
            speedup = sequential_time / batch_time
            print(f"Speedup:    {speedup:.2f}x faster with batch processing")
        
        # Show region distribution for batch processing
        if batch_results:
            region_counts = {}
            for result in batch_results:
                if result['success']:
                    region = result['region']
                    region_counts[region] = region_counts.get(region, 0) + 1
            
            print(f"\nBatch region distribution:")
            for region, count in sorted(region_counts.items()):
                print(f"  {region}: {count} requests")
        
        # Demonstrate Converse API batch processing
        print("\n--- Converse API Batch Processing ---")
        
        batch_message_lists = []
        for i in range(5):
            messages = [ConverseAPIHelper.create_message(
                MessageRole.USER, 
                f"Converse question {i+1}: What color is the number {i+1}?"
            )]
            batch_message_lists.append(messages)
        
        start_time = time.time()
        try:
            converse_batch_responses = await balancer.converse_model_batch(
                model_id=model_id,
                message_lists=batch_message_lists,
                inference_config={"maxTokens": 30, "temperature": 0},
                check_availability=False
            )
            converse_batch_time = time.time() - start_time
            
            print(f"Converse batch processing: {len(converse_batch_responses)} requests in {converse_batch_time:.2f}s")
            
            for i, response in enumerate(converse_batch_responses, 1):
                parsed = ConverseAPIHelper.parse_converse_response(response['response'])
                print(f"  Request {i} -> {response['region']}: {parsed['content'][0]['text'][:50]}...")
                
        except Exception as e:
            print(f"Converse batch processing failed: {e}")


async def concurrent_requests_example():
    """Example of making concurrent requests with both APIs."""
    print("\n=== Concurrent Requests Example (Both APIs) ===")
    
    try:
        async with BedrockRegionBalancer(max_workers=20) as balancer:
            model_id = "claude-3.7-sonnet"  # Use Cross Region Inference model
            
            # Test 1: invoke_model API concurrent requests
            print("\nTesting concurrent invoke_model requests:")
            
            async def make_invoke_request(request_id: int):
                body = {
                    "messages": [
                        {"role": "user", "content": f"This is invoke_model request {request_id}"}
                    ],
                    "max_tokens": 20,
                    "temperature": 0,
                    "anthropic_version": "bedrock-2023-05-31"
                }
                
                try:
                    start = time.time()
                    response = await balancer.invoke_model(model_id, body, check_availability=False)
                    elapsed = time.time() - start
                    return {
                        'request_id': request_id,
                        'api': 'invoke_model',
                        'region': response['region'],
                        'time': elapsed,
                        'success': True
                    }
                except Exception as e:
                    return {
                        'request_id': request_id,
                        'api': 'invoke_model',
                        'error': str(e),
                        'success': False
                    }
            
            # Test 2: converse API concurrent requests
            async def make_converse_request(request_id: int):
                messages = [
                    ConverseAPIHelper.create_message(
                        MessageRole.USER, 
                        f"This is converse API request {request_id}"
                    )
                ]
                
                try:
                    start = time.time()
                    response = await balancer.converse_model(
                        model_id=model_id,
                        messages=messages,
                        inference_config={"maxTokens": 20, "temperature": 0},
                        check_availability=False
                    )
                    elapsed = time.time() - start
                    return {
                        'request_id': request_id,
                        'api': 'converse',
                        'region': response['region'],
                        'time': elapsed,
                        'success': True
                    }
                except Exception as e:
                    return {
                        'request_id': request_id,
                        'api': 'converse',
                        'error': str(e),
                        'success': False
                    }
            
            # Launch concurrent requests for both APIs
            num_requests_per_api = 5
            
            # Invoke model requests
            start_time = time.time()
            invoke_tasks = [make_invoke_request(i) for i in range(num_requests_per_api)]
            invoke_results = await asyncio.gather(*invoke_tasks)
            invoke_time = time.time() - start_time
            
            # Converse API requests
            start_time = time.time()
            converse_tasks = [make_converse_request(i) for i in range(num_requests_per_api)]
            converse_results = await asyncio.gather(*converse_tasks)
            converse_time = time.time() - start_time
            
            # Analyze results for both APIs
            def analyze_results(results, api_name, total_time):
                successful = [r for r in results if r['success']]
                failed = [r for r in results if not r['success']]
                
                print(f"\n{api_name} API Results:")
                print(f"  Total requests: {len(results)}")
                print(f"  Successful: {len(successful)}")
                print(f"  Failed: {len(failed)}")
                print(f"  Total time: {total_time:.2f}s")
                if len(results) > 0:
                    print(f"  Average time per request: {total_time/len(results):.2f}s")
                
                # Show region distribution
                region_counts = {}
                for result in successful:
                    region = result['region']
                    region_counts[region] = region_counts.get(region, 0) + 1
                
                if region_counts:
                    print(f"  Region distribution:")
                    for region, count in sorted(region_counts.items()):
                        print(f"    {region}: {count} requests")
            
            analyze_results(invoke_results, "invoke_model", invoke_time)
            analyze_results(converse_results, "converse", converse_time)
            
            # Test 3: Mixed concurrent requests
            print("\nTesting mixed concurrent requests (both APIs together):")
            
            mixed_tasks = []
            mixed_tasks.extend([make_invoke_request(i) for i in range(3)])
            mixed_tasks.extend([make_converse_request(i) for i in range(3)])
            
            start_time = time.time()
            mixed_results = await asyncio.gather(*mixed_tasks)
            mixed_time = time.time() - start_time
            
            successful_mixed = [r for r in mixed_results if r['success']]
            print(f"  Mixed API requests: {len(mixed_results)} total")
            print(f"  Successful: {len(successful_mixed)}")
            print(f"  Total time: {mixed_time:.2f}s")
            
            # Show API distribution
            api_counts = {}
            region_counts = {}
            for result in successful_mixed:
                api = result['api']
                region = result['region']
                api_counts[api] = api_counts.get(api, 0) + 1
                region_counts[region] = region_counts.get(region, 0) + 1
            
            if api_counts:
                print(f"  API distribution: {api_counts}")
            if region_counts:
                print(f"  Region distribution: {region_counts}")
            
    except Exception as e:
        print(f"✗ Concurrent requests example failed: {e}")
        print("This is expected if you don't have access to the model")


async def streaming_example():
    """Example with streaming responses (if supported by model)."""
    print("\n=== Streaming Example ===")
    
    try:
        async with BedrockRegionBalancer() as balancer:
            # Note: Streaming support depends on the model
            # This is a conceptual example
            model_id = "claude-3.7-sonnet"
            
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": "Write a haiku about cloud computing."
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.7,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            try:
                response = await balancer.invoke_model(model_id, body)
                print(f"Response from {response['region']}:")
                print(response['response']['content'][0]['text'])
            except Exception as e:
                print(f"✗ Streaming request failed: {e}")
            
    except Exception as e:
        print(f"✗ Streaming example failed: {e}")
        print("This is expected if you don't have access to the model")


async def model_migration_example():
    """Example showing how to handle model migrations."""
    print("\n=== Model Migration Example ===")
    
    try:
        async with BedrockRegionBalancer() as balancer:
            # List of models to try (from newest to oldest)
            model_versions = [
                "claude-3.7-sonnet",
                "claude-3.7-sonnet",
                "claude-3.7-sonnet"  # Older model as fallback
            ]
            
            body = {
                "messages": [{"role": "user", "content": "What's the weather like?"}],
                "max_tokens": 50,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            # Try models in order until one works
            for model_id in model_versions:
                try:
                    print(f"Trying model: {model_id}")
                    response = await balancer.invoke_model(model_id, body)
                    print(f"Success! Using {model_id} in region {response['region']}")
                    break
                except ModelNotAvailableError:
                    print(f"  Model {model_id} not available, trying next...")
                    continue
                except Exception as e:
                    print(f"  Unexpected error with {model_id}: {e}")
                    break
                
    except Exception as e:
        print(f"✗ Model migration example failed: {e}")
        print("This is expected if you don't have access to the model")


async def main():
    """Run all advanced examples."""
    print("Bedrock Region Balancer - Advanced Usage Examples with Batch Processing")
    print("=" * 70)
    print()
    print("This demonstrates advanced features including:")
    print("• AWS Secrets Manager integration")
    print("• Custom .env file locations")
    print("• Cross Region Inference model IDs")
    print("• Advanced error handling")
    print("• Performance optimization")
    print("• Concurrent request patterns")
    print("• NEW: Batch processing for improved performance")
    print()
    
    # New advanced examples
    await secrets_manager_example()
    await custom_dotenv_example() 
    await custom_regions_example()
    
    # Existing examples (updated)
    await error_handling_example()
    await performance_comparison()
    await batch_processing_advanced_example()  # New batch processing example
    await concurrent_requests_example()
    await streaming_example()
    await model_migration_example()
    
    print("\n" + "=" * 70)
    print("Advanced examples completed!")
    print("\nKey takeaways:")
    print("• Secrets Manager supports Bedrock API keys and AWS credentials")
    print("• .env files can be customized for different environments")
    print("• Cross Region Inference provides automatic failover")
    print("• Multiple authentication methods work seamlessly together")
    print("• Error handling enables graceful degradation")
    print("• NEW: Batch processing provides significant performance improvements")
    print("• NEW: Round-robin distribution in batch processing improves load balancing")


if __name__ == "__main__":
    asyncio.run(main())