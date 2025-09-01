"""
RCK SDK for Python
"""

__version__ = "0.2.0"

# Core configuration
from .config import configure

# High-level API functions
from .api import (
    structured_transform,
    learn_from_examples,
    generate_text,
    generate_image,
    auto,
    ImageResponse,
    ImageDetails,
)

# Pydantic Models for type hinting and advanced usage
from .model import (
    EndpointModel,
    AttractorInputBase,
    AttractorOutputBase,
    ComputeConfig,
    EngineEnum,
    SpeedEnum,
    ScaleEnum
)

# Custom Exceptions
from .exceptions import (
    RCKException,
    RCKConfigurationError,
    RCKAPIError
)

__all__ = [
    # Configuration
    "configure",
    # High-level API
    "structured_transform",
    "learn_from_examples",
    "generate_text",
    "generate_image",
    "auto",
    # API Response Models
    "ImageResponse",
    "ImageDetails",
    # Base Models for Customization
    "EndpointModel",
    "AttractorInputBase",
    "AttractorOutputBase",
    # Config Models for Overrides
    "ComputeConfig",
    "EngineEnum",
    "SpeedEnum",
    "ScaleEnum",
    # Exceptions
    "RCKException",
    "RCKConfigurationError",
    "RCKAPIError",
]
