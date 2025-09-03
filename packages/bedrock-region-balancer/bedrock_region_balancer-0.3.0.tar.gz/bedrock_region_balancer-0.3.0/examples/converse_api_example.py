"""
Converse API Usage Examples for Bedrock Region Balancer with Batch Processing.

This example demonstrates the new Converse API alongside the traditional invoke_model API.
The Converse API provides a unified interface across different foundation models,
supporting multimodal content, tool use, and advanced features like guardrails.

NEW: Batch processing support for improved performance and load distribution.
"""

import asyncio
import json
from bedrock_region_balancer import (
    BedrockRegionBalancer,
    ConverseAPIHelper,
    MessageRole,
    ContentType,
    ToolChoice,
    APIMethod
)


async def basic_converse_example():
    """Basic Converse API usage example."""
    print("=== Basic Converse API Example ===")
    
    async with BedrockRegionBalancer() as balancer:
        # Create messages using ConverseAPIHelper
        messages = [
            ConverseAPIHelper.create_message(
                MessageRole.USER, 
                "Hello! Please introduce yourself and explain the difference between invoke_model and converse APIs."
            )
        ]
        
        # Create inference configuration
        inference_config = ConverseAPIHelper.create_inference_config(
            max_tokens=200,
            temperature=0.7,
            top_p=0.9
        )
        
        try:
            # Use Converse API
            response = await balancer.converse_model(
                model_id="claude-3.5-sonnet",
                messages=messages,
                inference_config=inference_config
            )
            
            print("✓ Converse API Response:")
            print(f"  Region: {response['region']}")
            print(f"  Model ID: {response['model_id']}")
            
            # Parse response using ConverseAPIHelper
            parsed = ConverseAPIHelper.parse_converse_response(response['response'])
            print(f"  Response: {parsed['content'][0]['text']}")
            print(f"  Stop Reason: {parsed['stop_reason']}")
            print(f"  Usage: {parsed['usage']}")
            
        except Exception as e:
            print(f"✗ Error: {e}")


async def multimodal_converse_example():
    """Multimodal content example with Converse API."""
    print("\n=== Multimodal Converse API Example ===")
    
    async with BedrockRegionBalancer() as balancer:
        # Create multimodal message with text and image placeholder
        content_blocks = [
            ConverseAPIHelper.create_text_content(
                "Describe what you would expect to see in a typical cloud architecture diagram. "
                "What are the key components?"
            ),
            # Note: For actual image, you would use:
            # ConverseAPIHelper.create_image_content(
            #     source={"bytes": image_bytes}, 
            #     format="png"
            # )
        ]
        
        messages = [
            ConverseAPIHelper.create_message(MessageRole.USER, content_blocks)
        ]
        
        # System prompt for context
        system = [{"text": "You are a cloud architecture expert. Provide clear, technical explanations."}]
        
        try:
            response = await balancer.converse_model(
                model_id="claude-3.5-sonnet",
                messages=messages,
                system=system,
                inference_config={"maxTokens": 300, "temperature": 0.5}
            )
            
            print("✓ Multimodal Converse Response:")
            print(f"  Region: {response['region']}")
            
            parsed = ConverseAPIHelper.parse_converse_response(response['response'])
            print(f"  Response: {parsed['content'][0]['text']}")
            
        except Exception as e:
            print(f"✗ Error: {e}")


async def tool_use_converse_example():
    """Tool use example with Converse API."""
    print("\n=== Tool Use Converse API Example ===")
    
    async with BedrockRegionBalancer() as balancer:
        # Define a simple tool
        tools = [
            {
                "toolSpec": {
                    "name": "get_weather",
                    "description": "Get current weather information for a city",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "city": {
                                    "type": "string",
                                    "description": "The city name"
                                },
                                "unit": {
                                    "type": "string",
                                    "enum": ["celsius", "fahrenheit"],
                                    "description": "Temperature unit"
                                }
                            },
                            "required": ["city"]
                        }
                    }
                }
            }
        ]
        
        # Create tool configuration
        tool_config = ConverseAPIHelper.create_tool_config(
            tools=tools,
            tool_choice=ToolChoice.AUTO
        )
        
        messages = [
            ConverseAPIHelper.create_message(
                MessageRole.USER,
                "What's the weather like in Seoul, South Korea? Use Celsius please."
            )
        ]
        
        try:
            response = await balancer.converse_model(
                model_id="claude-3.5-sonnet",
                messages=messages,
                tool_config=tool_config,
                inference_config={"maxTokens": 200}
            )
            
            print("✓ Tool Use Converse Response:")
            print(f"  Region: {response['region']}")
            
            parsed = ConverseAPIHelper.parse_converse_response(response['response'])
            
            for content in parsed['content']:
                if content['type'] == 'text':
                    print(f"  Text: {content['text']}")
                elif content['type'] == 'tool_use':
                    print(f"  Tool Use: {content['name']}")
                    print(f"  Tool Input: {content['input']}")
            
        except Exception as e:
            print(f"✗ Error: {e}")


async def api_comparison_example():
    """Compare invoke_model vs converse APIs side by side."""
    print("\n=== API Comparison: invoke_model vs converse ===")
    
    async with BedrockRegionBalancer() as balancer:
        prompt = "Explain quantum computing in one sentence."
        
        # Traditional invoke_model API
        print("\nUsing invoke_model API:")
        try:
            invoke_body = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 100,
                "temperature": 0.5,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            invoke_response = await balancer.invoke_model(
                model_id="claude-3.5-sonnet",
                body=invoke_body
            )
            
            print(f"  Region: {invoke_response['region']}")
            print(f"  Response: {invoke_response['response']['content'][0]['text']}")
            
        except Exception as e:
            print(f"  ✗ invoke_model Error: {e}")
        
        # New Converse API
        print("\nUsing converse API:")
        try:
            messages = [
                ConverseAPIHelper.create_message(MessageRole.USER, prompt)
            ]
            
            converse_response = await balancer.converse_model(
                model_id="claude-3.5-sonnet",
                messages=messages,
                inference_config={
                    "maxTokens": 100,
                    "temperature": 0.5
                }
            )
            
            print(f"  Region: {converse_response['region']}")
            
            parsed = ConverseAPIHelper.parse_converse_response(converse_response['response'])
            print(f"  Response: {parsed['content'][0]['text']}")
            
        except Exception as e:
            print(f"  ✗ converse Error: {e}")


async def format_conversion_example():
    """Demonstrate conversion between invoke_model and converse formats."""
    print("\n=== Format Conversion Example ===")
    
    # Original invoke_model format
    invoke_body = {
        "messages": [
            {"role": "user", "content": "What is machine learning?"}
        ],
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 0.9,
        "system": "You are a helpful AI assistant specializing in technology."
    }
    
    print("Original invoke_model format:")
    print(json.dumps(invoke_body, indent=2))
    
    # Convert to converse format
    converse_format = ConverseAPIHelper.convert_invoke_model_to_converse(invoke_body)
    
    print("\nConverted to converse format:")
    print(json.dumps(converse_format, indent=2))
    
    # Use the converted format
    async with BedrockRegionBalancer() as balancer:
        try:
            response = await balancer.converse_model(
                model_id="claude-3.5-sonnet",
                messages=converse_format['messages'],
                inference_config=converse_format.get('inferenceConfig'),
                system=converse_format.get('system')
            )
            
            print(f"\n✓ Conversion successful! Response from {response['region']}")
            
        except Exception as e:
            print(f"✗ Conversion test failed: {e}")


async def all_regions_comparison():
    """Compare responses from all regions using both APIs."""
    print("\n=== All Regions Comparison ===")
    
    async with BedrockRegionBalancer() as balancer:
        prompt = "What is the capital of South Korea?"
        
        print("Testing invoke_model in all regions:")
        try:
            invoke_body = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            invoke_results = await balancer.invoke_model_all_regions(
                model_id="claude-3.5-sonnet",
                body=invoke_body
            )
            
            for result in invoke_results:
                if 'error' in result:
                    print(f"  {result['region']}: Error - {result['error']}")
                else:
                    print(f"  {result['region']}: {result['response']['content'][0]['text']}")
                    
        except Exception as e:
            print(f"  ✗ invoke_model_all_regions Error: {e}")
        
        print("\nTesting converse in all regions:")
        try:
            messages = [ConverseAPIHelper.create_message(MessageRole.USER, prompt)]
            
            converse_results = await balancer.converse_model_all_regions(
                model_id="claude-3.5-sonnet",
                messages=messages,
                inference_config={"maxTokens": 50, "temperature": 0}
            )
            
            for result in converse_results:
                if 'error' in result:
                    print(f"  {result['region']}: Error - {result['error']}")
                else:
                    parsed = ConverseAPIHelper.parse_converse_response(result['response'])
                    print(f"  {result['region']}: {parsed['content'][0]['text']}")
                    
        except Exception as e:
            print(f"  ✗ converse_model_all_regions Error: {e}")


async def main():
    """Run all Converse API examples."""
    print("Bedrock Region Balancer - Converse API Examples")
    print("=" * 55)
    print()
    print("This demonstrates the new Converse API alongside invoke_model:")
    print("• Basic converse usage with message formatting")
    print("• Multimodal content support")
    print("• Tool use and function calling")
    print("• Side-by-side API comparison")
    print("• Format conversion between APIs")
    print("• All regions testing")
    print()
    
    await basic_converse_example()
    await multimodal_converse_example()
    await tool_use_converse_example()
    await api_comparison_example()
    await format_conversion_example()
    await all_regions_comparison()
    
    print("\n" + "=" * 55)
    print("Converse API examples completed!")
    print()
    print("Key advantages of Converse API:")
    print("✓ Unified interface across all foundation models")
    print("✓ Native multimodal content support")
    print("✓ Built-in tool use and function calling")
    print("✓ Guardrail integration")
    print("✓ Structured response format")
    print("✓ Better parameter validation")
    print()
    print("Both APIs are fully supported in BedrockRegionBalancer!")


if __name__ == "__main__":
    asyncio.run(main())