"""
Batch vs Sequential Processing Comparison Example.

This example demonstrates the performance difference between:
1. Sequential processing (one request at a time)
2. Batch processing (multiple requests in parallel with round-robin distribution)

Key Features Demonstrated:
- Performance comparison with real timing metrics
- Round-robin region distribution in batch processing
- Memory and resource efficiency
- Error handling in both scenarios
- Both invoke_model and converse API comparisons
"""

import asyncio
import time
import statistics
from bedrock_region_balancer import (
    BedrockRegionBalancer,
    ConverseAPIHelper,
    MessageRole
)


async def sequential_processing_example(balancer, num_requests=10):
    """Demonstrate traditional sequential processing."""
    print(f"=== Sequential Processing ({num_requests} requests) ===")
    
    model_id = "claude-3.7-sonnet"
    results = []
    regions_used = []
    
    start_time = time.time()
    
    for i in range(num_requests):
        body = {
            "messages": [{"role": "user", "content": f"Sequential request {i+1}: What is {i+1} squared?"}],
            "max_tokens": 30,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            # Individual request - each one waits for the previous to complete
            request_start = time.time()
            response = await balancer.invoke_model(model_id, body, check_availability=False)
            request_time = time.time() - request_start
            
            results.append({
                'request_id': i + 1,
                'region': response['region'],
                'response_time': request_time,
                'success': True,
                'content': response['response']['content'][0]['text'][:50]
            })
            regions_used.append(response['region'])
            
            print(f"  Request {i+1:2d}: {response['region']:15s} ({request_time:.3f}s)")
            
        except Exception as e:
            results.append({
                'request_id': i + 1,
                'error': str(e),
                'success': False
            })
            print(f"  Request {i+1:2d}: ERROR - {str(e)}")
    
    total_time = time.time() - start_time
    
    # Analysis
    successful_requests = [r for r in results if r['success']]
    success_rate = len(successful_requests) / len(results) * 100
    
    if successful_requests:
        response_times = [r['response_time'] for r in successful_requests]
        avg_response_time = statistics.mean(response_times)
        
        # Region distribution
        region_counts = {}
        for region in regions_used:
            region_counts[region] = region_counts.get(region, 0) + 1
    else:
        avg_response_time = 0
        region_counts = {}
    
    print(f"\n📊 Sequential Processing Results:")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Success rate: {success_rate:.1f}% ({len(successful_requests)}/{len(results)})")
    if successful_requests:
        print(f"   Average response time: {avg_response_time:.3f}s")
        print(f"   Region distribution: {region_counts}")
    
    return {
        'total_time': total_time,
        'success_rate': success_rate,
        'avg_response_time': avg_response_time,
        'region_distribution': region_counts,
        'successful_requests': len(successful_requests)
    }


async def batch_processing_example(balancer, num_requests=10):
    """Demonstrate new batch processing with round-robin distribution."""
    print(f"\n=== Batch Processing ({num_requests} requests) ===")
    
    model_id = "claude-3.7-sonnet"
    
    # Prepare all requests
    batch_bodies = []
    for i in range(num_requests):
        body = {
            "messages": [{"role": "user", "content": f"Batch request {i+1}: What is {i+1} squared?"}],
            "max_tokens": 30,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        batch_bodies.append(body)
    
    start_time = time.time()
    
    try:
        # Single batch call - all requests processed in parallel with round-robin
        batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies, check_availability=False)
        
        total_time = time.time() - start_time
        
        results = []
        regions_used = []
        
        for i, response in enumerate(batch_responses):
            results.append({
                'request_id': i + 1,
                'region': response['region'],
                'success': True,
                'content': response['response']['content'][0]['text'][:50]
            })
            regions_used.append(response['region'])
            print(f"  Request {i+1:2d}: {response['region']:15s}")
        
        success_rate = 100.0
        
    except Exception as e:
        total_time = time.time() - start_time
        success_rate = 0.0
        regions_used = []
        results = []
        print(f"  ERROR: {str(e)}")
    
    # Analysis
    region_counts = {}
    for region in regions_used:
        region_counts[region] = region_counts.get(region, 0) + 1
    
    print(f"\n📊 Batch Processing Results:")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Success rate: {success_rate:.1f}% ({len(results)}/{num_requests})")
    if results:
        print(f"   Region distribution: {region_counts}")
        print(f"   Round-robin pattern: {regions_used}")
    
    return {
        'total_time': total_time,
        'success_rate': success_rate,
        'region_distribution': region_counts,
        'successful_requests': len(results),
        'round_robin_pattern': regions_used
    }


async def converse_api_comparison(balancer, num_requests=5):
    """Compare sequential vs batch processing using Converse API."""
    print(f"\n=== Converse API Comparison ({num_requests} requests) ===")
    
    model_id = "claude-3.7-sonnet"
    
    # Sequential converse processing
    print("\n--- Sequential Converse Processing ---")
    start_time = time.time()
    sequential_regions = []
    
    for i in range(num_requests):
        messages = [ConverseAPIHelper.create_message(
            MessageRole.USER, 
            f"Sequential converse {i+1}: Describe the color of number {i+1}."
        )]
        
        try:
            response = await balancer.converse_model(
                model_id=model_id,
                messages=messages,
                inference_config={"maxTokens": 30, "temperature": 0},
                check_availability=False
            )
            sequential_regions.append(response['region'])
            parsed = ConverseAPIHelper.parse_converse_response(response['response'])
            print(f"  Request {i+1}: {response['region']} - {parsed['content'][0]['text'][:40]}...")
            
        except Exception as e:
            print(f"  Request {i+1}: ERROR - {str(e)}")
    
    sequential_time = time.time() - start_time
    
    # Batch converse processing
    print("\n--- Batch Converse Processing ---")
    start_time = time.time()
    
    batch_message_lists = []
    for i in range(num_requests):
        messages = [ConverseAPIHelper.create_message(
            MessageRole.USER, 
            f"Batch converse {i+1}: Describe the color of number {i+1}."
        )]
        batch_message_lists.append(messages)
    
    try:
        batch_responses = await balancer.converse_model_batch(
            model_id=model_id,
            message_lists=batch_message_lists,
            inference_config={"maxTokens": 30, "temperature": 0},
            check_availability=False
        )
        
        batch_regions = []
        for i, response in enumerate(batch_responses):
            batch_regions.append(response['region'])
            parsed = ConverseAPIHelper.parse_converse_response(response['response'])
            print(f"  Request {i+1}: {response['region']} - {parsed['content'][0]['text'][:40]}...")
        
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        batch_regions = []
    
    batch_time = time.time() - start_time
    
    print(f"\n📊 Converse API Comparison:")
    print(f"   Sequential time: {sequential_time:.3f}s")
    print(f"   Batch time: {batch_time:.3f}s")
    if batch_time > 0:
        speedup = sequential_time / batch_time
        print(f"   Speedup: {speedup:.2f}x faster with batch processing")
    
    if sequential_regions and batch_regions:
        print(f"   Sequential regions: {sequential_regions}")
        print(f"   Batch regions: {batch_regions}")


async def load_test_comparison(balancer, request_counts=[5, 10, 20]):
    """Compare performance across different load levels."""
    print(f"\n=== Load Test Comparison ===")
    
    results = []
    
    for num_requests in request_counts:
        print(f"\n--- Testing with {num_requests} requests ---")
        
        # Sequential test
        sequential_result = await sequential_processing_example(balancer, num_requests)
        
        # Batch test
        batch_result = await batch_processing_example(balancer, num_requests)
        
        # Calculate speedup
        if batch_result['total_time'] > 0:
            speedup = sequential_result['total_time'] / batch_result['total_time']
        else:
            speedup = 0
        
        results.append({
            'num_requests': num_requests,
            'sequential_time': sequential_result['total_time'],
            'batch_time': batch_result['total_time'],
            'speedup': speedup,
            'sequential_success': sequential_result['successful_requests'],
            'batch_success': batch_result['successful_requests']
        })
        
        print(f"   📈 Speedup: {speedup:.2f}x faster with batch processing")
    
    # Summary table
    print(f"\n📋 Performance Summary:")
    print(f"{'Requests':<10} {'Sequential':<12} {'Batch':<10} {'Speedup':<10} {'Success Rate'}")
    print("-" * 55)
    
    for result in results:
        seq_success_rate = result['sequential_success'] / result['num_requests'] * 100
        batch_success_rate = result['batch_success'] / result['num_requests'] * 100
        
        print(f"{result['num_requests']:<10} "
              f"{result['sequential_time']:<12.3f} "
              f"{result['batch_time']:<10.3f} "
              f"{result['speedup']:<10.2f} "
              f"{seq_success_rate:.0f}% / {batch_success_rate:.0f}%")


async def memory_and_resource_comparison(balancer):
    """Compare memory and resource usage between sequential and batch processing."""
    print(f"\n=== Memory and Resource Comparison ===")
    
    print("\nResource efficiency analysis:")
    print("• Sequential processing:")
    print("  - Low memory usage (one request at a time)")
    print("  - High latency (network round-trips add up)")
    print("  - Simple error handling (fail fast)")
    print("  - Predictable load on API endpoints")
    
    print("\n• Batch processing:")
    print("  - Higher memory usage (multiple requests in memory)")
    print("  - Low latency (parallel execution)")
    print("  - Complex error handling (partial failures possible)")
    print("  - Distributed load across regions with round-robin")
    
    # Demonstrate with actual requests
    num_requests = 8
    model_id = "claude-3.7-sonnet"
    
    print(f"\nDemonstrating resource patterns with {num_requests} requests:")
    
    # Show round-robin distribution pattern
    batch_bodies = []
    for i in range(num_requests):
        body = {
            "messages": [{"role": "user", "content": f"Resource test {i+1}"}],
            "max_tokens": 10,
            "temperature": 0,
            "anthropic_version": "bedrock-2023-05-31"
        }
        batch_bodies.append(body)
    
    try:
        start_time = time.time()
        batch_responses = await balancer.invoke_model_batch(model_id, batch_bodies, check_availability=False)
        batch_time = time.time() - start_time
        
        regions_used = [response['region'] for response in batch_responses]
        
        print(f"\nBatch processing results:")
        print(f"  Total time: {batch_time:.3f}s")
        print(f"  Round-robin pattern: {regions_used}")
        
        # Show load distribution
        region_counts = {}
        for region in regions_used:
            region_counts[region] = region_counts.get(region, 0) + 1
        
        print(f"  Load distribution:")
        for region, count in sorted(region_counts.items()):
            percentage = count / len(regions_used) * 100
            print(f"    {region}: {count} requests ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"  Resource test failed: {e}")


async def error_handling_comparison(balancer):
    """Compare error handling between sequential and batch processing."""
    print(f"\n=== Error Handling Comparison ===")
    
    # Test with mixed valid and invalid requests
    print("\nTesting error scenarios:")
    
    valid_body = {
        "messages": [{"role": "user", "content": "Valid request"}],
        "max_tokens": 20,
        "temperature": 0,
        "anthropic_version": "bedrock-2023-05-31"
    }
    
    invalid_body = {
        "messages": [{"role": "user", "content": "Invalid request"}],
        "max_tokens": -1,  # Invalid parameter
        "temperature": 0,
        "anthropic_version": "bedrock-2023-05-31"
    }
    
    # Sequential error handling
    print("\n--- Sequential Error Handling ---")
    sequential_results = []
    
    for i, body in enumerate([valid_body, invalid_body, valid_body], 1):
        try:
            response = await balancer.invoke_model("claude-3.7-sonnet", body, check_availability=False)
            sequential_results.append(f"Request {i}: SUCCESS")
            print(f"  Request {i}: ✓ SUCCESS")
        except Exception as e:
            sequential_results.append(f"Request {i}: ERROR - {type(e).__name__}")
            print(f"  Request {i}: ✗ ERROR - {type(e).__name__}")
    
    # Batch error handling
    print("\n--- Batch Error Handling ---")
    mixed_bodies = [valid_body, invalid_body, valid_body]
    
    try:
        batch_responses = await balancer.invoke_model_batch("claude-3.7-sonnet", mixed_bodies, check_availability=False)
        print(f"  Batch processing: ✓ SUCCESS (some requests may have failed individually)")
        for i, response in enumerate(batch_responses, 1):
            if 'error' in response:
                print(f"    Request {i}: ✗ ERROR in batch")
            else:
                print(f"    Request {i}: ✓ SUCCESS in batch")
    except Exception as e:
        print(f"  Batch processing: ✗ COMPLETE FAILURE - {type(e).__name__}")
        print(f"    All requests failed due to batch-level error")
    
    print("\nError handling insights:")
    print("• Sequential: Fails fast, easy to identify which request failed")
    print("• Batch: Better resilience, but requires careful error handling design")
    print("• Recommendation: Use batch for performance, handle partial failures gracefully")


async def main():
    """Run comprehensive batch vs sequential comparison."""
    print("🚀 Bedrock Region Balancer - Batch vs Sequential Processing Comparison")
    print("=" * 80)
    print()
    print("This example compares the performance and behavior of:")
    print("• Sequential processing (traditional approach)")
    print("• Batch processing with round-robin distribution (new feature)")
    print()
    print("Key metrics analyzed:")
    print("• Total execution time")
    print("• Request success rates") 
    print("• Region distribution patterns")
    print("• Resource utilization")
    print("• Error handling behavior")
    print()
    
    try:
        async with BedrockRegionBalancer(
            default_model="claude-3.7-sonnet"
        ) as balancer:
            
            print("Available regions:", balancer.bedrock_client.get_available_regions())
            print()
            
            # Main comparison tests
            await load_test_comparison(balancer, request_counts=[5, 10])
            
            # Converse API comparison
            await converse_api_comparison(balancer, num_requests=5)
            
            # Resource analysis
            await memory_and_resource_comparison(balancer)
            
            # Error handling
            await error_handling_comparison(balancer)
            
    except Exception as e:
        print(f"\n❌ Error during comparison: {e}")
        print("\nNote: This example requires valid AWS credentials and access to Claude models.")
        print("Make sure you have configured your credentials via:")
        print("• .env file with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("• AWS credentials file")
        print("• IAM roles (if running on AWS infrastructure)")
    
    print("\n" + "=" * 80)
    print("🎯 Key Takeaways:")
    print()
    print("✅ Batch Processing Advantages:")
    print("   • 2-10x faster execution time")
    print("   • Automatic round-robin load distribution")
    print("   • Better resource utilization")
    print("   • Reduced network overhead")
    print()
    print("✅ Sequential Processing Advantages:")
    print("   • Lower memory usage")
    print("   • Simpler error handling")
    print("   • Fail-fast behavior")
    print("   • Easier debugging")
    print()
    print("🎯 When to use Batch Processing:")
    print("   • Multiple similar requests")
    print("   • Performance is critical")
    print("   • Load distribution needed")
    print("   • High-throughput scenarios")
    print()
    print("🎯 When to use Sequential Processing:")
    print("   • Memory constraints")
    print("   • Simple error handling requirements")
    print("   • Single request or very few requests")
    print("   • Interactive applications with immediate feedback")


if __name__ == "__main__":
    asyncio.run(main())