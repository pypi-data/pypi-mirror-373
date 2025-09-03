"""
Authentication types and credential handling for Bedrock Region Balancer.
"""

from enum import Enum
from typing import Dict, Any, Optional
import os
import logging

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


class AuthType(Enum):
    """Supported authentication types."""
    AWS_SESSION = "aws_session"           # access_key_id, secret_access_key, session_token
    AWS_ACCESS_KEY = "aws_access_key"     # access_key_id, secret_access_key
    BEDROCK_API_KEY = "bedrock_api_key"   # AWS_BEARER_TOKEN_BEDROCK


class CredentialManager:
    """Manage different types of AWS credentials."""
    
    @staticmethod
    def detect_auth_type(credentials: Dict[str, Any]) -> AuthType:
        """
        Auto-detect authentication type based on provided credentials.
        
        Args:
            credentials: Dictionary containing credential information
            
        Returns:
            Detected AuthType
            
        Raises:
            ValueError: If credentials format is not recognized
        """
        if not credentials:
            raise ValueError("Credentials dictionary cannot be empty")
            
        # Check for Bedrock API key (various key names)
        if any(key in credentials for key in ['bedrock_api_key', 'aws_bearer_token_bedrock', 'api_key']):
            return AuthType.BEDROCK_API_KEY
            
        # Check for AWS credentials
        if 'aws_access_key_id' in credentials and 'aws_secret_access_key' in credentials:
            if 'aws_session_token' in credentials:
                return AuthType.AWS_SESSION
            else:
                return AuthType.AWS_ACCESS_KEY
                
        # Check alternative key names
        if 'access_key_id' in credentials and 'secret_access_key' in credentials:
            if 'session_token' in credentials:
                return AuthType.AWS_SESSION
            else:
                return AuthType.AWS_ACCESS_KEY
                
        raise ValueError(
            "Unrecognized credential format. Expected one of: "
            "1) {'bedrock_api_key': '...'} or {'aws_bearer_token_bedrock': '...'} "
            "2) {'aws_access_key_id': '...', 'aws_secret_access_key': '...'} "
            "3) {'aws_access_key_id': '...', 'aws_secret_access_key': '...', 'aws_session_token': '...'}"
        )
    
    @staticmethod
    def normalize_credentials(credentials: Dict[str, Any], auth_type: AuthType) -> Dict[str, str]:
        """
        Normalize credentials to standard boto3 format.
        
        Args:
            credentials: Raw credential dictionary
            auth_type: Type of authentication
            
        Returns:
            Normalized credentials for boto3
        """
        if auth_type == AuthType.BEDROCK_API_KEY:
            # For Bedrock API key, we need to set it as a bearer token
            # This will be handled by setting the environment variable AWS_BEARER_TOKEN_BEDROCK
            api_key = (credentials.get('bedrock_api_key') or 
                      credentials.get('aws_bearer_token_bedrock') or 
                      credentials.get('api_key'))
            
            if not api_key:
                raise ValueError("API key not found in credentials")
            
            # Set environment variable for Bedrock API key authentication
            os.environ['AWS_BEARER_TOKEN_BEDROCK'] = api_key
            
            # Return empty dict as boto3 will use the environment variable
            return {}
            
        elif auth_type == AuthType.AWS_SESSION:
            return {
                'aws_access_key_id': credentials.get('aws_access_key_id') or credentials.get('access_key_id', ''),
                'aws_secret_access_key': credentials.get('aws_secret_access_key') or credentials.get('secret_access_key', ''),
                'aws_session_token': credentials.get('aws_session_token') or credentials.get('session_token', '')
            }
            
        elif auth_type == AuthType.AWS_ACCESS_KEY:
            return {
                'aws_access_key_id': credentials.get('aws_access_key_id') or credentials.get('access_key_id', ''),
                'aws_secret_access_key': credentials.get('aws_secret_access_key') or credentials.get('secret_access_key', '')
            }
        
        raise ValueError(f"Unsupported auth type: {auth_type}")
    
    @staticmethod
    def load_from_environment(dotenv_path: Optional[str] = None, use_dotenv: bool = True) -> Optional[Dict[str, str]]:
        """
        Load credentials from environment variables and optionally .env files.
        
        Environment variable precedence:
        1. AWS_BEARER_TOKEN_BEDROCK (official Bedrock API key env var)
        2. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY + AWS_SESSION_TOKEN (if present)
        3. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY
        
        Args:
            dotenv_path: Path to .env file (optional, defaults to .env in current directory)
            use_dotenv: Whether to load .env file (default: True)
        
        Returns:
            Credentials dictionary or None if not found
        """
        # Load .env file if available and requested
        if use_dotenv and DOTENV_AVAILABLE:
            try:
                if dotenv_path:
                    load_dotenv(dotenv_path)
                    logger.info(f"Loaded environment variables from {dotenv_path}")
                else:
                    # Try to find .env file in current directory and parent directories
                    if load_dotenv(verbose=False):
                        logger.info("Loaded environment variables from .env file")
            except Exception as e:
                logger.warning(f"Failed to load .env file: {str(e)}")
        elif use_dotenv and not DOTENV_AVAILABLE:
            logger.warning("python-dotenv not available. Install with: pip install python-dotenv")
        # Check for Bedrock API key first (AWS_BEARER_TOKEN_BEDROCK is the official env var)
        bedrock_api_key = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
        if bedrock_api_key:
            logger.info("Using Bedrock API key from environment")
            return {'aws_bearer_token_bedrock': bedrock_api_key}
        
        # Check for AWS credentials
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        
        if aws_access_key_id and aws_secret_access_key:
            credentials = {
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            }
            
            if aws_session_token:
                credentials['aws_session_token'] = aws_session_token
                logger.info("Using AWS session credentials from environment")
            else:
                logger.info("Using AWS access key credentials from environment")
                
            return credentials
        
        logger.info("No credentials found in environment variables")
        return None
    
    @staticmethod
    def validate_credentials(credentials: Dict[str, str], auth_type: AuthType) -> bool:
        """
        Validate that credentials contain required fields.
        
        Args:
            credentials: Credential dictionary
            auth_type: Authentication type
            
        Returns:
            True if valid, False otherwise
        """
        if auth_type == AuthType.BEDROCK_API_KEY:
            return any(key in credentials and credentials[key] 
                      for key in ['bedrock_api_key', 'aws_bearer_token_bedrock', 'api_key'])
            
        elif auth_type == AuthType.AWS_SESSION:
            required_fields = ['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']
            return all(field in credentials and credentials[field] for field in required_fields)
            
        elif auth_type == AuthType.AWS_ACCESS_KEY:
            required_fields = ['aws_access_key_id', 'aws_secret_access_key']
            return all(field in credentials and credentials[field] for field in required_fields)
            
        return False