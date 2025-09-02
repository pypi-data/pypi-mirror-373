"""
Model mappings for different regions.
Maps model names to their region-specific profile IDs.
"""

# Model mappings by region for Claude 3.7+ models using Cross Region Inference
# Using Cross Region Inference profile IDs with region prefixes (us./eu./apac.)
MODEL_MAPPINGS = {
    "us-west-2": {
        # Claude 3.7+ models - Cross Region Inference profiles for US region
        "claude-3.7-sonnet": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        
        # Claude 4.x models - Cross Region Inference profiles for US region  
        "claude-4.0-sonnet": "us.anthropic.claude-sonnet-4-20250514-v1:0",
        "claude-4.1-opus": "us.anthropic.claude-opus-4-1-20250805-v1:0",
        "claude-4-opus": "us.anthropic.claude-opus-4-20250514-v1:0"
    },
    "eu-central-1": {
        # Claude 3.7+ models - Cross Region Inference profiles for EU region
        "claude-3.7-sonnet": "eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
        
        # Claude 4.x models - Cross Region Inference profiles for EU region
        "claude-4.0-sonnet": "eu.anthropic.claude-sonnet-4-20250514-v1:0"
    },
    "ap-northeast-2": {
        # Claude 3.7+ models - Cross Region Inference profiles for APAC region
        "claude-3.7-sonnet": "apac.anthropic.claude-3-7-sonnet-20250219-v1:0",
        
        # Claude 4.x models - Cross Region Inference profiles for APAC region
        "claude-4.0-sonnet": "apac.anthropic.claude-sonnet-4-20250514-v1:0"
    }
}

# Default model for testing - Claude 3.7 Sonnet (confirmed ACTIVE in all regions)
DEFAULT_MODEL = "claude-3.7-sonnet"

def get_model_id(model_name: str, region: str) -> str:
    """
    Get the region-specific model ID for a given model name.
    
    Args:
        model_name: The model name (e.g., "claude-3.7-sonnet")
        region: The AWS region (e.g., "us-west-2")
        
    Returns:
        The region-specific model ID
        
    Raises:
        ValueError: If the model is not available in the specified region
    """
    if region not in MODEL_MAPPINGS:
        raise ValueError(f"Region '{region}' is not supported")
    
    if model_name not in MODEL_MAPPINGS[region]:
        raise ValueError(f"Model '{model_name}' is not available in region '{region}'")
    
    return MODEL_MAPPINGS[region][model_name]

def get_available_models(region: str) -> list:
    """
    Get list of available models for a specific region.
    
    Args:
        region: The AWS region
        
    Returns:
        List of available model names
    """
    if region not in MODEL_MAPPINGS:
        return []
    
    return list(MODEL_MAPPINGS[region].keys())

def get_model_regions(model_name: str) -> list:
    """
    Get list of regions where a model is available.
    
    Args:
        model_name: The model name
        
    Returns:
        List of regions where the model is available
    """
    regions = []
    for region, models in MODEL_MAPPINGS.items():
        if model_name in models:
            regions.append(region)
    
    return regions
