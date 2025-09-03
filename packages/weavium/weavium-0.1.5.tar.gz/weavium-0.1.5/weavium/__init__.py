"""
Weavium Python Client

A Python client library for interacting with the Weavium prompt compression API.
Provides methods to compress prompts and inject data into datasets, plus boto3 instrumentation.
"""

from .client import (
    WeaviumClient,
    LLMMessage,
    CompressionResult,
    InjectResult,
)

from .instrumentation import (
    instrument_bedrock,
)

__version__ = "0.1.5"
__author__ = "Weavium Team"
__email__ = "support@weavium.com"
__package_name__ = "weavium"

__all__ = [
    "WeaviumClient",
    "LLMMessage", 
    "CompressionResult",
    "InjectResult",
    "instrument_bedrock",
] 