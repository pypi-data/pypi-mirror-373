"""
AWS Bedrock Region Load Balancer

A Python package for load balancing AWS Bedrock API calls across multiple regions
using round-robin algorithm with async execution.
"""

from .balancer import BedrockRegionBalancer
from .exceptions import (
    BedrockBalancerError,
    ModelNotAvailableError,
    RegionNotAvailableError,
    SecretsManagerError
)
from .auth_types import AuthType
from .converse_api import (
    ConverseAPIHelper,
    APIMethod,
    ContentType,
    MessageRole,
    StopReason,
    ToolChoice
)

__version__ = '0.2.1'
__all__ = [
    'BedrockRegionBalancer',
    'BedrockBalancerError',
    'ModelNotAvailableError',
    'RegionNotAvailableError',
    'SecretsManagerError',
    'AuthType',
    'ConverseAPIHelper',
    'APIMethod',
    'ContentType',
    'MessageRole',
    'StopReason',
    'ToolChoice'
]