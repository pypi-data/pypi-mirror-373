"""
Main load balancer implementation for AWS Bedrock across multiple regions.
"""

import asyncio
import logging
import time
import os
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import json

from .client import BedrockClient
from .exceptions import (
    BedrockBalancerError,
    ModelNotAvailableError,
    RegionNotAvailableError,
    SecretsManagerError
)
from .model_mappings import get_model_id, DEFAULT_MODEL
from .secrets_manager import SecretsManager
from .auth_types import AuthType, CredentialManager
from .converse_api import ConverseAPIHelper, APIMethod

logger = logging.getLogger(__name__)


class BedrockRegionBalancer:
    """
    Load balancer for AWS Bedrock API calls across multiple regions.
    
    Implements round-robin algorithm with async execution for distributing
    API calls across us-west-2, eu-central-1, and ap-northeast-2.
    """
    
    def __init__(self, 
                 credentials: Optional[Dict[str, str]] = None,
                 regions: Optional[List[str]] = None,
                 max_workers: int = 10,
                 secret_name: Optional[str] = None,
                 secret_region: str = 'us-west-2',
                 default_model: str = DEFAULT_MODEL,
                 auth_type: Optional[AuthType] = None,
                 use_environment: bool = True,
                 dotenv_path: Optional[str] = None,
                 use_dotenv: bool = True):
        """
        Initialize Bedrock Region Balancer.
        
        Args:
            credentials: Direct credentials dictionary (optional)
                - For AWS Session: {'aws_access_key_id': '...', 'aws_secret_access_key': '...', 'aws_session_token': '...'}
                - For AWS Access Key: {'aws_access_key_id': '...', 'aws_secret_access_key': '...'}
                - For Bedrock API Key: {'bedrock_api_key': '...'}
            regions: List of regions to use (default from BEDROCK_REGIONS env var or us-west-2, eu-central-1, ap-northeast-2)
            max_workers: Maximum number of worker threads for async execution
            secret_name: Name of secret in AWS Secrets Manager (optional, cannot use with credentials)
            secret_region: AWS region where secret is stored (default: us-west-2)
            default_model: Default model to use (default: claude-3.7-sonnet)
            auth_type: Force specific authentication type (optional, auto-detected if not provided)
            use_environment: Whether to check environment variables for credentials (default: True)
            dotenv_path: Path to .env file (optional, defaults to .env in current directory)
            use_dotenv: Whether to load .env file (default: True)
        """
        # Get regions from environment variable or use defaults
        if regions is None:
            env_regions = os.environ.get('BEDROCK_REGIONS', '')
            if env_regions:
                self.regions = [r.strip() for r in env_regions.split(',') if r.strip()]
            else:
                self.regions = ['us-west-2', 'eu-central-1', 'ap-northeast-2']
        else:
            self.regions = regions
            
        self.max_workers = max_workers
        self.default_model = default_model
        
        # Initialize credentials with priority order:
        # 1. Secrets Manager (if secret_name provided)
        # 2. Direct credentials parameter
        # 3. Environment variables (if use_environment=True)
        # 4. Default AWS credential chain
        
        if secret_name and credentials:
            raise ValueError("Cannot specify both 'secret_name' and 'credentials'. Choose one method.")
        
        raw_credentials = None
        credential_source = "default_aws_chain"
        
        if secret_name:
            # Load from Secrets Manager
            try:
                secrets_manager = SecretsManager(region_name=secret_region)
                raw_credentials = secrets_manager.get_bedrock_credentials(secret_name)
                credential_source = f"secrets_manager:{secret_name}"
                logger.info(f"Successfully loaded credentials from Secrets Manager: {secret_name}")
            except Exception as e:
                raise SecretsManagerError(f"Failed to load credentials from Secrets Manager: {str(e)}")
        elif credentials:
            # Use provided credentials
            raw_credentials = credentials
            credential_source = "direct_parameter"
        elif use_environment:
            # Try to load from environment variables and .env file
            env_credentials = CredentialManager.load_from_environment(
                dotenv_path=dotenv_path,
                use_dotenv=use_dotenv
            )
            if env_credentials:
                raw_credentials = env_credentials
                credential_source = "environment_variables" + (".env_file" if use_dotenv else "")
                
        # Process and normalize credentials
        if raw_credentials:
            # Detect or use specified auth type
            detected_auth_type = auth_type or CredentialManager.detect_auth_type(raw_credentials)
            
            # Validate credentials
            if not CredentialManager.validate_credentials(raw_credentials, detected_auth_type):
                raise ValueError(f"Invalid credentials for auth type: {detected_auth_type.value}")
            
            # Normalize credentials for boto3
            self._credentials = CredentialManager.normalize_credentials(raw_credentials, detected_auth_type)
            self._auth_type = detected_auth_type
            
            logger.info(f"Using {detected_auth_type.value} authentication from {credential_source}")
        else:
            # No explicit credentials provided, use default AWS credential chain
            self._credentials = None
            self._auth_type = None
            logger.info("Using default AWS credential chain")
        
        # Initialize Bedrock client
        self.bedrock_client = BedrockClient(
            credentials=self._credentials,
            regions=self.regions
        )
        
        # Round-robin state
        self._current_region_index = 0
        self._lock = asyncio.Lock()
        
        # Model availability cache (TTL: 5 minutes)
        self._model_cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Thread pool for async execution
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Verify at least one region is available
        available_regions = self.bedrock_client.get_available_regions()
        if not available_regions:
            raise BedrockBalancerError("No regions are available for Bedrock")
        
        logger.info(f"Initialized Bedrock balancer with regions: {available_regions}")
    
    async def _get_next_region(self) -> str:
        """Get next region using round-robin algorithm."""
        async with self._lock:
            available_regions = self.bedrock_client.get_available_regions()
            if not available_regions:
                raise RegionNotAvailableError("No regions available")
            
            # Ensure index is within bounds
            self._current_region_index = self._current_region_index % len(available_regions)
            region = available_regions[self._current_region_index]
            
            # Move to next region for next call
            self._current_region_index = (self._current_region_index + 1) % len(available_regions)
            
            return region
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self._model_cache:
            return False
        
        cache_entry = self._model_cache[cache_key]
        return (time.time() - cache_entry['timestamp']) < self._cache_ttl
    
    async def _check_model_availability_cached(self, model_id: str, region: str) -> bool:
        """Check model availability with caching."""
        cache_key = f"{model_id}:{region}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self._model_cache[cache_key]['available']
        
        # Check availability
        loop = asyncio.get_event_loop()
        available = await loop.run_in_executor(
            self._executor,
            self.bedrock_client.check_model_availability,
            model_id,
            region
        )
        
        # Update cache
        self._model_cache[cache_key] = {
            'available': available,
            'timestamp': time.time()
        }
        
        return available
    
    async def _find_available_regions_for_model(self, model_id: str) -> List[str]:
        """Find all regions where a model is available."""
        available_regions = self.bedrock_client.get_available_regions()
        
        # Check all regions in parallel
        tasks = []
        for region in available_regions:
            task = self._check_model_availability_cached(model_id, region)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Return regions where model is available
        return [region for region, available in zip(available_regions, results) if available]
    
    async def _invoke_model_in_region(self, region: str, model_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke model in a specific region."""
        loop = asyncio.get_event_loop()
        
        def _invoke():
            runtime_client = self.bedrock_client.get_runtime_client(region)
            
            # Check if model_id is a short name and convert to region-specific ID
            actual_model_id = model_id
            try:
                # If it's a short name like "claude-3.7-sonnet", convert it
                if not model_id.startswith('anthropic.'):
                    actual_model_id = get_model_id(model_id, region)
            except ValueError:
                # If conversion fails, use the original model_id
                pass
            
            # Convert body to JSON if needed
            if isinstance(body, dict):
                body_json = json.dumps(body)
            else:
                body_json = body
            
            # Invoke model
            response = runtime_client.invoke_model(
                modelId=actual_model_id,
                body=body_json,
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            return {
                'response': response_body,
                'region': region,
                'model_id': actual_model_id,
                'response_metadata': response.get('ResponseMetadata', {})
            }
        
        return await loop.run_in_executor(self._executor, _invoke)
    
    async def _converse_in_region(self, region: str, model_id: str, 
                                messages: List[Dict[str, Any]], 
                                inference_config: Optional[Dict[str, Any]] = None,
                                tool_config: Optional[Dict[str, Any]] = None,
                                guardrail_config: Optional[Dict[str, Any]] = None,
                                system: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Converse with model in a specific region using Converse API."""
        loop = asyncio.get_event_loop()
        
        def _converse():
            runtime_client = self.bedrock_client.get_runtime_client(region)
            
            # Check if model_id is a short name and convert to region-specific ID
            actual_model_id = model_id
            try:
                # If it's a short name like "claude-3.7-sonnet", convert it
                if not model_id.startswith('anthropic.'):
                    actual_model_id = get_model_id(model_id, region)
            except ValueError:
                # If conversion fails, use the original model_id
                pass
            
            # Build converse request
            converse_request = {
                'modelId': actual_model_id,
                'messages': messages
            }
            
            # Add optional configurations
            if inference_config:
                converse_request['inferenceConfig'] = inference_config
            if tool_config:
                converse_request['toolConfig'] = tool_config
            if guardrail_config:
                converse_request['guardrailConfig'] = guardrail_config
            if system:
                converse_request['system'] = system
            
            # Call Converse API
            response = runtime_client.converse(**converse_request)
            
            return {
                'response': response,
                'region': region,
                'model_id': actual_model_id,
                'response_metadata': response.get('ResponseMetadata', {})
            }
        
        return await loop.run_in_executor(self._executor, _converse)
    
    async def invoke_model(self, model_id: str, body: Dict[str, Any], 
                          check_availability: bool = True) -> Dict[str, Any]:
        """
        Invoke Bedrock model using round-robin load balancing.
        
        Args:
            model_id: Bedrock model ID
            body: Request body for model invocation
            check_availability: Whether to check model availability before invocation
            
        Returns:
            Dict containing model response and metadata
            
        Raises:
            ModelNotAvailableError: If model is not available in any region
            BedrockBalancerError: For other errors
        """
        results = await self.invoke_model_batch(model_id, [body], check_availability)
        return results[0]
    
    async def invoke_model_batch(self, model_id: str, bodies: List[Dict[str, Any]], 
                                check_availability: bool = True) -> List[Dict[str, Any]]:
        """
        Invoke Bedrock model with multiple messages using round-robin load balancing.
        Each message is sent to a different region using round-robin distribution.
        
        Args:
            model_id: Bedrock model ID
            bodies: List of request bodies for model invocation
            check_availability: Whether to check model availability before invocation
            
        Returns:
            List of Dict containing model responses and metadata (same order as input)
            
        Raises:
            ModelNotAvailableError: If model is not available in any region
            BedrockBalancerError: For other errors
        """
        try:
            if check_availability:
                # Find regions where model is available
                available_regions = await self._find_available_regions_for_model(model_id)
                if not available_regions:
                    raise ModelNotAvailableError(
                        f"Model '{model_id}' is not available in any of the configured regions"
                    )
                
                # Update bedrock client to only use available regions for this request
                original_regions = self.bedrock_client.get_available_regions()
                available_set = set(available_regions) & set(original_regions)
                
                if not available_set:
                    raise ModelNotAvailableError(
                        f"Model '{model_id}' is not available in any accessible region"
                    )
            
            # Create tasks for parallel execution using round-robin distribution
            tasks = []
            regions_used = []
            
            for body in bodies:
                # Get next region using round-robin
                region = await self._get_next_region()
                
                # If checking availability, ensure selected region has the model
                if check_availability:
                    # Find a region that has the model starting from current round-robin position
                    attempts = 0
                    max_attempts = len(self.bedrock_client.get_available_regions())
                    
                    while region not in available_regions and attempts < max_attempts:
                        region = await self._get_next_region()
                        attempts += 1
                    
                    if region not in available_regions:
                        raise ModelNotAvailableError(
                            f"Could not find available region for model '{model_id}'"
                        )
                
                # Create task for this message
                task = self._invoke_model_in_region(region, model_id, body)
                tasks.append(task)
                regions_used.append(region)
            
            # Execute all tasks in parallel
            logger.info(f"Invoking model '{model_id}' with {len(bodies)} messages across regions: {regions_used}")
            results = await asyncio.gather(*tasks)
            
            return results
            
        except Exception as e:
            logger.error(f"Error invoking model batch: {str(e)}")
            raise
    
    async def invoke_model_all_regions(self, model_id: str, body: Dict[str, Any],
                                     check_availability: bool = True) -> List[Dict[str, Any]]:
        """
        Invoke model in all available regions simultaneously.
        
        Args:
            model_id: Bedrock model ID
            body: Request body for model invocation
            check_availability: Whether to check model availability before invocation
            
        Returns:
            List of responses from all regions
        """
        # Find available regions for model
        if check_availability:
            available_regions = await self._find_available_regions_for_model(model_id)
            if not available_regions:
                raise ModelNotAvailableError(
                    f"Model '{model_id}' is not available in any region"
                )
        else:
            available_regions = self.bedrock_client.get_available_regions()
        
        # Invoke model in all regions simultaneously
        tasks = []
        for region in available_regions:
            task = self._invoke_model_in_region(region, model_id, body)
            tasks.append(task)
        
        # Gather results, handling individual failures
        results = []
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for region, response in zip(available_regions, responses):
            if isinstance(response, Exception):
                logger.error(f"Failed to invoke model in region {region}: {str(response)}")
                results.append({
                    'error': str(response),
                    'region': region,
                    'model_id': model_id
                })
            else:
                results.append(response)
        
        return results
    
    async def converse_model(self, model_id: str, 
                           messages: List[Dict[str, Any]],
                           inference_config: Optional[Dict[str, Any]] = None,
                           tool_config: Optional[Dict[str, Any]] = None,
                           guardrail_config: Optional[Dict[str, Any]] = None,
                           system: Optional[List[Dict[str, str]]] = None,
                           check_availability: bool = True) -> Dict[str, Any]:
        """
        Converse with Bedrock model using Converse API and round-robin load balancing.
        
        Args:
            model_id: Bedrock model ID
            messages: List of message objects for conversation
            inference_config: Inference configuration (temperature, max_tokens, etc.)
            tool_config: Tool configuration for function calling
            guardrail_config: Guardrail configuration
            system: System prompts
            check_availability: Whether to check model availability before invocation
            
        Returns:
            Dict containing model response and metadata
            
        Raises:
            ModelNotAvailableError: If model is not available in any region
            BedrockBalancerError: For other errors
        """
        results = await self.converse_model_batch(
            model_id, [messages], inference_config, tool_config, 
            guardrail_config, system, check_availability
        )
        return results[0]
    
    async def converse_model_batch(self, model_id: str, 
                                  message_lists: List[List[Dict[str, Any]]],
                                  inference_config: Optional[Dict[str, Any]] = None,
                                  tool_config: Optional[Dict[str, Any]] = None,
                                  guardrail_config: Optional[Dict[str, Any]] = None,
                                  system: Optional[List[Dict[str, str]]] = None,
                                  check_availability: bool = True) -> List[Dict[str, Any]]:
        """
        Converse with Bedrock model with multiple message lists using round-robin load balancing.
        Each message list is sent to a different region using round-robin distribution.
        
        Args:
            model_id: Bedrock model ID
            message_lists: List of message lists for conversations
            inference_config: Inference configuration (temperature, max_tokens, etc.)
            tool_config: Tool configuration for function calling
            guardrail_config: Guardrail configuration
            system: System prompts
            check_availability: Whether to check model availability before invocation
            
        Returns:
            List of Dict containing model responses and metadata (same order as input)
            
        Raises:
            ModelNotAvailableError: If model is not available in any region
            BedrockBalancerError: For other errors
        """
        try:
            if check_availability:
                # Find regions where model is available
                available_regions = await self._find_available_regions_for_model(model_id)
                if not available_regions:
                    raise ModelNotAvailableError(
                        f"Model '{model_id}' is not available in any of the configured regions"
                    )
                
                # Update bedrock client to only use available regions for this request
                original_regions = self.bedrock_client.get_available_regions()
                available_set = set(available_regions) & set(original_regions)
                
                if not available_set:
                    raise ModelNotAvailableError(
                        f"Model '{model_id}' is not available in any accessible region"
                    )
            
            # Create tasks for parallel execution using round-robin distribution
            tasks = []
            regions_used = []
            
            for messages in message_lists:
                # Get next region using round-robin
                region = await self._get_next_region()
                
                # If checking availability, ensure selected region has the model
                if check_availability:
                    # Find a region that has the model starting from current round-robin position
                    attempts = 0
                    max_attempts = len(self.bedrock_client.get_available_regions())
                    
                    while region not in available_regions and attempts < max_attempts:
                        region = await self._get_next_region()
                        attempts += 1
                    
                    if region not in available_regions:
                        raise ModelNotAvailableError(
                            f"Could not find available region for model '{model_id}'"
                        )
                
                # Create task for this message list
                task = self._converse_in_region(
                    region, model_id, messages, inference_config, 
                    tool_config, guardrail_config, system
                )
                tasks.append(task)
                regions_used.append(region)
            
            # Execute all tasks in parallel
            logger.info(f"Conversing with model '{model_id}' with {len(message_lists)} message lists across regions: {regions_used}")
            results = await asyncio.gather(*tasks)
            
            return results
            
        except Exception as e:
            logger.error(f"Error conversing with model batch: {str(e)}")
            raise
    
    async def converse_model_all_regions(self, model_id: str,
                                       messages: List[Dict[str, Any]],
                                       inference_config: Optional[Dict[str, Any]] = None,
                                       tool_config: Optional[Dict[str, Any]] = None,
                                       guardrail_config: Optional[Dict[str, Any]] = None,
                                       system: Optional[List[Dict[str, str]]] = None,
                                       check_availability: bool = True) -> List[Dict[str, Any]]:
        """
        Converse with model in all available regions simultaneously using Converse API.
        
        Args:
            model_id: Bedrock model ID
            messages: List of message objects for conversation
            inference_config: Inference configuration (temperature, max_tokens, etc.)
            tool_config: Tool configuration for function calling
            guardrail_config: Guardrail configuration
            system: System prompts
            check_availability: Whether to check model availability before invocation
            
        Returns:
            List of responses from all regions
        """
        # Find available regions for model
        if check_availability:
            available_regions = await self._find_available_regions_for_model(model_id)
            if not available_regions:
                raise ModelNotAvailableError(
                    f"Model '{model_id}' is not available in any region"
                )
        else:
            available_regions = self.bedrock_client.get_available_regions()
        
        # Converse with model in all regions simultaneously
        tasks = []
        for region in available_regions:
            task = self._converse_in_region(
                region, model_id, messages, inference_config,
                tool_config, guardrail_config, system
            )
            tasks.append(task)
        
        # Gather results, handling individual failures
        results = []
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for region, response in zip(available_regions, responses):
            if isinstance(response, Exception):
                logger.error(f"Failed to converse with model in region {region}: {str(response)}")
                results.append({
                    'error': str(response),
                    'region': region,
                    'model_id': model_id
                })
            else:
                results.append(response)
        
        return results
    
    def get_model_availability_report(self) -> Dict[str, Any]:
        """
        Get a report of model availability across all regions.
        
        Returns:
            Dict with availability information
        """
        return {
            'regions': self.regions,
            'available_regions': self.bedrock_client.get_available_regions(),
            'models_by_region': self.bedrock_client.get_available_models_by_region(),
            'cache_ttl_seconds': self._cache_ttl,
            'current_region_index': self._current_region_index,
            'default_model': self.default_model
        }
    
    def get_default_model(self) -> str:
        """
        Get the default model configured for this balancer.
        
        Returns:
            The default model name
        """
        return self.default_model
    
    def close(self):
        """Clean up resources."""
        self._executor.shutdown(wait=True)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        _ = exc_type, exc_val, exc_tb  # Suppress unused parameter warnings
        self.close()