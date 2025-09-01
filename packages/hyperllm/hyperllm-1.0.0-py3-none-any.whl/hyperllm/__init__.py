"""Hyper LLM - A unified interface for multiple LLM providers"""

from .interface import HyperLLM, create_interface
from .providers import get_available_providers

__version__ = "1.0.0"
__all__ = ["HyperLLM", "create_interface", "get_available_providers"]