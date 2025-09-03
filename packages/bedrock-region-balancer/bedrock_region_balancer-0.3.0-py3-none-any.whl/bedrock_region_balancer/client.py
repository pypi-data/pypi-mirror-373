"""
Bedrock client management for multiple regions.
"""

import logging
from typing import Dict, Optional, List
import boto3
from botocore.exceptions import ClientError

from .exceptions import RegionNotAvailableError

logger = logging.getLogger(__name__)


class BedrockClient:
    """Manage Bedrock clients for multiple regions."""
    
    # Default regions for load balancing
    DEFAULT_REGIONS = ['us-west-2', 'eu-central-1', 'ap-northeast-2']
    
    # Default endpoints for each region
    DEFAULT_ENDPOINTS = {
        'us-west-2': {
            'bedrock': 'https://bedrock.us-west-2.amazonaws.com',
            'bedrock-runtime': 'https://bedrock-runtime.us-west-2.amazonaws.com'
        },
        'eu-central-1': {
            'bedrock': 'https://bedrock.eu-central-1.amazonaws.com',
            'bedrock-runtime': 'https://bedrock-runtime.eu-central-1.amazonaws.com'
        },
        'ap-northeast-2': {
            'bedrock': 'https://bedrock.ap-northeast-2.amazonaws.com',
            'bedrock-runtime': 'https://bedrock-runtime.ap-northeast-2.amazonaws.com'
        }
    }
    
    def __init__(self, credentials: Optional[Dict[str, str]] = None, 
                 regions: Optional[List[str]] = None,
                 endpoints: Optional[List[str]] = None):
        """
        Initialize Bedrock client manager.
        
        Args:
            credentials: AWS credentials dict (optional, uses default credential chain if not provided)
            regions: List of AWS regions to use (optional, uses DEFAULT_REGIONS if not provided)
            endpoints: List of endpoint URLs for each region (optional, uses default endpoints if not provided)
                      Must match the number of regions if provided
        """
        self.credentials = credentials
        self.regions = regions or self.DEFAULT_REGIONS
        
        # Set up endpoints - either from parameter or defaults
        if endpoints is not None:
            if len(endpoints) != len(self.regions):
                raise ValueError(f"Number of endpoints ({len(endpoints)}) must match number of regions ({len(self.regions)})")
            self.endpoints = dict(zip(self.regions, endpoints))
        else:
            self.endpoints = {}
        
        self._clients = {}
        self._runtime_clients = {}
        self._available_regions = set()
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Bedrock clients for all specified regions."""
        for region in self.regions:
            try:
                # Prepare client configuration
                client_config = {'region_name': region}
                runtime_client_config = {'region_name': region}
                
                # Add credentials if provided
                if self.credentials:
                    client_config.update(self.credentials)
                    runtime_client_config.update(self.credentials)
                
                # Add endpoint URL if provided in parameters
                if region in self.endpoints:
                    # If custom endpoint is provided, use it for both bedrock and bedrock-runtime
                    client_config['endpoint_url'] = self.endpoints[region]
                    runtime_client_config['endpoint_url'] = self.endpoints[region]
                elif region in self.DEFAULT_ENDPOINTS:
                    # Use default endpoints for bedrock and bedrock-runtime separately
                    client_config['endpoint_url'] = self.DEFAULT_ENDPOINTS[region]['bedrock']
                    runtime_client_config['endpoint_url'] = self.DEFAULT_ENDPOINTS[region]['bedrock-runtime']
                
                # Create bedrock client for model availability checking
                self._clients[region] = boto3.client('bedrock', **client_config)
                self._runtime_clients[region] = boto3.client('bedrock-runtime', **runtime_client_config)
                
                # Test the connection
                self._clients[region].list_foundation_models()
                self._available_regions.add(region)
                logger.info(f"Successfully initialized Bedrock client for region: {region}")
                
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock client for region {region}: {str(e)}")
    
    def get_available_regions(self) -> List[str]:
        """Get list of available regions."""
        return list(self._available_regions)
    
    def get_client(self, region: str):
        """
        Get Bedrock client for a specific region.
        
        Args:
            region: AWS region name
            
        Returns:
            Bedrock client
            
        Raises:
            RegionNotAvailableError: If region is not available
        """
        if region not in self._available_regions:
            raise RegionNotAvailableError(f"Region '{region}' is not available")
        return self._clients[region]
    
    def get_runtime_client(self, region: str):
        """
        Get Bedrock Runtime client for a specific region.
        
        Args:
            region: AWS region name
            
        Returns:
            Bedrock Runtime client
            
        Raises:
            RegionNotAvailableError: If region is not available
        """
        if region not in self._available_regions:
            raise RegionNotAvailableError(f"Region '{region}' is not available")
        return self._runtime_clients[region]
    
    def check_model_availability(self, model_id: str, region: str) -> bool:
        """
        Check if a model is available in a specific region.
        
        Args:
            model_id: Bedrock model ID (short name like 'claude-3.7-sonnet' or full ID)
            region: AWS region name
            
        Returns:
            True if model is available, False otherwise
        """
        if region not in self._available_regions:
            return False
        
        try:
            # Convert short name to actual model ID if needed
            actual_model_id = model_id
            try:
                # If it's a short name like "claude-3.7-sonnet", convert it
                if not model_id.startswith(('anthropic.', 'us.', 'eu.', 'apac.')):
                    from .model_mappings import get_model_id
                    actual_model_id = get_model_id(model_id, region)
            except ValueError:
                # If conversion fails, use the original model_id
                pass
            
            client = self.get_client(region)
            
            # Check if it's a Cross Region Inference profile ID
            if actual_model_id.startswith(('us.', 'eu.', 'apac.')):
                # For Cross Region Inference profiles, check via list_inference_profiles
                try:
                    response = client.list_inference_profiles()
                    for profile in response.get('inferenceProfileSummaries', []):
                        if profile.get('inferenceProfileId') == actual_model_id:
                            # Check if profile is active
                            if profile.get('status') == 'ACTIVE':
                                return True
                    
                    # Check with pagination if needed
                    while 'nextToken' in response:
                        response = client.list_inference_profiles(nextToken=response['nextToken'])
                        for profile in response.get('inferenceProfileSummaries', []):
                            if profile.get('inferenceProfileId') == actual_model_id:
                                if profile.get('status') == 'ACTIVE':
                                    return True
                    
                    return False
                    
                except Exception:
                    # If list_inference_profiles fails, fall back to foundation models check
                    pass
            
            # For regular model IDs, check foundation models
            response = client.list_foundation_models()
            
            for model in response.get('modelSummaries', []):
                if model.get('modelId') == actual_model_id:
                    # Check if model is active
                    if model.get('modelLifecycle', {}).get('status') == 'ACTIVE':
                        return True
                    
            # Check with pagination if needed
            while 'nextToken' in response:
                response = client.list_foundation_models(nextToken=response['nextToken'])
                for model in response.get('modelSummaries', []):
                    if model.get('modelId') == actual_model_id:
                        if model.get('modelLifecycle', {}).get('status') == 'ACTIVE':
                            return True
            
            return False
            
        except ClientError as e:
            logger.error(f"Error checking model availability in region {region}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking model availability: {str(e)}")
            return False
    
    def get_available_models_by_region(self) -> Dict[str, List[str]]:
        """
        Get all available models for each region.
        
        Returns:
            Dict mapping region to list of available model IDs
        """
        models_by_region = {}
        
        for region in self._available_regions:
            models = []
            try:
                client = self.get_client(region)
                response = client.list_foundation_models()
                
                for model in response.get('modelSummaries', []):
                    if model.get('modelLifecycle', {}).get('status') == 'ACTIVE':
                        models.append(model.get('modelId'))
                
                # Handle pagination
                while 'nextToken' in response:
                    response = client.list_foundation_models(nextToken=response['nextToken'])
                    for model in response.get('modelSummaries', []):
                        if model.get('modelLifecycle', {}).get('status') == 'ACTIVE':
                            models.append(model.get('modelId'))
                
                models_by_region[region] = models
                
            except Exception as e:
                logger.error(f"Error listing models for region {region}: {str(e)}")
                models_by_region[region] = []
        
        return models_by_region