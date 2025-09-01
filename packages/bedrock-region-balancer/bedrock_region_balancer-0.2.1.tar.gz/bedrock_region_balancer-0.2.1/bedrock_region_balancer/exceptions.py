"""
Custom exceptions for Bedrock Region Balancer.
"""


class BedrockBalancerError(Exception):
    """Base exception for Bedrock Region Balancer."""
    pass


class ModelNotAvailableError(BedrockBalancerError):
    """Raised when a model is not available in any of the specified regions."""
    pass


class RegionNotAvailableError(BedrockBalancerError):
    """Raised when a region is not available or accessible."""
    pass


class SecretsManagerError(BedrockBalancerError):
    """Raised when there's an error accessing AWS Secrets Manager."""
    pass