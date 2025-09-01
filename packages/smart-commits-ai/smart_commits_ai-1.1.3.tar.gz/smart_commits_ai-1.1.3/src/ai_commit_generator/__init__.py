"""
AI Commit Generator - Automatically generate conventional commit messages using AI.

This package provides an AI-powered Git commit message generator that analyzes
staged changes and creates professional, conventional commit messages using
various AI providers (Groq, OpenRouter, Cohere).
"""

__version__ = "1.1.3"
__author__ = "AI Commit Generator Team"
__email__ = "team@ai-commit-generator.dev"

from .api_clients import APIClient, CohereClient, GroqClient, OpenRouterClient
from .config import Config
from .core import CommitGenerator

__all__ = [
    "CommitGenerator",
    "Config",
    "APIClient",
    "GroqClient",
    "OpenRouterClient",
    "CohereClient",
    "__version__",
]
