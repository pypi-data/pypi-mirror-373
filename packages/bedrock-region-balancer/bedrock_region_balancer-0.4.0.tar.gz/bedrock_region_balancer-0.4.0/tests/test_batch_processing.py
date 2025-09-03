#!/usr/bin/env python3
"""
Comprehensive test suite for batch processing functionality in Bedrock Region Balancer.
"""

import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from bedrock_region_balancer import BedrockRegionBalancer, ConverseAPIHelper, MessageRole


class TestBatchProcessing(unittest.TestCase):
    """Unit tests for batch processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_regions = ['us-west-2', 'eu-central-1', 'ap-northeast-2']
        self.test_model_id = 'claude-3.7-sonnet'
        self.mock_credentials = {
            'aws_access_key_id': 'test_key',
            'aws_secret_access_key': 'test_secret'
        }
    
    @patch('bedrock_region_balancer.balancer.BedrockClient')
    def test_balancer_initialization_with_batch_support(self, mock_bedrock_client):
        """Test that balancer initializes correctly with batch processing support."""
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = self.test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        balancer = BedrockRegionBalancer(
            credentials=self.mock_credentials,
            regions=self.test_regions
        )
        
        # Verify batch methods exist
        self.assertTrue(hasattr(balancer, 'invoke_model_batch'))
        self.assertTrue(hasattr(balancer, 'converse_model_batch'))
        self.assertTrue(callable(getattr(balancer, 'invoke_model_batch')))
        self.assertTrue(callable(getattr(balancer, 'converse_model_batch')))
    
    @patch('bedrock_region_balancer.balancer.BedrockClient')
    async def test_invoke_model_batch_round_robin_distribution(self, mock_bedrock_client):
        """Test that invoke_model_batch distributes requests across regions using round-robin."""
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = self.test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        balancer = BedrockRegionBalancer(
            credentials=self.mock_credentials,
            regions=self.test_regions
        )
        
        # Mock the _invoke_model_in_region method to track which regions are used
        used_regions = []
        
        async def mock_invoke_in_region(region, model_id, body):
            used_regions.append(region)
            return {
                'response': {'content': [{'text': f'Response from {region}'}]},
                'region': region,
                'model_id': model_id
            }
        
        balancer._invoke_model_in_region = mock_invoke_in_region
        balancer._find_available_regions_for_model = AsyncMock(return_value=self.test_regions)
        
        # Prepare batch bodies
        batch_bodies = [
            {
                "messages": [{"role": "user", "content": f"Request {i}"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
            for i in range(6)  # Test with 6 requests across 3 regions
        ]
        
        # Execute batch
        responses = await balancer.invoke_model_batch(self.test_model_id, batch_bodies)
        
        # Verify responses
        self.assertEqual(len(responses), 6)
        self.assertEqual(len(used_regions), 6)
        
        # Verify round-robin distribution: should cycle through regions
        expected_regions = [
            'us-west-2', 'eu-central-1', 'ap-northeast-2',  # First cycle
            'us-west-2', 'eu-central-1', 'ap-northeast-2'   # Second cycle
        ]
        self.assertEqual(used_regions, expected_regions)
    
    @patch('bedrock_region_balancer.balancer.BedrockClient')
    async def test_converse_model_batch_round_robin_distribution(self, mock_bedrock_client):
        """Test that converse_model_batch distributes requests across regions using round-robin."""
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = self.test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        balancer = BedrockRegionBalancer(
            credentials=self.mock_credentials,
            regions=self.test_regions
        )
        
        # Mock the _converse_in_region method to track which regions are used
        used_regions = []
        
        async def mock_converse_in_region(region, model_id, messages, inference_config, tool_config, guardrail_config, system):
            used_regions.append(region)
            return {
                'response': {
                    'output': {'message': {'content': [{'text': f'Response from {region}'}]}},
                    'stopReason': 'end_turn',
                    'usage': {'inputTokens': 10, 'outputTokens': 5}
                },
                'region': region,
                'model_id': model_id
            }
        
        balancer._converse_in_region = mock_converse_in_region
        balancer._find_available_regions_for_model = AsyncMock(return_value=self.test_regions)
        
        # Prepare batch message lists
        batch_message_lists = [
            [ConverseAPIHelper.create_message(MessageRole.USER, f"Converse request {i}")]
            for i in range(4)  # Test with 4 requests
        ]
        
        # Execute batch
        responses = await balancer.converse_model_batch(
            self.test_model_id, 
            batch_message_lists,
            inference_config={'maxTokens': 50}
        )
        
        # Verify responses
        self.assertEqual(len(responses), 4)
        self.assertEqual(len(used_regions), 4)
        
        # Verify round-robin distribution
        expected_regions = ['us-west-2', 'eu-central-1', 'ap-northeast-2', 'us-west-2']
        self.assertEqual(used_regions, expected_regions)
    
    @patch('bedrock_region_balancer.balancer.BedrockClient')
    async def test_batch_processing_error_handling(self, mock_bedrock_client):
        """Test error handling in batch processing."""
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = self.test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        balancer = BedrockRegionBalancer(
            credentials=self.mock_credentials,
            regions=self.test_regions
        )
        
        # Mock error scenarios
        balancer._find_available_regions_for_model = AsyncMock(return_value=[])  # No available regions
        
        batch_bodies = [
            {
                "messages": [{"role": "user", "content": "Test"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
        ]
        
        # Test with no available regions
        with self.assertRaises(Exception):
            await balancer.invoke_model_batch(self.test_model_id, batch_bodies)
    
    @patch('bedrock_region_balancer.balancer.BedrockClient')
    async def test_single_vs_batch_api_compatibility(self, mock_bedrock_client):
        """Test that single API methods now use batch processing internally."""
        # Mock the BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = self.test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        balancer = BedrockRegionBalancer(
            credentials=self.mock_credentials,
            regions=self.test_regions
        )
        
        # Mock batch method to verify it's called
        batch_call_count = 0
        original_invoke_model_batch = balancer.invoke_model_batch
        
        async def mock_invoke_model_batch(model_id, bodies, check_availability=True):
            nonlocal batch_call_count
            batch_call_count += 1
            # Simulate batch response
            return [{
                'response': {'content': [{'text': 'Test response'}]},
                'region': 'us-west-2',
                'model_id': model_id
            }]
        
        balancer.invoke_model_batch = mock_invoke_model_batch
        
        # Call single API method
        body = {
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 50,
            "anthropic_version": "bedrock-2023-05-31"
        }
        
        response = await balancer.invoke_model(self.test_model_id, body)
        
        # Verify that batch method was called
        self.assertEqual(batch_call_count, 1)
        self.assertIn('response', response)
        self.assertIn('region', response)
    
    def test_batch_method_signatures(self):
        """Test that batch methods have correct signatures."""
        from inspect import signature
        
        # Test invoke_model_batch signature
        sig_invoke = signature(BedrockRegionBalancer.invoke_model_batch)
        params_invoke = list(sig_invoke.parameters.keys())
        expected_invoke = ['self', 'model_id', 'bodies', 'check_availability']
        self.assertEqual(params_invoke, expected_invoke)
        
        # Test converse_model_batch signature
        sig_converse = signature(BedrockRegionBalancer.converse_model_batch)
        params_converse = list(sig_converse.parameters.keys())
        expected_converse = [
            'self', 'model_id', 'message_lists', 'inference_config', 
            'tool_config', 'guardrail_config', 'system', 'check_availability'
        ]
        self.assertEqual(params_converse, expected_converse)


class TestBatchProcessingIntegration(unittest.TestCase):
    """Integration tests for batch processing with mocked AWS responses."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_regions = ['us-west-2', 'eu-central-1']
        self.test_model_id = 'claude-3.7-sonnet'
        self.mock_credentials = {
            'aws_access_key_id': 'test_key',
            'aws_secret_access_key': 'test_secret'
        }
    
    @patch('bedrock_region_balancer.balancer.BedrockClient')
    @patch('bedrock_region_balancer.client.boto3')
    async def test_batch_invoke_model_with_mock_aws_response(self, mock_boto3, mock_bedrock_client):
        """Test batch invoke_model with mocked AWS responses."""
        # Mock BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = self.test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        # Mock runtime clients for each region
        mock_runtime_clients = {}
        for region in self.test_regions:
            mock_runtime = MagicMock()
            mock_runtime.invoke_model.return_value = {
                'body': MagicMock(),
                'ResponseMetadata': {'HTTPStatusCode': 200}
            }
            # Mock the response body
            mock_response_body = {
                'content': [{'text': f'Response from {region}'}],
                'usage': {'input_tokens': 10, 'output_tokens': 5}
            }
            mock_runtime.invoke_model.return_value['body'].read.return_value = json.dumps(mock_response_body).encode()
            mock_runtime_clients[region] = mock_runtime
        
        mock_client_instance.get_runtime_client.side_effect = lambda region: mock_runtime_clients[region]
        
        balancer = BedrockRegionBalancer(
            credentials=self.mock_credentials,
            regions=self.test_regions
        )
        
        # Mock model availability
        balancer._find_available_regions_for_model = AsyncMock(return_value=self.test_regions)
        
        # Prepare batch requests
        batch_bodies = [
            {
                "messages": [{"role": "user", "content": f"Test message {i}"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
            for i in range(3)
        ]
        
        # Execute batch
        responses = await balancer.invoke_model_batch(self.test_model_id, batch_bodies)
        
        # Verify results
        self.assertEqual(len(responses), 3)
        
        for i, response in enumerate(responses):
            self.assertIn('response', response)
            self.assertIn('region', response)
            self.assertIn('model_id', response)
            self.assertIn('content', response['response'])
        
        # Verify that different regions were used (round-robin)
        used_regions = [resp['region'] for resp in responses]
        self.assertIn('us-west-2', used_regions)
        self.assertIn('eu-central-1', used_regions)
    
    @patch('bedrock_region_balancer.balancer.BedrockClient')
    @patch('bedrock_region_balancer.client.boto3')
    async def test_batch_converse_with_mock_aws_response(self, mock_boto3, mock_bedrock_client):
        """Test batch converse API with mocked AWS responses."""
        # Mock BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = self.test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        # Mock runtime clients for each region
        mock_runtime_clients = {}
        for region in self.test_regions:
            mock_runtime = MagicMock()
            mock_converse_response = {
                'output': {
                    'message': {
                        'content': [{'text': f'Converse response from {region}'}],
                        'role': 'assistant'
                    }
                },
                'stopReason': 'end_turn',
                'usage': {'inputTokens': 15, 'outputTokens': 8},
                'ResponseMetadata': {'HTTPStatusCode': 200}
            }
            mock_runtime.converse.return_value = mock_converse_response
            mock_runtime_clients[region] = mock_runtime
        
        mock_client_instance.get_runtime_client.side_effect = lambda region: mock_runtime_clients[region]
        
        balancer = BedrockRegionBalancer(
            credentials=self.mock_credentials,
            regions=self.test_regions
        )
        
        # Mock model availability
        balancer._find_available_regions_for_model = AsyncMock(return_value=self.test_regions)
        
        # Prepare batch message lists
        batch_message_lists = [
            [ConverseAPIHelper.create_message(MessageRole.USER, f"Converse test {i}")]
            for i in range(4)
        ]
        
        # Execute batch
        responses = await balancer.converse_model_batch(
            self.test_model_id,
            batch_message_lists,
            inference_config={'maxTokens': 100, 'temperature': 0.7}
        )
        
        # Verify results
        self.assertEqual(len(responses), 4)
        
        for response in responses:
            self.assertIn('response', response)
            self.assertIn('region', response)
            self.assertIn('model_id', response)
            self.assertIn('output', response['response'])
            self.assertIn('stopReason', response['response'])
    
    @patch('bedrock_region_balancer.balancer.BedrockClient')
    async def test_performance_comparison_single_vs_batch(self, mock_bedrock_client):
        """Test performance difference between single and batch processing."""
        import time
        
        # Mock BedrockClient
        mock_client_instance = MagicMock()
        mock_client_instance.get_available_regions.return_value = self.test_regions
        mock_bedrock_client.return_value = mock_client_instance
        
        balancer = BedrockRegionBalancer(
            credentials=self.mock_credentials,
            regions=self.test_regions
        )
        
        # Mock methods with delays to simulate network latency
        async def mock_invoke_with_delay(region, model_id, body):
            await asyncio.sleep(0.1)  # Simulate 100ms latency
            return {
                'response': {'content': [{'text': f'Response from {region}'}]},
                'region': region,
                'model_id': model_id
            }
        
        balancer._invoke_model_in_region = mock_invoke_with_delay
        balancer._find_available_regions_for_model = AsyncMock(return_value=self.test_regions)
        
        # Test data
        test_bodies = [
            {
                "messages": [{"role": "user", "content": f"Request {i}"}],
                "max_tokens": 50,
                "anthropic_version": "bedrock-2023-05-31"
            }
            for i in range(5)
        ]
        
        # Test sequential processing (simulated)
        start_time = time.time()
        sequential_responses = []
        for body in test_bodies:
            response = await balancer.invoke_model(self.test_model_id, body)
            sequential_responses.append(response)
        sequential_time = time.time() - start_time
        
        # Test batch processing
        start_time = time.time()
        batch_responses = await balancer.invoke_model_batch(self.test_model_id, test_bodies)
        batch_time = time.time() - start_time
        
        # Verify results
        self.assertEqual(len(sequential_responses), 5)
        self.assertEqual(len(batch_responses), 5)
        
        # Batch should be faster (parallel execution)
        print(f"Sequential time: {sequential_time:.3f}s")
        print(f"Batch time: {batch_time:.3f}s")
        print(f"Speedup: {sequential_time / batch_time:.2f}x")
        
        # Due to parallel execution, batch should be significantly faster
        self.assertLess(batch_time, sequential_time * 0.8)  # At least 20% faster


# Async test runner helper
def run_async_test(test_func):
    """Helper function to run async tests."""
    return asyncio.get_event_loop().run_until_complete(test_func())


if __name__ == "__main__":
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add unit tests
    unit_test_methods = [
        'test_balancer_initialization_with_batch_support',
        'test_batch_method_signatures'
    ]
    
    for method in unit_test_methods:
        suite.addTest(TestBatchProcessing(method))
    
    # Add async unit tests
    async_unit_tests = [
        TestBatchProcessing().test_invoke_model_batch_round_robin_distribution,
        TestBatchProcessing().test_converse_model_batch_round_robin_distribution,
        TestBatchProcessing().test_batch_processing_error_handling,
        TestBatchProcessing().test_single_vs_batch_api_compatibility
    ]
    
    # Add async integration tests  
    async_integration_tests = [
        TestBatchProcessingIntegration().test_batch_invoke_model_with_mock_aws_response,
        TestBatchProcessingIntegration().test_batch_converse_with_mock_aws_response,
        TestBatchProcessingIntegration().test_performance_comparison_single_vs_batch
    ]
    
    print("🧪 Running Bedrock Region Balancer Batch Processing Tests")
    print("=" * 60)
    
    # Run synchronous tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run asynchronous tests
    print("\n🔄 Running Async Unit Tests...")
    for i, test in enumerate(async_unit_tests, 1):
        try:
            print(f"\nTest {i}: {test.__name__}")
            run_async_test(test)
            print("✅ PASSED")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print("\n🔄 Running Async Integration Tests...")
    for i, test in enumerate(async_integration_tests, 1):
        try:
            print(f"\nIntegration Test {i}: {test.__name__}")
            run_async_test(test)
            print("✅ PASSED")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print(f"\n🏁 Test Summary:")
    print(f"Synchronous Tests: {result.testsRun} run, {len(result.failures)} failures, {len(result.errors)} errors")
    print(f"Asynchronous Tests: {len(async_unit_tests + async_integration_tests)} run")
    
    if result.wasSuccessful():
        print("🎉 All synchronous tests passed!")
    else:
        print("⚠️  Some synchronous tests failed!")