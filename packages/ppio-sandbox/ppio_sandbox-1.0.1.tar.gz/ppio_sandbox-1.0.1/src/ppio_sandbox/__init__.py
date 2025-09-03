"""
PPIO Sandbox SDK - Python library for sandbox environments and AI agent tools.

This package provides a comprehensive SDK for working with PPIO sandbox environments,
enabling developers to create, manage, and interact with sandboxed execution contexts
for AI agents and applications.

The SDK is organized into three main modules:
- core: Core sandbox functionality and API clients
- code_interpreter: Code execution and interpretation capabilities  
- desktop: Desktop environment interaction tools
"""

__version__ = "1.0.0"
__author__ = "PPIO"
__email__ = "dev@ppio.com"

# Import core functionality
from . import core
from . import connect
from . import code_interpreter
from . import desktop

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Modules (for backwards compatibility)
    "core",
    "connect", 
    "code_interpreter",
    "desktop",
]
