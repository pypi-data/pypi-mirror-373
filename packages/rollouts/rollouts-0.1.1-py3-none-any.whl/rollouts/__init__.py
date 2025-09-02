"""
Rollouts - A high-quality Python package for generating multiple LLM responses.
"""

from .client import RolloutsClient, create_client
from .datatypes import Rollouts, Response, Usage
from .config import Config
from .openrouter import OpenRouter

__version__ = "0.1.0"

__all__ = [
    "RolloutsClient",
    "create_client",
    "Rollouts",
    "Response",
    "Usage",
    "Config",
    "OpenRouter",
]