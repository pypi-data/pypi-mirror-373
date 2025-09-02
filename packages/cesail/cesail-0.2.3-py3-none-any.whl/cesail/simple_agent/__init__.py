"""
CeSail Simple Agent

This package provides the AI-powered web automation agent.
"""

__version__ = "0.1.1"
__author__ = "CeSail Contributors"
__email__ = "ajjayawardane@gmail.com"

# Import main components for easy access
from .simple_agent import SimpleAgent
from .llm_interface import SimpleLLMInterface

__all__ = [
    "SimpleAgent",
    "SimpleLLMInterface",
    "__version__",
    "__author__",
    "__email__"
]

