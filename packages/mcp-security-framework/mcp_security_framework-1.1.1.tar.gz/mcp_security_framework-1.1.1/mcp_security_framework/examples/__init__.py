"""
Examples Module

This module contains comprehensive examples of how to implement
the MCP Security Framework with real server configurations.

The examples demonstrate:
- Complete implementation of abstract methods
- Real-world server configurations
- Production-ready security setups
- Integration with popular web frameworks

Author: MCP Security Team
Version: 1.0.0
License: MIT
"""

# Import examples conditionally to avoid import errors when dependencies are missing
try:
    from .fastapi_example import FastAPIExample

    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False
    FastAPIExample = None

try:
    from .flask_example import FlaskExample

    _FLASK_AVAILABLE = True
except ImportError:
    _FLASK_AVAILABLE = False
    FlaskExample = None

try:
    from .django_example import DjangoExample

    _DJANGO_AVAILABLE = True
except ImportError:
    _DJANGO_AVAILABLE = False
    DjangoExample = None

try:
    from .standalone_example import StandaloneExample

    _STANDALONE_AVAILABLE = True
except ImportError:
    _STANDALONE_AVAILABLE = False
    StandaloneExample = None

try:
    from .microservice_example import MicroserviceExample

    _MICROSERVICE_AVAILABLE = True
except ImportError:
    _MICROSERVICE_AVAILABLE = False
    MicroserviceExample = None

try:
    from .gateway_example import APIGatewayExample

    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    APIGatewayExample = None

# Build __all__ list with only available examples
__all__ = []

if _FASTAPI_AVAILABLE:
    __all__.append("FastAPIExample")
if _FLASK_AVAILABLE:
    __all__.append("FlaskExample")
if _DJANGO_AVAILABLE:
    __all__.append("DjangoExample")
if _STANDALONE_AVAILABLE:
    __all__.append("StandaloneExample")
if _MICROSERVICE_AVAILABLE:
    __all__.append("MicroserviceExample")
if _GATEWAY_AVAILABLE:
    __all__.append("APIGatewayExample")
