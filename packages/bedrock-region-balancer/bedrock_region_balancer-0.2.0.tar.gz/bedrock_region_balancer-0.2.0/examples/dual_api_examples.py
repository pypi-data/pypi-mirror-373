"""
Dual API Examples for Bedrock Region Balancer.

This example specifically demonstrates using both invoke_model and converse APIs
together, showing their differences, similarities, and when to use each approach.
"""

import asyncio
import json
import time
from bedrock_region_balancer import (
    BedrockRegionBalancer,
    ConverseAPIHelper,
    MessageRole,
    ContentType,
    ToolChoice
)


async def side_by_side_comparison():
    """Compare invoke_model vs converse API side by side."""
    print("=== Side-by-Side API Comparison ===")
    
    async with BedrockRegionBalancer() as balancer:
        # Test prompts for comparison
        test_prompts = [
            "What is artificial intelligence?",
            "Write a haiku about coding.",
            "Explain the concept of recursion in programming.",
            "What are the benefits of cloud computing?"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\nTest {i}: {prompt}")
            print("-" * 60)
            
            # invoke_model API
            print("📞 invoke_model API:")
            try:
                invoke_body = {
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                    "temperature": 0.5,
                    "anthropic_version": "bedrock-2023-05-31"
                }
                
                start_time = time.time()
                invoke_response = await balancer.invoke_model(
                    model_id="claude-3.5-sonnet",
                    body=invoke_body
                )
                invoke_time = time.time() - start_time
                
                print(f"  ⏱️  Time: {invoke_time:.3f}s")
                print(f"  🌍 Region: {invoke_response['region']}")
                print(f"  💬 Response: {invoke_response['response']['content'][0]['text']}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            # converse API
            print("\n💬 converse API:")
            try:
                messages = [ConverseAPIHelper.create_message(MessageRole.USER, prompt)]
                inference_config = ConverseAPIHelper.create_inference_config(
                    max_tokens=100,
                    temperature=0.5
                )
                
                start_time = time.time()
                converse_response = await balancer.converse_model(
                    model_id="claude-3.5-sonnet",
                    messages=messages,
                    inference_config=inference_config
                )
                converse_time = time.time() - start_time
                
                parsed = ConverseAPIHelper.parse_converse_response(converse_response['response'])
                
                print(f"  ⏱️  Time: {converse_time:.3f}s")
                print(f"  🌍 Region: {converse_response['region']}")
                print(f"  💬 Response: {parsed['content'][0]['text']}")
                print(f"  🛑 Stop reason: {parsed['stop_reason']}")
                print(f"  📊 Usage: {parsed['usage']}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")


async def multimodal_comparison():
    """Compare multimodal capabilities between APIs."""
    print("\n=== Multimodal Content Comparison ===")
    
    async with BedrockRegionBalancer() as balancer:
        
        # Test 1: Text-only content (both APIs support)
        print("\nTest 1: Text-only content (both APIs)")
        print("-" * 45)
        
        text_prompt = "Describe the importance of data visualization."
        
        # invoke_model with text
        print("📞 invoke_model (text only):")
        try:
            invoke_response = await balancer.invoke_model(
                model_id="claude-3.5-sonnet",
                body={
                    "messages": [{"role": "user", "content": text_prompt}],
                    "max_tokens": 80,
                    "temperature": 0.3,
                    "anthropic_version": "bedrock-2023-05-31"
                }
            )
            print(f"  ✅ Success: {invoke_response['response']['content'][0]['text']}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # converse with text
        print("\n💬 converse (text only):")
        try:
            messages = [ConverseAPIHelper.create_message(MessageRole.USER, text_prompt)]
            converse_response = await balancer.converse_model(
                model_id="claude-3.5-sonnet",
                messages=messages,
                inference_config={"maxTokens": 80, "temperature": 0.3}
            )
            parsed = ConverseAPIHelper.parse_converse_response(converse_response['response'])
            print(f"  ✅ Success: {parsed['content'][0]['text']}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Test 2: Multimodal content (converse API advantage)
        print("\nTest 2: Multimodal content (converse API advantage)")
        print("-" * 52)
        
        print("📞 invoke_model:")
        print("  ⚠️  Limited multimodal support - requires manual formatting")
        
        print("\n💬 converse API:")
        print("  ✅ Native multimodal support with structured content blocks")
        
        # Demonstrate multimodal content creation (without actual images)
        try:
            # Create multimodal content blocks
            multimodal_content = [
                ConverseAPIHelper.create_text_content(
                    "If I provided an image of a data chart, what key elements would you analyze?"
                ),
                # Example of how you would add an image:
                # ConverseAPIHelper.create_image_content(
                #     source={"bytes": image_bytes}, 
                #     format="png"
                # ),
                ConverseAPIHelper.create_text_content(
                    "Please provide a general framework for chart analysis."
                )
            ]
            
            multimodal_messages = [
                ConverseAPIHelper.create_message(MessageRole.USER, multimodal_content)
            ]
            
            multimodal_response = await balancer.converse_model(
                model_id="claude-3.5-sonnet",
                messages=multimodal_messages,
                inference_config={"maxTokens": 150}
            )
            
            parsed = ConverseAPIHelper.parse_converse_response(multimodal_response['response'])
            print(f"  ✅ Multimodal structure created successfully")
            print(f"  💬 Response: {parsed['content'][0]['text']}")
            
        except Exception as e:
            print(f"  ❌ Multimodal error: {e}")


async def tool_use_comparison():
    """Compare tool use capabilities between APIs."""
    print("\n=== Tool Use and Function Calling Comparison ===")
    
    async with BedrockRegionBalancer() as balancer:
        
        print("📞 invoke_model API:")
        print("  ⚠️  Tool use support varies by model and requires manual implementation")
        
        print("\n💬 converse API:")
        print("  ✅ Native tool use with standardized function calling")
        
        # Define a simple calculator tool
        calculator_tool = {
            "toolSpec": {
                "name": "calculator",
                "description": "Perform basic mathematical calculations",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["add", "subtract", "multiply", "divide"],
                                "description": "The mathematical operation to perform"
                            },
                            "a": {
                                "type": "number",
                                "description": "First number"
                            },
                            "b": {
                                "type": "number", 
                                "description": "Second number"
                            }
                        },
                        "required": ["operation", "a", "b"]
                    }
                }
            }
        }
        
        # Create tool configuration
        tool_config = ConverseAPIHelper.create_tool_config(
            tools=[calculator_tool],
            tool_choice=ToolChoice.AUTO
        )
        
        # Test tool use with converse API
        try:
            messages = [
                ConverseAPIHelper.create_message(
                    MessageRole.USER,
                    "I need to calculate 15 * 7. Can you help me with this calculation?"
                )
            ]
            
            tool_response = await balancer.converse_model(
                model_id="claude-3.5-sonnet",
                messages=messages,
                tool_config=tool_config,
                inference_config={"maxTokens": 200}
            )
            
            parsed = ConverseAPIHelper.parse_converse_response(tool_response['response'])
            print(f"  ✅ Tool use response generated")
            
            for content in parsed['content']:
                if content['type'] == 'text':
                    print(f"  💬 Text: {content['text']}")
                elif content['type'] == 'tool_use':
                    print(f"  🛠️  Tool called: {content['name']}")
                    print(f"  📥 Input: {content['input']}")
            
        except Exception as e:
            print(f"  ❌ Tool use error: {e}")


async def performance_benchmark():
    """Benchmark performance differences between APIs."""
    print("\n=== Performance Benchmark ===")
    
    async with BedrockRegionBalancer() as balancer:
        test_prompt = "What is machine learning?"
        num_tests = 5
        
        # Benchmark invoke_model
        print(f"🔥 Benchmarking invoke_model API ({num_tests} requests):")
        invoke_times = []
        
        for i in range(num_tests):
            try:
                start = time.time()
                response = await balancer.invoke_model(
                    model_id="claude-3.5-sonnet",
                    body={
                        "messages": [{"role": "user", "content": test_prompt}],
                        "max_tokens": 50,
                        "temperature": 0.1,
                        "anthropic_version": "bedrock-2023-05-31"
                    },
                    check_availability=False  # Skip check for faster benchmark
                )
                elapsed = time.time() - start
                invoke_times.append(elapsed)
                print(f"  Request {i+1}: {elapsed:.3f}s -> {response['region']}")
            except Exception as e:
                print(f"  Request {i+1}: Failed - {e}")
        
        # Benchmark converse API
        print(f"\n💬 Benchmarking converse API ({num_tests} requests):")
        converse_times = []
        
        for i in range(num_tests):
            try:
                messages = [ConverseAPIHelper.create_message(MessageRole.USER, test_prompt)]
                
                start = time.time()
                response = await balancer.converse_model(
                    model_id="claude-3.5-sonnet",
                    messages=messages,
                    inference_config={"maxTokens": 50, "temperature": 0.1},
                    check_availability=False  # Skip check for faster benchmark
                )
                elapsed = time.time() - start
                converse_times.append(elapsed)
                print(f"  Request {i+1}: {elapsed:.3f}s -> {response['region']}")
            except Exception as e:
                print(f"  Request {i+1}: Failed - {e}")
        
        # Analyze benchmark results
        if invoke_times and converse_times:
            invoke_avg = sum(invoke_times) / len(invoke_times)
            converse_avg = sum(converse_times) / len(converse_times)
            
            print(f"\n📊 Benchmark Results:")
            print(f"  📞 invoke_model average: {invoke_avg:.3f}s")
            print(f"  💬 converse average: {converse_avg:.3f}s")
            
            if invoke_avg < converse_avg:
                print(f"  🏆 invoke_model is {(converse_avg/invoke_avg):.1f}x faster")
            elif converse_avg < invoke_avg:
                print(f"  🏆 converse is {(invoke_avg/converse_avg):.1f}x faster")
            else:
                print(f"  🤝 Both APIs have similar performance")


async def format_migration_example():
    """Show how to migrate from invoke_model to converse format."""
    print("\n=== Format Migration Example ===")
    
    async with BedrockRegionBalancer() as balancer:
        
        print("🔄 Migrating from invoke_model to converse format:")
        
        # Original invoke_model request
        original_requests = [
            {
                "name": "Simple message",
                "body": {
                    "messages": [{"role": "user", "content": "Hello, how are you?"}],
                    "max_tokens": 50,
                    "temperature": 0.7
                }
            },
            {
                "name": "With system prompt",
                "body": {
                    "messages": [
                        {"role": "user", "content": "Tell me about quantum computing."}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "system": "You are a physics professor explaining complex topics simply."
                }
            },
            {
                "name": "Multi-turn conversation",
                "body": {
                    "messages": [
                        {"role": "user", "content": "What is Python?"},
                        {"role": "assistant", "content": "Python is a programming language."},
                        {"role": "user", "content": "What makes it special?"}
                    ],
                    "max_tokens": 80,
                    "temperature": 0.3
                }
            }
        ]
        
        for i, request in enumerate(original_requests, 1):
            print(f"\nMigration {i}: {request['name']}")
            print("-" * 40)
            
            # Show original format
            print("📞 Original invoke_model format:")
            print(f"  {json.dumps(request['body'], indent=2)}")
            
            # Convert to converse format
            try:
                converted = ConverseAPIHelper.convert_invoke_model_to_converse(request['body'])
                
                print("\n💬 Converted converse format:")
                print(f"  messages: {json.dumps(converted['messages'], indent=2)}")
                if 'inferenceConfig' in converted:
                    print(f"  inferenceConfig: {json.dumps(converted['inferenceConfig'], indent=2)}")
                if 'system' in converted:
                    print(f"  system: {json.dumps(converted['system'], indent=2)}")
                
                # Test both formats work
                print("\n🧪 Testing both formats:")
                
                # Original invoke_model
                invoke_response = await balancer.invoke_model(
                    model_id="claude-3.5-sonnet",
                    body={**request['body'], "anthropic_version": "bedrock-2023-05-31"}
                )
                print(f"  📞 invoke_model: ✅ Success from {invoke_response['region']}")
                
                # Converted converse
                converse_response = await balancer.converse_model(
                    model_id="claude-3.5-sonnet",
                    messages=converted['messages'],
                    inference_config=converted.get('inferenceConfig'),
                    system=converted.get('system')
                )
                print(f"  💬 converse: ✅ Success from {converse_response['region']}")
                
            except Exception as e:
                print(f"  ❌ Migration error: {e}")


async def all_regions_dual_api_test():
    """Test both APIs across all regions simultaneously."""
    print("\n=== All Regions Dual API Test ===")
    
    async with BedrockRegionBalancer() as balancer:
        
        prompt = "What is the capital of South Korea?"
        
        print("🌍 Testing invoke_model across all regions:")
        try:
            invoke_body = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 30,
                "temperature": 0,
                "anthropic_version": "bedrock-2023-05-31"
            }
            
            invoke_results = await balancer.invoke_model_all_regions(
                model_id="claude-3.5-sonnet",
                body=invoke_body
            )
            
            for result in invoke_results:
                if 'error' in result:
                    print(f"  ❌ {result['region']}: {result['error']}")
                else:
                    print(f"  ✅ {result['region']}: {result['response']['content'][0]['text']}")
                    
        except Exception as e:
            print(f"  ❌ invoke_model_all_regions error: {e}")
        
        print("\n🌍 Testing converse across all regions:")
        try:
            messages = [ConverseAPIHelper.create_message(MessageRole.USER, prompt)]
            
            converse_results = await balancer.converse_model_all_regions(
                model_id="claude-3.5-sonnet",
                messages=messages,
                inference_config={"maxTokens": 30, "temperature": 0}
            )
            
            for result in converse_results:
                if 'error' in result:
                    print(f"  ❌ {result['region']}: {result['error']}")
                else:
                    parsed = ConverseAPIHelper.parse_converse_response(result['response'])
                    print(f"  ✅ {result['region']}: {parsed['content'][0]['text']}")
                    
        except Exception as e:
            print(f"  ❌ converse_model_all_regions error: {e}")


async def main():
    """Run all dual API examples."""
    print("Bedrock Region Balancer - Dual API Examples")
    print("=" * 50)
    print()
    print("This demonstrates both invoke_model and converse APIs:")
    print("📞 invoke_model: Traditional API with model-specific formats")
    print("💬 converse: Modern unified API with advanced features")
    print("🔄 Format conversion and migration examples")
    print("🏆 Performance comparisons and feature analysis")
    print()
    
    await side_by_side_comparison()
    await multimodal_comparison()
    await tool_use_comparison()
    await performance_benchmark()
    await format_migration_example()
    await all_regions_dual_api_test()
    
    print("\n" + "=" * 50)
    print("Dual API examples completed!")
    print()
    print("📊 Summary:")
    print("• Both APIs fully supported with identical load balancing")
    print("• converse API offers more advanced features (multimodal, tools)")
    print("• invoke_model remains for compatibility and specific use cases")
    print("• Easy format conversion between APIs")
    print("• Performance characteristics may vary by model and region")
    print()
    print("🎯 Recommendation:")
    print("• Use converse API for new projects and advanced features")
    print("• Use invoke_model for existing code and simple use cases")
    print("• Both APIs work seamlessly with BedrockRegionBalancer!")


if __name__ == "__main__":
    asyncio.run(main())