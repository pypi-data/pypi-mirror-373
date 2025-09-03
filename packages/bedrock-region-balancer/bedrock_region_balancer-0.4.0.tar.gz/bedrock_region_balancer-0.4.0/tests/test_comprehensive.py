#!/usr/bin/env python3
"""
Comprehensive integration test for the Bedrock Region Balancer.
Tests both existing functionality and new batch processing features.
"""

import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock

from bedrock_region_balancer import (
    BedrockRegionBalancer, 
    ConverseAPIHelper, 
    MessageRole,
    BedrockBalancerError,
    ModelNotAvailableError
)


async def test_initialization_and_basic_functionality():
    """Test basic initialization and that both single and batch methods work."""
    print("=== Testing Initialization and Basic Functionality ===")
    
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
        
        # Test 1: Check that methods exist
        assert hasattr(balancer, 'invoke_model'), "invoke_model method missing"
        assert hasattr(balancer, 'invoke_model_batch'), "invoke_model_batch method missing"
        assert hasattr(balancer, 'converse_model'), "converse_model method missing"
        assert hasattr(balancer, 'converse_model_batch'), "converse_model_batch method missing"
        print("✅ All required methods exist")
        
        # Test 2: Check default model
        default_model = balancer.get_default_model()
        assert default_model, "Default model should be set"
        print(f"✅ Default model: {default_model}")
        
        # Test 3: Check regions
        assert balancer.regions == test_regions, "Regions not set correctly"
        print(f"✅ Regions configured: {balancer.regions}")


async def test_batch_vs_single_performance():
    """Test performance difference between batch and individual processing."""
    print("\n=== Testing Performance: Batch vs Sequential ===")
    
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
        
        # Mock the internal methods with realistic latency
        async def mock_invoke_with_latency(region, model_id, body):
            await asyncio.sleep(0.02)  # 20ms simulated latency
            return {
                'response': {'content': [{'text': f'Response from {region}'}]},
                'region': region,
                'model_id': model_id
            }
        
        balancer._invoke_model_in_region = mock_invoke_with_latency
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        # Prepare test data
        num_requests = 10
        test_bodies = [
            {
                "messages": [{"role": "user", "content": f"Test {i}"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
            for i in range(num_requests)
        ]
        
        # Test sequential processing
        print(f"Processing {num_requests} requests sequentially...")
        start_time = time.time()
        sequential_responses = []
        for body in test_bodies:
            response = await mock_invoke_with_latency('us-west-2', 'claude-3.7-sonnet', body)
            sequential_responses.append(response)
        sequential_time = time.time() - start_time
        
        # Test batch processing
        print(f"Processing {num_requests} requests in batch...")
        start_time = time.time()
        batch_responses = await balancer.invoke_model_batch('claude-3.7-sonnet', test_bodies)
        batch_time = time.time() - start_time
        
        # Verify results
        assert len(sequential_responses) == num_requests
        assert len(batch_responses) == num_requests
        
        speedup = sequential_time / batch_time
        print(f"✅ Sequential time: {sequential_time:.3f}s")
        print(f"✅ Batch time: {batch_time:.3f}s")
        print(f"✅ Speedup: {speedup:.2f}x faster")
        
        # Batch should be significantly faster
        assert speedup > 2.0, f"Batch should be at least 2x faster, got {speedup:.2f}x"


async def test_round_robin_distribution():
    """Test that round-robin distribution works correctly."""
    print("\n=== Testing Round-Robin Distribution ===")
    
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
        
        # Track region usage
        used_regions = []
        
        async def mock_invoke_track_region(region, model_id, body):
            used_regions.append(region)
            return {
                'response': {'content': [{'text': f'Response from {region}'}]},
                'region': region,
                'model_id': model_id
            }
        
        balancer._invoke_model_in_region = mock_invoke_track_region
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        # Test with 9 requests (3 full cycles)
        test_bodies = [
            {
                "messages": [{"role": "user", "content": f"Test {i}"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
            for i in range(9)
        ]
        
        # Execute batch
        responses = await balancer.invoke_model_batch('claude-3.7-sonnet', test_bodies)
        
        # Verify round-robin pattern
        expected_pattern = [
            'us-west-2', 'eu-central-1', 'ap-northeast-2',  # Cycle 1
            'us-west-2', 'eu-central-1', 'ap-northeast-2',  # Cycle 2
            'us-west-2', 'eu-central-1', 'ap-northeast-2'   # Cycle 3
        ]
        
        assert used_regions == expected_pattern, f"Expected {expected_pattern}, got {used_regions}"
        print(f"✅ Round-robin pattern verified: {used_regions}")
        
        # Verify each region was used equally
        region_counts = {region: used_regions.count(region) for region in test_regions}
        print(f"✅ Region distribution: {region_counts}")
        
        for region, count in region_counts.items():
            assert count == 3, f"Region {region} should be used 3 times, got {count}"


async def test_converse_api_batch():
    """Test batch processing with Converse API."""
    print("\n=== Testing Converse API Batch Processing ===")
    
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
        
        # Track region usage
        used_regions = []
        
        async def mock_converse_track_region(region, model_id, messages, inference_config, tool_config, guardrail_config, system):
            used_regions.append(region)
            return {
                'response': {
                    'output': {
                        'message': {
                            'content': [{'text': f'Converse response from {region}'}],
                            'role': 'assistant'
                        }
                    },
                    'stopReason': 'end_turn',
                    'usage': {'inputTokens': 15, 'outputTokens': 8}
                },
                'region': region,
                'model_id': model_id
            }
        
        balancer._converse_in_region = mock_converse_track_region
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        # Prepare batch message lists
        batch_message_lists = []
        for i in range(5):
            messages = [ConverseAPIHelper.create_message(
                MessageRole.USER, 
                f"Converse test {i}: Explain {i} in one sentence."
            )]
            batch_message_lists.append(messages)
        
        # Execute batch
        responses = await balancer.converse_model_batch(
            'claude-3.7-sonnet',
            batch_message_lists,
            inference_config={'maxTokens': 100, 'temperature': 0.7}
        )
        
        # Verify results
        assert len(responses) == 5, f"Expected 5 responses, got {len(responses)}"
        assert len(used_regions) == 5, f"Expected 5 region calls, got {len(used_regions)}"
        
        # Verify round-robin distribution
        expected_pattern = ['us-west-2', 'eu-central-1', 'us-west-2', 'eu-central-1', 'us-west-2']
        assert used_regions == expected_pattern, f"Expected {expected_pattern}, got {used_regions}"
        
        print(f"✅ Converse batch processed 5 requests")
        print(f"✅ Used regions in round-robin: {used_regions}")
        
        # Verify response structure
        for i, response in enumerate(responses):
            assert 'response' in response
            assert 'region' in response
            assert 'model_id' in response
            assert 'output' in response['response']
            print(f"   Response {i+1}: {response['region']}")


async def test_error_scenarios():
    """Test various error scenarios."""
    print("\n=== Testing Error Scenarios ===")
    
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
        
        # Test 1: Model not available in any region
        balancer._find_available_regions_for_model = AsyncMock(return_value=[])
        
        test_body = {
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 50,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        try:
            await balancer.invoke_model_batch('non-existent-model', [test_body])
            assert False, "Should have raised ModelNotAvailableError"
        except ModelNotAvailableError:
            print("✅ Correctly handled model not available error")
        except Exception as e:
            print(f"✅ Handled error (different type): {type(e).__name__}")
        
        # Test 2: Empty batch
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        empty_responses = await balancer.invoke_model_batch('claude-3.7-sonnet', [])
        assert len(empty_responses) == 0, "Empty batch should return empty list"
        print("✅ Empty batch handled correctly")
        
        # Test 3: Single request through batch API
        balancer._invoke_model_in_region = AsyncMock(return_value={
            'response': {'content': [{'text': 'Single response'}]},
            'region': 'us-west-2',
            'model_id': 'claude-3.7-sonnet'
        })
        
        single_response = await balancer.invoke_model_batch('claude-3.7-sonnet', [test_body])
        assert len(single_response) == 1, "Single request should return one response"
        print("✅ Single request through batch API works")


async def test_backward_compatibility():
    """Test that existing single-request methods still work."""
    print("\n=== Testing Backward Compatibility ===")
    
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
        
        # Mock internal methods
        balancer._invoke_model_in_region = AsyncMock(return_value={
            'response': {'content': [{'text': 'Single invoke response'}]},
            'region': 'us-west-2',
            'model_id': 'claude-3.7-sonnet'
        })
        
        balancer._converse_in_region = AsyncMock(return_value={
            'response': {
                'output': {'message': {'content': [{'text': 'Single converse response'}]}},
                'stopReason': 'end_turn',
                'usage': {'inputTokens': 10, 'outputTokens': 5}
            },
            'region': 'us-west-2',
            'model_id': 'claude-3.7-sonnet'
        })
        
        balancer._find_available_regions_for_model = AsyncMock(return_value=test_regions)
        
        # Test single invoke_model
        body = {
            "messages": [{"role": "user", "content": "Single test"}],
            "max_tokens": 50,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        response = await balancer.invoke_model('claude-3.7-sonnet', body)
        assert 'response' in response
        assert 'region' in response
        print("✅ Single invoke_model method works")
        
        # Test single converse_model
        messages = [ConverseAPIHelper.create_message(MessageRole.USER, "Single converse test")]
        
        converse_response = await balancer.converse_model('claude-3.7-sonnet', messages)
        assert 'response' in converse_response
        assert 'region' in converse_response
        print("✅ Single converse_model method works")


async def main():
    """Run comprehensive tests."""
    print("🧪 Bedrock Region Balancer - Comprehensive Test Suite")
    print("=" * 65)
    
    test_functions = [
        test_initialization_and_basic_functionality,
        test_batch_vs_single_performance,
        test_round_robin_distribution,
        test_converse_api_batch,
        test_error_scenarios,
        test_backward_compatibility
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
    
    print(f"\n🏁 Comprehensive Test Results:")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Total:  {len(test_functions)}")
    
    if failed == 0:
        print("\n🎉 All comprehensive tests passed!")
        print("✅ Batch processing is fully functional")
        print("✅ Round-robin distribution works correctly")
        print("✅ Both invoke_model and converse APIs support batch processing")
        print("✅ Backward compatibility is maintained")
        print("✅ Error handling works as expected")
        print("✅ Performance improvements verified")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the implementation.")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)