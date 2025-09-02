"""
.env File Usage Examples for Bedrock Region Balancer.

This example demonstrates different ways to use .env files for configuration
and authentication with the Bedrock Region Balancer.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from bedrock_region_balancer import BedrockRegionBalancer, AuthType


async def basic_dotenv_example():
    """Example using default .env file in current directory."""
    print("=== Basic .env File Example ===")
    print("Looking for .env file in current directory...")
    
    if os.path.exists('.env'):
        print("✓ Found .env file")
        
        async with BedrockRegionBalancer(use_dotenv=True) as balancer:
            # Show loaded configuration
            report = balancer.get_model_availability_report()
            print(f"Default model: {report['default_model']}")
            print(f"Regions: {report['regions']}")
            
            # Test with a simple request
            model_id = balancer.get_default_model()
            body = {
                "messages": [{"role": "user", "content": "Hello from .env!"}],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            try:
                response = await balancer.invoke_model(model_id, body)
                print(f"✓ Success! Response from {response['region']}")
            except Exception as e:
                print(f"✗ Error: {e}")
                
    else:
        print("✗ No .env file found")
        print("Copy .env.example to .env and configure your credentials")


async def custom_dotenv_path_example():
    """Example using custom .env file path."""
    print("\n=== Custom .env File Path Example ===")
    
    # Create a temporary .env file for demonstration
    env_content = """
# Temporary .env file for testing
AWS_BEARER_TOKEN_BEDROCK=demo-api-key
BEDROCK_REGIONS=us-west-2,eu-central-1
DEFAULT_MODEL=claude-3.5-sonnet
MAX_WORKERS=5
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(env_content.strip())
        temp_env_path = f.name
    
    try:
        print(f"Created temporary .env file at: {temp_env_path}")
        
        async with BedrockRegionBalancer(
            dotenv_path=temp_env_path,
            use_dotenv=True
        ) as balancer:
            
            report = balancer.get_model_availability_report()
            print(f"✓ Loaded configuration from custom path")
            print(f"  Default model: {report['default_model']}")
            print(f"  Regions: {report['regions']}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Clean up temporary file
        os.unlink(temp_env_path)
        print("Cleaned up temporary file")


async def environment_specific_example():
    """Example using environment-specific .env files."""
    print("\n=== Environment-Specific .env Files Example ===")
    
    environments = ['development', 'staging', 'production']
    
    for env in environments:
        env_file = f".env.{env}"
        print(f"\nChecking for {env_file}...")
        
        if os.path.exists(env_file):
            print(f"✓ Found {env_file}")
            
            try:
                async with BedrockRegionBalancer(
                    dotenv_path=env_file,
                    use_dotenv=True
                ) as balancer:
                    
                    report = balancer.get_model_availability_report()
                    print(f"  Environment: {env}")
                    print(f"  Default model: {report['default_model']}")
                    print(f"  Regions: {report['regions']}")
                    
            except Exception as e:
                print(f"✗ Error loading {env_file}: {e}")
        else:
            print(f"✗ {env_file} not found")
            
            # Create example file for reference
            example_content = f"""
# Example {env_file} configuration
# Copy and modify for your {env} environment

# Authentication (choose one)
AWS_BEARER_TOKEN_BEDROCK=your-{env}-api-key
# AWS_ACCESS_KEY_ID=your-{env}-access-key
# AWS_SECRET_ACCESS_KEY=your-{env}-secret-key

# Configuration
BEDROCK_REGIONS=us-west-2,eu-central-1,ap-northeast-2
DEFAULT_MODEL=claude-3.7-sonnet
MAX_WORKERS={5 if env == 'development' else 20}
"""
            
            print(f"  Example content for {env_file}:")
            print("  " + example_content.strip().replace('\n', '\n  '))


async def dotenv_priority_example():
    """Example showing .env file priority and override behavior."""
    print("\n=== .env Priority and Override Example ===")
    
    # Show current environment variables
    print("Current environment variables:")
    env_vars = ['AWS_BEARER_TOKEN_BEDROCK', 'BEDROCK_REGIONS', 'DEFAULT_MODEL']
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        print(f"  {var}: {value}")
    
    print("\nTesting priority order:")
    print("1. Direct credentials parameter (highest)")
    print("2. Environment variables")  
    print("3. .env file (lowest)")
    
    # Test with direct credentials (should override everything)
    try:
        async with BedrockRegionBalancer(
            credentials={'bedrock_api_key': 'direct-parameter-key'},
            use_dotenv=True,  # .env file will be loaded but overridden
            default_model="claude-3.5-sonnet"
        ) as balancer:
            print("\n✓ Direct credentials parameter used (highest priority)")
            
    except Exception as e:
        print(f"✗ Error with direct credentials: {e}")
    
    # Test with environment variables only
    try:
        async with BedrockRegionBalancer(
            use_dotenv=False,  # Skip .env file
            use_environment=True
        ) as balancer:
            print("✓ Environment variables used (medium priority)")
            
    except Exception as e:
        print(f"✗ Error with environment variables: {e}")
        
    # Test with .env file only
    try:
        # Temporarily clear environment variables for this test
        original_env = {}
        for var in env_vars:
            if var in os.environ:
                original_env[var] = os.environ[var]
                del os.environ[var]
        
        async with BedrockRegionBalancer(
            use_dotenv=True,
            use_environment=True  # Will check env vars but they're cleared
        ) as balancer:
            print("✓ .env file used (lowest priority)")
            
        # Restore environment variables
        for var, value in original_env.items():
            os.environ[var] = value
            
    except Exception as e:
        print(f"✗ Error with .env file: {e}")


async def dotenv_validation_example():
    """Example showing .env file validation and error handling."""
    print("\n=== .env File Validation Example ===")
    
    # Test with invalid .env content
    invalid_configs = [
        ("Empty credentials", "BEDROCK_REGIONS=us-west-2"),
        ("Invalid region", "AWS_BEARER_TOKEN_BEDROCK=key\nBEDROCK_REGIONS=invalid-region"),
        ("Mixed formats", "AWS_BEARER_TOKEN_BEDROCK=key\nAWS_ACCESS_KEY_ID=id"),
    ]
    
    for test_name, content in invalid_configs:
        print(f"\nTesting: {test_name}")
        
        # Create temporary invalid .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            async with BedrockRegionBalancer(
                dotenv_path=temp_path,
                use_dotenv=True
            ) as balancer:
                print(f"✓ Loaded despite potential issues")
                
        except Exception as e:
            print(f"✗ Validation error (expected): {type(e).__name__}: {e}")
        finally:
            os.unlink(temp_path)


async def main():
    """Run all .env examples."""
    print("Bedrock Region Balancer - .env File Examples")
    print("=" * 50)
    print()
    print("This demonstrates various ways to use .env files:")
    print("• Basic .env file usage")
    print("• Custom file paths")
    print("• Environment-specific configurations")
    print("• Priority and override behavior")
    print("• Validation and error handling")
    print()
    
    await basic_dotenv_example()
    await custom_dotenv_path_example()
    await environment_specific_example()
    await dotenv_priority_example()
    await dotenv_validation_example()
    
    print("\n" + "=" * 50)
    print(".env examples completed!")
    print("\nBest practices:")
    print("• Use .env files for development convenience")
    print("• Use environment variables for production")
    print("• Use Secrets Manager for sensitive credentials")
    print("• Never commit .env files to version control")
    print("• Use environment-specific .env files (.env.dev, .env.prod)")


if __name__ == "__main__":
    asyncio.run(main())