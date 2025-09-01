"""AI API clients for different providers.

This module provides a unified interface for interacting with different AI providers:
- Groq: Fast and free inference with Llama models
- OpenRouter: Access to multiple premium models (Claude, GPT-4, etc.)
- Cohere: Enterprise-focused AI with Command models

All clients implement the same APIClient interface and handle:
- HTTP requests with retries and error handling
- Provider-specific API formats and authentication
- Rate limiting and timeout management
- Response parsing and validation

Example:
    client = create_client("groq", api_key, "llama-3.3-70b-versatile")
    message = client.generate_commit_message(prompt)
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API-related errors."""

    pass


class APIClient(ABC):
    """Abstract base class for AI API clients."""

    def __init__(
        self, api_key: str, model: str, max_retries: int = 3, retry_delay: int = 1
    ):
        """Initialize API client.

        Args:
            api_key: API key for the provider
            model: Model name to use
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=retry_delay,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @abstractmethod
    def generate_commit_message(self, prompt: str) -> str:
        """Generate a commit message using the AI API.

        Args:
            prompt: The prompt to send to the AI

        Returns:
            Generated commit message

        Raises:
            APIError: If the API call fails
        """
        pass

    def _make_request(
        self, url: str, headers: Dict[str, str], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling.

        Args:
            url: API endpoint URL
            headers: Request headers
            data: Request payload

        Returns:
            Response JSON data

        Raises:
            APIError: If the request fails
        """
        try:
            logger.debug(f"Making API request to {url}")
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                timeout=30,
                verify=True  # Ensure SSL verification
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.SSLError:
            raise APIError("SSL verification failed")
        except requests.exceptions.Timeout:
            raise APIError("API request timed out")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise APIError("Invalid API key")
            elif response.status_code == 429:
                raise APIError("Rate limit exceeded. Please try again later")
            elif response.status_code >= 500:
                raise APIError(f"API server error: {response.status_code}")
            else:
                raise APIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {e}")
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {e}")


class GroqClient(APIClient):
    """Groq API client."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://api.groq.com/openai/v1"

    def generate_commit_message(self, prompt: str) -> str:
        """Generate commit message using Groq API."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 0.3,
            "stream": False,
        }

        response = self._make_request(url, headers, data)

        try:
            message = response["choices"][0]["message"]["content"].strip()
            if not message:
                raise APIError("Empty response from Groq API")
            return message
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Groq API response format: {response}")
            raise APIError(f"Invalid response format from Groq API: {e}")


class OpenRouterClient(APIClient):
    """OpenRouter API client."""

    def __init__(
        self, api_key: str, model: str = "meta-llama/llama-3.1-70b-instruct", **kwargs
    ):
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://openrouter.ai/api/v1"

    def generate_commit_message(self, prompt: str) -> str:
        """Generate commit message using OpenRouter API."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ai-commit-generator",
            "X-Title": "AI Commit Generator",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 0.3,
        }

        response = self._make_request(url, headers, data)

        try:
            message = response["choices"][0]["message"]["content"].strip()
            if not message:
                raise APIError("Empty response from OpenRouter API")
            return message
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected OpenRouter API response format: {response}")
            raise APIError(f"Invalid response format from OpenRouter API: {e}")


class CohereClient(APIClient):
    """Cohere API client."""

    def __init__(self, api_key: str, model: str = "command-r-plus", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://api.cohere.ai/v1"

    def generate_commit_message(self, prompt: str) -> str:
        """Generate commit message using Cohere API."""
        url = f"{self.base_url}/chat"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "message": prompt,
            "max_tokens": 100,
            "temperature": 0.3,
        }

        response = self._make_request(url, headers, data)

        try:
            message = response["text"].strip()
            if not message:
                raise APIError("Empty response from Cohere API")
            return message
        except KeyError as e:
            logger.error(f"Unexpected Cohere API response format: {response}")
            raise APIError(f"Invalid response format from Cohere API: {e}")


def create_client(provider: str, api_key: str, model: str, **kwargs) -> APIClient:
    """Factory function to create API client based on provider.

    Args:
        provider: Provider name (groq, openrouter, cohere)
        api_key: API key for the provider
        model: Model name to use
        **kwargs: Additional arguments for the client

    Returns:
        Configured API client

    Raises:
        ValueError: If provider is not supported
    """
    clients = {
        "groq": GroqClient,
        "openrouter": OpenRouterClient,
        "cohere": CohereClient,
    }

    if provider not in clients:
        raise ValueError(
            f"Unsupported provider: {provider}. Supported: {list(clients.keys())}"
        )

    return clients[provider](api_key, model, **kwargs)
