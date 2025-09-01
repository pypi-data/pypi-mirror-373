"""
AWS Bedrock Converse API integration for standardized model interactions.

The Converse API provides a unified interface across different foundation models,
supporting multimodal content, tool use, and advanced features like guardrails.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
import json
import logging

logger = logging.getLogger(__name__)


class APIMethod(Enum):
    """Supported API methods for Bedrock interactions."""
    INVOKE_MODEL = "invoke_model"
    CONVERSE = "converse"


class ContentType(Enum):
    """Supported content types for Converse API."""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    TOOL_USE = "toolUse"
    TOOL_RESULT = "toolResult"


class MessageRole(Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"


class StopReason(Enum):
    """Reasons why model generation stopped."""
    END_TURN = "end_turn"
    TOOL_USE = "tool_use"
    MAX_TOKENS = "max_tokens"
    STOP_SEQUENCE = "stop_sequence"
    GUARDRAIL_INTERVENED = "guardrail_intervened"
    CONTENT_FILTERED = "content_filtered"


class ToolChoice(Enum):
    """Tool usage configuration options."""
    AUTO = "auto"      # Model decides whether to use tools
    ANY = "any"        # Must use at least one tool
    TOOL = "tool"      # Must use specific named tool


class ConverseAPIHelper:
    """Helper class for working with Bedrock Converse API."""
    
    @staticmethod
    def create_message(role: Union[str, MessageRole], content: Union[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Create a properly formatted message for Converse API.
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content - string or list of content blocks
            
        Returns:
            Formatted message dictionary
        """
        if isinstance(role, MessageRole):
            role = role.value
            
        if isinstance(content, str):
            # Simple text message
            return {
                "role": role,
                "content": [
                    {
                        "text": content
                    }
                ]
            }
        else:
            # Complex content with multiple blocks
            return {
                "role": role,
                "content": content
            }
    
    @staticmethod
    def create_text_content(text: str) -> Dict[str, Any]:
        """Create text content block."""
        return {
            "text": text
        }
    
    @staticmethod
    def create_image_content(source: Dict[str, Any], format: str = "png") -> Dict[str, Any]:
        """
        Create image content block.
        
        Args:
            source: Image source (bytes or S3 location)
            format: Image format (png, jpeg, gif, webp)
            
        Returns:
            Image content block
        """
        return {
            "image": {
                "format": format,
                "source": source
            }
        }
    
    @staticmethod
    def create_document_content(source: Dict[str, Any], format: str, name: str) -> Dict[str, Any]:
        """
        Create document content block.
        
        Args:
            source: Document source (bytes or S3 location)
            format: Document format (pdf, csv, doc, docx, xls, xlsx, html, txt, md)
            name: Document name
            
        Returns:
            Document content block
        """
        return {
            "document": {
                "format": format,
                "name": name,
                "source": source
            }
        }
    
    @staticmethod
    def create_tool_use_content(tool_use_id: str, name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create tool use content block."""
        return {
            "toolUse": {
                "toolUseId": tool_use_id,
                "name": name,
                "input": input_data
            }
        }
    
    @staticmethod
    def create_tool_result_content(tool_use_id: str, content: List[Dict[str, Any]], 
                                 status: str = "success") -> Dict[str, Any]:
        """
        Create tool result content block.
        
        Args:
            tool_use_id: ID of the tool use request
            content: Result content blocks
            status: Result status ('success' or 'error')
            
        Returns:
            Tool result content block
        """
        return {
            "toolResult": {
                "toolUseId": tool_use_id,
                "content": content,
                "status": status
            }
        }
    
    @staticmethod
    def create_inference_config(max_tokens: Optional[int] = None,
                              temperature: Optional[float] = None,
                              top_p: Optional[float] = None,
                              stop_sequences: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create inference configuration.
        
        Args:
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling threshold (0.0 to 1.0)
            stop_sequences: Sequences that will stop generation
            
        Returns:
            Inference configuration dictionary
        """
        config = {}
        
        if max_tokens is not None:
            config["maxTokens"] = max_tokens
        if temperature is not None:
            config["temperature"] = temperature
        if top_p is not None:
            config["topP"] = top_p
        if stop_sequences is not None:
            config["stopSequences"] = stop_sequences
            
        return config
    
    @staticmethod
    def create_tool_config(tools: List[Dict[str, Any]], 
                          tool_choice: Optional[Union[str, ToolChoice, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create tool configuration.
        
        Args:
            tools: List of tool specifications
            tool_choice: Tool usage preference
            
        Returns:
            Tool configuration dictionary
        """
        config = {"tools": tools}
        
        if tool_choice is not None:
            if isinstance(tool_choice, ToolChoice):
                config["toolChoice"] = {"auto": {}} if tool_choice == ToolChoice.AUTO else {tool_choice.value: {}}
            elif isinstance(tool_choice, str):
                if tool_choice in ["auto", "any"]:
                    config["toolChoice"] = {tool_choice: {}}
                else:
                    # Assume it's a tool name
                    config["toolChoice"] = {"tool": {"name": tool_choice}}
            else:
                config["toolChoice"] = tool_choice
                
        return config
    
    @staticmethod
    def create_guardrail_config(guardrail_identifier: str, 
                               guardrail_version: str,
                               trace: bool = False) -> Dict[str, Any]:
        """
        Create guardrail configuration.
        
        Args:
            guardrail_identifier: Guardrail ID or ARN
            guardrail_version: Guardrail version
            trace: Enable guardrail trace
            
        Returns:
            Guardrail configuration dictionary
        """
        return {
            "guardrailIdentifier": guardrail_identifier,
            "guardrailVersion": guardrail_version,
            "trace": trace
        }
    
    @staticmethod
    def convert_invoke_model_to_converse(body: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert invoke_model format to Converse API format.
        
        Args:
            body: invoke_model request body
            
        Returns:
            Converse API compatible request
        """
        if isinstance(body, str):
            body = json.loads(body)
        
        # Create converse request structure
        converse_request = {
            "messages": [],
            "inferenceConfig": {}
        }
        
        # Handle different model formats
        if "messages" in body:
            # Already in messages format (Anthropic Claude)
            for msg in body["messages"]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                converse_request["messages"].append(
                    ConverseAPIHelper.create_message(role, content)
                )
        elif "prompt" in body:
            # Legacy prompt format
            converse_request["messages"].append(
                ConverseAPIHelper.create_message("user", body["prompt"])
            )
        elif "inputText" in body:
            # Amazon Titan format
            converse_request["messages"].append(
                ConverseAPIHelper.create_message("user", body["inputText"])
            )
        
        # Map inference parameters
        inference_config = {}
        
        # Common parameters
        param_mapping = {
            "max_tokens": "maxTokens",
            "max_tokens_to_sample": "maxTokens", 
            "maxTokens": "maxTokens",
            "temperature": "temperature",
            "top_p": "topP",
            "topP": "topP",
            "stop_sequences": "stopSequences"
        }
        
        for old_key, new_key in param_mapping.items():
            if old_key in body:
                inference_config[new_key] = body[old_key]
        
        if inference_config:
            converse_request["inferenceConfig"] = inference_config
        
        # Handle system prompts
        if "system" in body:
            converse_request["system"] = [{"text": body["system"]}]
        
        return converse_request
    
    @staticmethod
    def parse_converse_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Converse API response into a standardized format.
        
        Args:
            response: Raw Converse API response
            
        Returns:
            Standardized response format
        """
        parsed = {
            "content": [],
            "stop_reason": response.get("stopReason", "unknown"),
            "usage": response.get("usage", {}),
            "metrics": response.get("metrics", {}),
            "model_id": response.get("ResponseMetadata", {}).get("HTTPHeaders", {}).get("x-amzn-bedrock-model-id")
        }
        
        # Extract content from output message
        output = response.get("output", {})
        message = output.get("message", {})
        content_blocks = message.get("content", [])
        
        for block in content_blocks:
            if "text" in block:
                parsed["content"].append({
                    "type": "text",
                    "text": block["text"]
                })
            elif "toolUse" in block:
                parsed["content"].append({
                    "type": "tool_use",
                    "id": block["toolUse"]["toolUseId"],
                    "name": block["toolUse"]["name"],
                    "input": block["toolUse"]["input"]
                })
        
        return parsed
    
    @staticmethod
    def is_model_compatible(model_id: str) -> bool:
        """
        Check if a model is compatible with Converse API.
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if model supports Converse API
        """
        # Most modern models support Converse API
        # Legacy models might not support it
        converse_compatible_patterns = [
            "anthropic.claude-3",
            "anthropic.claude-sonnet",
            "anthropic.claude-haiku", 
            "anthropic.claude-opus",
            "amazon.titan-text",
            "amazon.titan-embed",
            "ai21.j2",
            "cohere.command",
            "meta.llama",
            "mistral."
        ]
        
        return any(pattern in model_id.lower() for pattern in converse_compatible_patterns)