"""
AWS Secrets Manager integration for retrieving Bedrock API credentials.
"""

import json
import logging
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

from .exceptions import SecretsManagerError
from .auth_types import AuthType, CredentialManager

logger = logging.getLogger(__name__)


class SecretsManager:
    """Handle AWS Secrets Manager operations for Bedrock credentials."""
    
    def __init__(self, region_name: str = 'us-west-2'):
        """
        Initialize Secrets Manager client.
        
        Args:
            region_name: AWS region for Secrets Manager (default: us-west-2)
        """
        self.region_name = region_name
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of Secrets Manager client."""
        if self._client is None:
            self._client = boto3.client('secretsmanager', region_name=self.region_name)
        return self._client
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """
        Retrieve secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name of the secret in AWS Secrets Manager
            
        Returns:
            Dict containing the secret values
            
        Raises:
            SecretsManagerError: If unable to retrieve secret
        """
        try:
            logger.debug(f"Retrieving secret: {secret_name}")
            response = self.client.get_secret_value(SecretId=secret_name)
            
            # Parse the secret string
            if 'SecretString' in response:
                secret = response['SecretString']
                try:
                    return json.loads(secret)
                except json.JSONDecodeError:
                    # If not JSON, return as dict with 'value' key
                    return {'value': secret}
            else:
                # Binary secret
                raise SecretsManagerError("Binary secrets are not supported")
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ResourceNotFoundException':
                raise SecretsManagerError(f"Secret '{secret_name}' not found")
            elif error_code == 'InvalidRequestException':
                raise SecretsManagerError(f"Invalid request for secret '{secret_name}'")
            elif error_code == 'InvalidParameterException':
                raise SecretsManagerError(f"Invalid parameter for secret '{secret_name}'")
            elif error_code == 'DecryptionFailure':
                raise SecretsManagerError(f"Cannot decrypt secret '{secret_name}'")
            elif error_code == 'InternalServiceError':
                raise SecretsManagerError("AWS Secrets Manager internal error")
            else:
                raise SecretsManagerError(f"Error retrieving secret: {str(e)}")
        except Exception as e:
            raise SecretsManagerError(f"Unexpected error retrieving secret: {str(e)}")
    
    def get_bedrock_credentials(self, secret_name: str) -> Dict[str, str]:
        """
        Retrieve Bedrock credentials from Secrets Manager.
        
        Supports multiple credential formats:
        
        1. Bedrock API Key:
        {
            "bedrock_api_key": "your-api-key"
        }
        or
        {
            "aws_bearer_token_bedrock": "your-api-key"
        }
        
        2. AWS Access Keys:
        {
            "access_key_id": "...",
            "secret_access_key": "..."
        }
        or
        {
            "aws_access_key_id": "...",
            "aws_secret_access_key": "..."
        }
        
        3. AWS Session Credentials:
        {
            "access_key_id": "...",
            "secret_access_key": "...",
            "session_token": "..."
        }
        
        Args:
            secret_name: Name of the secret containing Bedrock credentials
            
        Returns:
            Dict with normalized credentials
            
        Raises:
            SecretsManagerError: If credentials are invalid or missing
        """
        secret = self.get_secret(secret_name)
        
        try:
            # Auto-detect credential type
            auth_type = CredentialManager.detect_auth_type(secret)
            
            # Validate credentials
            if not CredentialManager.validate_credentials(secret, auth_type):
                raise SecretsManagerError(f"Invalid credentials for detected auth type: {auth_type.value}")
            
            logger.info(f"Detected {auth_type.value} credentials in Secrets Manager")
            
            # Return raw credentials (will be normalized by CredentialManager later)
            return secret
            
        except ValueError as e:
            raise SecretsManagerError(f"Invalid credential format in secret '{secret_name}': {str(e)}")
    
    def get_legacy_bedrock_credentials(self, secret_name: str) -> Dict[str, str]:
        """
        Legacy method for backward compatibility.
        Retrieve AWS access key credentials from Secrets Manager.
        
        Expected format:
        {
            "access_key_id": "...",
            "secret_access_key": "...",
            "session_token": "..." (optional)
        }
        
        Args:
            secret_name: Name of the secret containing AWS credentials
            
        Returns:
            Dict with AWS credentials in boto3 format
            
        Raises:
            SecretsManagerError: If credentials are invalid or missing
        """
        secret = self.get_secret(secret_name)
        
        # Validate required fields
        required_fields = ['access_key_id', 'secret_access_key']
        missing_fields = [field for field in required_fields if field not in secret]
        
        if missing_fields:
            raise SecretsManagerError(
                f"Missing required credential fields: {', '.join(missing_fields)}"
            )
        
        # Extract credentials
        credentials = {
            'aws_access_key_id': secret['access_key_id'],
            'aws_secret_access_key': secret['secret_access_key']
        }
        
        # Add optional session token if present
        if 'session_token' in secret:
            credentials['aws_session_token'] = secret['session_token']
        
        return credentials