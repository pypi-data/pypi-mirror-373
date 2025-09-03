#!/usr/bin/env python3
"""
Simple test for batch processing functionality without external dependencies.
Tests the new batch processing features with mocked responses.
"""

import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

# Import the modules we need to test
from bedrock_region_balancer import BedrockRegionBalancer, ConverseAPIHelper, MessageRole


async def test_batch_methods_exist():
    """Test that batch processing methods exist and are callable."""
    print("=== Testing Batch Method Existence ===")
    
    # Check if batch methods exist
    assert hasattr(BedrockRegionBalancer, 'invoke_model_batch'), "invoke_model_batch method missing"
    assert hasattr(BedrockRegionBalancer, 'converse_model_batch'), "converse_model_batch method missing"
    
    # Check if methods are callable
    assert callable(getattr(BedrockRegionBalancer, 'invoke_model_batch')), "invoke_model_batch not callable"
    assert callable(getattr(BedrockRegionBalancer, 'converse_model_batch')), "converse_model_batch not callable"
    
    print("✅ All batch methods exist and are callable")


async def test_batch_invoke_model_mock():
    """Test batch invoke_model with mocked responses."""
    print("\n=== Testing Batch invoke_model (Mocked) ===")
    
    # Mock credentials
    mock_credentials = {
        'aws_access_key_id': 'test_key',
        'aws_secret_access_key': 'test_secret'
    }
    
    test_regions = ['us-west-2', 'eu-central-1', 'ap-northeast-2']
    
    with patch('bedrock_region_balancer.balancer.BedrockClient') as mock_bedrock_client:
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        # Create balancer
        balancer = BedrockRegionBalancer(
            credentials=mock_credentials,
            regions=test_regions
        )
        
        # Track which regions are used
        used_regions = []
        
        # Mock the internal method that makes the actual API call
        async def mock_invoke_in_region(region, model_id, body):
            used_regions.append(region)
            return {
                'response': {
                    'content': [{'text': f'Mock response from {region}'}],
                    'usage': {'input_tokens': 10, 'output_tokens': 5}
                },
                'region': region,
                'model_id': model_id,
                'response_metadata': {'HTTPStatusCode': 200}
            }
        
        # Replace the method with our mock
        balancer._invoke_model_in_region = mock_invoke_in_region
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        # Prepare batch data
        batch_bodies = []
        for i in range(5):
            body = {
                "messages": [{"role": "user", "content": f"Batch request {i+1}"}],
                "max_tokens": 50,
                "temperature": 0.7,
                "anthropic_version": "bedrock-2023-05-31"
            }
            batch_bodies.append(body)
        
        # Execute batch processing
        print(f"Sending {len(batch_bodies)} requests in batch...")
        start_time = time.time()
        
        responses = await balancer.invoke_model_batch('claude-3.7-sonnet', batch_bodies)
        
        elapsed_time = time.time() - start_time
        
        # Verify results
        print(f"✅ Batch completed in {elapsed_time:.3f}s")
        print(f"✅ Received {len(responses)} responses")
        print(f"✅ Used regions: {used_regions}")
        
        # Check round-robin distribution
        expected_pattern = ['us-west-2', 'eu-central-1', 'ap-northeast-2', 'us-west-2', 'eu-central-1']
        assert used_regions == expected_pattern, f"Expected {expected_pattern}, got {used_regions}"
        print("✅ Round-robin distribution working correctly")
        
        # Verify response structure
        for i, response in enumerate(responses):
            assert 'response' in response
            assert 'region' in response
            assert 'model_id' in response
            assert response['response']['content'][0]['text'].startswith('Mock response from')
            print(f"   Response {i+1}: {response['region']} -> {response['response']['content'][0]['text']}")


async def test_batch_converse_model_mock():
    """Test batch converse_model with mocked responses."""
    print("\n=== Testing Batch converse_model (Mocked) ===")
    
    # Mock credentials
    mock_credentials = {
        'aws_access_key_id': 'test_key',
        'aws_secret_access_key': 'test_secret'
    }
    
    test_regions = ['us-west-2', 'eu-central-1']
    
    with patch('bedrock_region_balancer.balancer.BedrockClient') as mock_bedrock_client:
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        # Create balancer
        balancer = BedrockRegionBalancer(
            credentials=mock_credentials,
            regions=test_regions
        )
        
        # Track which regions are used
        used_regions = []
        
        # Mock the internal converse method
        async def mock_converse_in_region(region, model_id, messages, inference_config, tool_config, guardrail_config, system):
            used_regions.append(region)
            return {
                'response': {
                    'output': {
                        'message': {
                            'content': [{'text': f'Mock converse response from {region}'}],
                            'role': 'assistant'
                        }
                    },
                    'stopReason': 'end_turn',
                    'usage': {'inputTokens': 15, 'outputTokens': 8}
                },
                'region': region,
                'model_id': model_id,
                'response_metadata': {'HTTPStatusCode': 200}
            }
        
        # Replace the method with our mock
        balancer._converse_in_region = mock_converse_in_region
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        # Prepare batch message lists
        batch_message_lists = []
        for i in range(4):
            messages = [ConverseAPIHelper.create_message(
                MessageRole.USER, 
                f"Converse batch request {i+1}: What is {i+1} + {i+1}?"
            )]
            batch_message_lists.append(messages)
        
        # Execute batch processing
        print(f"Sending {len(batch_message_lists)} converse requests in batch...")
        start_time = time.time()
        
        responses = await balancer.converse_model_batch(
            'claude-3.7-sonnet',
            batch_message_lists,
            inference_config={'maxTokens': 100, 'temperature': 0.5}
        )
        
        elapsed_time = time.time() - start_time
        
        # Verify results
        print(f"✅ Converse batch completed in {elapsed_time:.3f}s")
        print(f"✅ Received {len(responses)} responses")
        print(f"✅ Used regions: {used_regions}")
        
        # Check round-robin distribution
        expected_pattern = ['us-west-2', 'eu-central-1', 'us-west-2', 'eu-central-1']
        assert used_regions == expected_pattern, f"Expected {expected_pattern}, got {used_regions}"
        print("✅ Round-robin distribution working correctly")
        
        # Verify response structure
        for i, response in enumerate(responses):
            assert 'response' in response
            assert 'region' in response
            assert 'model_id' in response
            assert 'output' in response['response']
            assert 'stopReason' in response['response']
            content = response['response']['output']['message']['content'][0]['text']
            print(f"   Response {i+1}: {response['region']} -> {content}")


async def test_single_vs_batch_compatibility():
    """Test that single methods use batch processing internally."""
    print("\n=== Testing Single vs Batch API Compatibility ===")
    
    # Mock credentials
    mock_credentials = {
        'aws_access_key_id': 'test_key',
        'aws_secret_access_key': 'test_secret'
    }
    
    test_regions = ['us-west-2']
    
    with patch('bedrock_region_balancer.balancer.BedrockClient') as mock_bedrock_client:
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        # Create balancer
        balancer = BedrockRegionBalancer(
            credentials=mock_credentials,
            regions=test_regions
        )
        
        # Track batch method calls
        batch_invoke_calls = []
        batch_converse_calls = []
        
        # Mock batch methods to track calls
        original_invoke_batch = balancer.invoke_model_batch
        original_converse_batch = balancer.converse_model_batch
        
        async def mock_invoke_batch(model_id, bodies, check_availability=True):
            batch_invoke_calls.append((model_id, len(bodies), check_availability))
            return [{
                'response': {'content': [{'text': 'Single method test response'}]},
                'region': 'us-west-2',
                'model_id': model_id
            }]
        
        async def mock_converse_batch(model_id, message_lists, inference_config=None, tool_config=None, 
                                    guardrail_config=None, system=None, check_availability=True):
            batch_converse_calls.append((model_id, len(message_lists), check_availability))
            return [{
                'response': {
                    'output': {'message': {'content': [{'text': 'Single converse test response'}]}},
                    'stopReason': 'end_turn',
                    'usage': {'inputTokens': 10, 'outputTokens': 5}
                },
                'region': 'us-west-2',
                'model_id': model_id
            }]
        
        balancer.invoke_model_batch = mock_invoke_batch
        balancer.converse_model_batch = mock_converse_batch
        
        # Test single invoke_model method
        body = {
            "messages": [{"role": "user", "content": "Single test"}],
            "max_tokens": 50,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        response = await balancer.invoke_model('claude-3.7-sonnet', body)
        
        # Verify single method used batch internally
        assert len(batch_invoke_calls) == 1, "invoke_model should call invoke_model_batch once"
        assert batch_invoke_calls[0][1] == 1, "invoke_model should call batch with 1 item"
        print("✅ invoke_model method uses batch processing internally")
        
        # Test single converse_model method
        messages = [ConverseAPIHelper.create_message(MessageRole.USER, "Single converse test")]
        
        converse_response = await balancer.converse_model('claude-3.7-sonnet', messages)
        
        # Verify single method used batch internally
        assert len(batch_converse_calls) == 1, "converse_model should call converse_model_batch once"
        assert batch_converse_calls[0][1] == 1, "converse_model should call batch with 1 item"
        print("✅ converse_model method uses batch processing internally")


async def test_performance_simulation():
    """Simulate performance comparison between sequential and batch processing."""
    print("\n=== Performance Simulation ===")
    
    # Mock credentials
    mock_credentials = {
        'aws_access_key_id': 'test_key',
        'aws_secret_access_key': 'test_secret'
    }
    
    test_regions = ['us-west-2', 'eu-central-1', 'ap-northeast-2']
    
    with patch('bedrock_region_balancer.balancer.BedrockClient') as mock_bedrock_client:
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        # Create balancer
        balancer = BedrockRegionBalancer(
            credentials=mock_credentials,
            regions=test_regions
        )
        
        # Mock with simulated latency
        async def mock_invoke_with_latency(region, model_id, body):
            await asyncio.sleep(0.05)  # Simulate 50ms network latency
            return {
                'response': {'content': [{'text': f'Response from {region}'}]},
                'region': region,
                'model_id': model_id
            }
        
        balancer._invoke_model_in_region = mock_invoke_with_latency
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        # Prepare test data
        num_requests = 6
        test_bodies = [
            {
                "messages": [{"role": "user", "content": f"Perf test {i}"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
            for i in range(num_requests)
        ]
        
        # Test sequential processing (simulate old behavior)
        print(f"Testing sequential processing with {num_requests} requests...")
        start_time = time.time()
        sequential_responses = []
        for body in test_bodies:
            # Temporarily bypass batch processing to simulate sequential
            response = await mock_invoke_with_latency('us-west-2', 'claude-3.7-sonnet', body)
            sequential_responses.append(response)
        sequential_time = time.time() - start_time
        
        # Test batch processing
        print(f"Testing batch processing with {num_requests} requests...")
        start_time = time.time()
        batch_responses = await balancer.invoke_model_batch('claude-3.7-sonnet', test_bodies)
        batch_time = time.time() - start_time
        
        # Results
        print(f"\n📊 Performance Comparison:")
        print(f"   Sequential: {sequential_time:.3f}s ({num_requests} requests)")
        print(f"   Batch:      {batch_time:.3f}s ({num_requests} requests)")
        print(f"   Speedup:    {sequential_time / batch_time:.2f}x faster")
        
        # Batch should be significantly faster due to parallel execution
        assert batch_time < sequential_time, "Batch processing should be faster than sequential"
        print("✅ Batch processing is faster than sequential processing")


async def test_error_handling():
    """Test error handling in batch processing."""
    print("\n=== Testing Error Handling ===")
    
    # Mock credentials
    mock_credentials = {
        'aws_access_key_id': 'test_key',
        'aws_secret_access_key': 'test_secret'
    }
    
    test_regions = ['us-west-2']
    
    with patch('bedrock_region_balancer.balancer.BedrockClient') as mock_bedrock_client:
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        # Create balancer
        balancer = BedrockRegionBalancer(
            credentials=mock_credentials,
            regions=test_regions
        )
        
        # Test 1: No available regions for model
        balancer._find_available_regions_for_model = AsyncMock(return_value=[])
        
        batch_bodies = [
            {
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
        ]
        
        try:
            await balancer.invoke_model_batch('non-existent-model', batch_bodies)
            assert False, "Should have raised an exception"
        except Exception as e:
            print(f"✅ Correctly handled error for unavailable model: {type(e).__name__}")
        
        # Test 2: Empty batch
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        empty_responses = await balancer.invoke_model_batch('claude-3.7-sonnet', [])
        assert len(empty_responses) == 0, "Empty batch should return empty responses"
        print("✅ Correctly handled empty batch")


async def main():
    """Run all batch processing tests."""
    print("🧪 Bedrock Region Balancer - Batch Processing Tests")
    print("=" * 60)
    
    test_functions = [
        test_batch_methods_exist,
        test_batch_invoke_model_mock,
        test_batch_converse_model_mock,
        test_single_vs_batch_compatibility,
        test_performance_simulation,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            print(f"\n🔄 Running {test_func.__name__}...")
            await test_func()
            passed += 1
            print(f"✅ {test_func.__name__} PASSED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🏁 Test Results:")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Total:  {len(test_functions)}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Batch processing is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the implementation.")


if __name__ == "__main__":
    asyncio.run(main())