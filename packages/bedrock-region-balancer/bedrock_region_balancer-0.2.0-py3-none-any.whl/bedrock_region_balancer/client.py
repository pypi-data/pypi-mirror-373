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
    
    def __init__(self, credentials: Optional[Dict[str, str]] = None, 
                 regions: Optional[List[str]] = None):
        """
        Initialize Bedrock client manager.
        
        Args:
            credentials: AWS credentials dict (optional, uses default credential chain if not provided)
            regions: List of AWS regions to use (optional, uses DEFAULT_REGIONS if not provided)
        """
        self.credentials = credentials
        self.regions = regions or self.DEFAULT_REGIONS
        self._clients = {}
        self._runtime_clients = {}
        self._available_regions = set()
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Bedrock clients for all specified regions."""
        for region in self.regions:
            try:
                # Create bedrock client for model availability checking
                if self.credentials:
                    self._clients[region] = boto3.client(
                        'bedrock',
                        region_name=region,
                        **self.credentials
                    )
                    self._runtime_clients[region] = boto3.client(
                        'bedrock-runtime',
                        region_name=region,
                        **self.credentials
                    )
                else:
                    self._clients[region] = boto3.client(
                        'bedrock',
                        region_name=region
                    )
                    self._runtime_clients[region] = boto3.client(
                        'bedrock-runtime',
                        region_name=region
                    )
                
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
            model_id: Bedrock model ID
            region: AWS region name
            
        Returns:
            True if model is available, False otherwise
        """
        if region not in self._available_regions:
            return False
        
        try:
            client = self.get_client(region)
            # List foundation models and check if our model is in the list
            response = client.list_foundation_models()
            
            for model in response.get('modelSummaries', []):
                if model.get('modelId') == model_id:
                    # Check if model is active
                    if model.get('modelLifecycle', {}).get('status') == 'ACTIVE':
                        return True
                    
            # Check with pagination if needed
            while 'nextToken' in response:
                response = client.list_foundation_models(nextToken=response['nextToken'])
                for model in response.get('modelSummaries', []):
                    if model.get('modelId') == model_id:
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