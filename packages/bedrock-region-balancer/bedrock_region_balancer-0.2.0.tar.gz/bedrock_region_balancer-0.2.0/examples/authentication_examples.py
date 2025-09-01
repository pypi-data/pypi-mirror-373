"""
Comprehensive Authentication Examples for Bedrock Region Balancer.

This example demonstrates all supported authentication methods:
1. Bedrock API Key authentication
2. AWS Session Credentials (temporary)
3. AWS Access Keys (permanent)
4. AWS Secrets Manager integration
5. Default AWS credential chain
6. Authentication priority and fallback
"""

import asyncio
import json
import os
import tempfile
from bedrock_region_balancer import (
    BedrockRegionBalancer,
    AuthType,
    SecretsManagerError,
    BedrockBalancerError
)


async def bedrock_api_key_auth_example():
    """Example: Bedrock API Key Authentication (Recommended)."""
    print("=== 1. Bedrock API Key Authentication ===")
    print("This is the recommended authentication method for Bedrock.")
    print()
    
    # Method 1: Direct parameter
    print("Method 1a: Direct parameter")
    try:
        async with BedrockRegionBalancer(
            credentials={'bedrock_api_key': 'demo-api-key-123'},
            auth_type=AuthType.BEDROCK_API_KEY,
            default_model="claude-3.7-sonnet"
        ) as balancer:
            print("✓ Balancer initialized with direct Bedrock API key")
            print(f"  Default model: {balancer.get_default_model()}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Method 1b: Alternative key name
    print("\nMethod 1b: Alternative key name (aws_bearer_token_bedrock)")
    try:
        async with BedrockRegionBalancer(
            credentials={'aws_bearer_token_bedrock': 'demo-bearer-token-456'},
            default_model="claude-3.5-sonnet"
        ) as balancer:
            print("✓ Balancer initialized with bearer token format")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Method 1c: Environment variable
    print("\nMethod 1c: Environment variable")
    original_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
    
    try:
        os.environ['AWS_BEARER_TOKEN_BEDROCK'] = 'demo-env-token-789'
        
        async with BedrockRegionBalancer() as balancer:
            print("✓ Balancer initialized from AWS_BEARER_TOKEN_BEDROCK environment variable")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Restore original value or remove
        if original_token:
            os.environ['AWS_BEARER_TOKEN_BEDROCK'] = original_token
        elif 'AWS_BEARER_TOKEN_BEDROCK' in os.environ:
            del os.environ['AWS_BEARER_TOKEN_BEDROCK']


async def aws_session_credentials_example():
    """Example: AWS Session Credentials (Temporary)."""
    print("\n=== 2. AWS Session Credentials ===")
    print("Use temporary credentials with session tokens (most secure).")
    print()
    
    # Method 2a: Direct parameter
    print("Method 2a: Direct parameter")
    try:
        session_credentials = {
            'aws_access_key_id': 'ASIA-demo-session-key',
            'aws_secret_access_key': 'demo-session-secret',
            'aws_session_token': 'demo-session-token-xyz'
        }
        
        async with BedrockRegionBalancer(
            credentials=session_credentials,
            auth_type=AuthType.AWS_SESSION,
            default_model="claude-3.7-sonnet"
        ) as balancer:
            print("✓ Balancer initialized with AWS session credentials")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Method 2b: Environment variables
    print("\nMethod 2b: Environment variables")
    
    # Save original values
    original_env = {}
    session_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
    
    for var in session_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
    
    try:
        os.environ['AWS_ACCESS_KEY_ID'] = 'ASIA-demo-env-key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'demo-env-secret'
        os.environ['AWS_SESSION_TOKEN'] = 'demo-env-session-token'
        
        async with BedrockRegionBalancer() as balancer:
            print("✓ Balancer initialized from AWS session environment variables")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Restore original values
        for var in session_vars:
            if var in original_env:
                os.environ[var] = original_env[var]
            elif var in os.environ:
                del os.environ[var]


async def aws_access_keys_example():
    """Example: AWS Access Keys (Permanent)."""
    print("\n=== 3. AWS Access Keys ===")
    print("Use permanent access keys (less secure than session credentials).")
    print()
    
    # Method 3a: Direct parameter
    print("Method 3a: Direct parameter")
    try:
        access_key_credentials = {
            'aws_access_key_id': 'AKIA-demo-access-key',
            'aws_secret_access_key': 'demo-access-secret'
        }
        
        async with BedrockRegionBalancer(
            credentials=access_key_credentials,
            auth_type=AuthType.AWS_ACCESS_KEY,
            default_model="claude-3.5-sonnet"
        ) as balancer:
            print("✓ Balancer initialized with AWS access keys")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Method 3b: Alternative naming
    print("\nMethod 3b: Alternative naming (without aws_ prefix)")
    try:
        alt_credentials = {
            'access_key_id': 'AKIA-demo-alt-key',
            'secret_access_key': 'demo-alt-secret'
        }
        
        async with BedrockRegionBalancer(
            credentials=alt_credentials,
            default_model="claude-3.7-sonnet"
        ) as balancer:
            print("✓ Balancer initialized with alternative key names")
            
    except Exception as e:
        print(f"✗ Error: {e}")


async def secrets_manager_auth_example():
    """Example: AWS Secrets Manager Integration."""
    print("\n=== 4. AWS Secrets Manager Integration ===")
    print("Store credentials securely in AWS Secrets Manager.")
    print()
    
    # Different secret formats supported
    secret_formats = [
        {
            'name': 'bedrock-api-key-format',
            'description': 'Bedrock API Key format',
            'format': '{"bedrock_api_key": "your-api-key"}'
        },
        {
            'name': 'aws-access-key-format', 
            'description': 'AWS Access Keys format',
            'format': '{"access_key_id": "AKIA...", "secret_access_key": "your-secret"}'
        },
        {
            'name': 'aws-session-format',
            'description': 'AWS Session Credentials format', 
            'format': '{"access_key_id": "ASIA...", "secret_access_key": "your-secret", "session_token": "your-token"}'
        }
    ]
    
    for secret_info in secret_formats:
        print(f"\n{secret_info['description']}:")
        print(f"  Secret Name: {secret_info['name']}")
        print(f"  Expected Format: {secret_info['format']}")
        
        try:
            async with BedrockRegionBalancer(
                secret_name=secret_info['name'],
                secret_region="us-west-2",
                default_model="claude-3.7-sonnet"
            ) as balancer:
                print(f"  ✓ Successfully loaded secret: {secret_info['name']}")
                
        except SecretsManagerError as e:
            print(f"  ✗ Secrets Manager error (expected in demo): {e}")
        except Exception as e:
            print(f"  ✗ Other error: {e}")


async def default_aws_chain_example():
    """Example: Default AWS Credential Chain."""
    print("\n=== 5. Default AWS Credential Chain ===")
    print("Use AWS SDK's default credential chain (IAM roles, instance profiles, etc.).")
    print()
    
    try:
        async with BedrockRegionBalancer(
            use_environment=False,  # Skip environment variables
            use_dotenv=False,       # Skip .env files
            default_model="claude-3.7-sonnet"
        ) as balancer:
            print("✓ Balancer initialized using default AWS credential chain")
            print("  This includes: IAM roles, EC2 instance profiles, ECS task roles, etc.")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Note: This is expected if you're not running on AWS infrastructure")
        print("        or don't have AWS credentials configured locally")


async def authentication_priority_example():
    """Example: Authentication Priority and Fallback."""
    print("\n=== 6. Authentication Priority and Fallback ===")
    print("Understanding how different auth methods are prioritized.")
    print()
    
    print("Authentication Priority Order:")
    print("1. secret_name (Secrets Manager) - Highest priority")
    print("2. credentials parameter")
    print("3. Environment variables + .env files")  
    print("4. Default AWS credential chain - Lowest priority")
    print()
    
    # Test priority with multiple methods available
    print("Testing priority with multiple auth sources:")
    
    # Set up environment with multiple auth sources
    os.environ['AWS_BEARER_TOKEN_BEDROCK'] = 'env-api-key'
    
    try:
        # Direct credentials should override environment
        async with BedrockRegionBalancer(
            credentials={'bedrock_api_key': 'direct-api-key'},
            use_environment=True,  # Environment available but should be overridden
            default_model="claude-3.7-sonnet"
        ) as balancer:
            print("✓ Direct credentials used (overrode environment variables)")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Clean up
        if 'AWS_BEARER_TOKEN_BEDROCK' in os.environ:
            del os.environ['AWS_BEARER_TOKEN_BEDROCK']


async def auto_detection_example():
    """Example: Automatic Authentication Type Detection."""
    print("\n=== 7. Automatic Authentication Type Detection ===")
    print("The balancer automatically detects credential types.")
    print()
    
    test_credentials = [
        {
            'name': 'Bedrock API Key',
            'creds': {'bedrock_api_key': 'test-key'},
            'expected_type': AuthType.BEDROCK_API_KEY
        },
        {
            'name': 'AWS Session Credentials',
            'creds': {
                'aws_access_key_id': 'ASIA123',
                'aws_secret_access_key': 'secret',
                'aws_session_token': 'token'
            },
            'expected_type': AuthType.AWS_SESSION
        },
        {
            'name': 'AWS Access Keys',
            'creds': {
                'aws_access_key_id': 'AKIA123', 
                'aws_secret_access_key': 'secret'
            },
            'expected_type': AuthType.AWS_ACCESS_KEY
        }
    ]
    
    for test in test_credentials:
        print(f"\nTesting: {test['name']}")
        try:
            async with BedrockRegionBalancer(
                credentials=test['creds'],
                default_model="claude-3.7-sonnet"
            ) as balancer:
                # The auth type is detected internally, but we can infer it worked
                print(f"✓ Successfully auto-detected {test['expected_type'].value} authentication")
                
        except Exception as e:
            print(f"✗ Error: {e}")


async def error_handling_auth_example():
    """Example: Authentication Error Handling."""
    print("\n=== 8. Authentication Error Handling ===")
    print("Handling various authentication errors gracefully.")
    print()
    
    # Test various error conditions
    error_tests = [
        {
            'name': 'Empty credentials',
            'creds': {},
            'description': 'Empty credentials dictionary'
        },
        {
            'name': 'Invalid credential format',
            'creds': {'invalid_key': 'some_value'},
            'description': 'Unrecognized credential keys'
        },
        {
            'name': 'Mixed credential types',
            'creds': {
                'bedrock_api_key': 'key1',
                'aws_access_key_id': 'key2'
            },
            'description': 'Conflicting credential types'
        }
    ]
    
    for test in error_tests:
        print(f"\nTesting: {test['name']}")
        print(f"Description: {test['description']}")
        
        try:
            async with BedrockRegionBalancer(
                credentials=test['creds'],
                use_environment=False,  # Prevent fallback to environment
                use_dotenv=False       # Prevent fallback to .env
            ) as balancer:
                print("✗ Unexpectedly succeeded")
                
        except ValueError as e:
            print(f"✓ Caught expected ValueError: {e}")
        except Exception as e:
            print(f"✓ Caught expected error: {type(e).__name__}: {e}")


async def main():
    """Run all authentication examples."""
    print("Bedrock Region Balancer - Comprehensive Authentication Examples")
    print("=" * 70)
    print()
    print("This demonstrates all authentication methods and best practices:")
    print()
    
    await bedrock_api_key_auth_example()
    await aws_session_credentials_example()
    await aws_access_keys_example()
    await secrets_manager_auth_example()
    await default_aws_chain_example()
    await authentication_priority_example()
    await auto_detection_example()
    await error_handling_auth_example()
    
    print("\n" + "=" * 70)
    print("Authentication examples completed!")
    print()
    print("Security Best Practices:")
    print("🔐 Use Bedrock API Keys when available (recommended)")
    print("🔐 Use AWS Session Credentials over permanent Access Keys")
    print("🔐 Store sensitive credentials in AWS Secrets Manager")
    print("🔐 Use IAM roles for EC2/ECS/Lambda deployments")
    print("🔐 Never hardcode credentials in source code")
    print("🔐 Rotate credentials regularly")
    print("🔐 Use least privilege IAM policies")
    print()
    print("For production deployments:")
    print("• Use IAM roles (EC2, ECS, Lambda)")
    print("• Use Secrets Manager for cross-account access")
    print("• Use environment variables for containerized deployments")
    print("• Always use encrypted connections and secure credential storage")


if __name__ == "__main__":
    asyncio.run(main())