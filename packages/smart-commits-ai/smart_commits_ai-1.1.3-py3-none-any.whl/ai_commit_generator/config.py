"""Configuration management for AI Commit Generator."""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration-related errors."""

    pass


class SecurityError(Exception):
    """Security-related errors."""

    pass


def validate_file_path(base_path: Path, file_path: Path) -> Path:
    """Validate file path is within base directory and safe.

    Args:
        base_path: Base directory path
        file_path: File path to validate

    Returns:
        Validated and resolved file path

    Raises:
        SecurityError: If path is unsafe or outside base directory
    """
    try:
        # Resolve paths
        resolved_base = base_path.resolve()
        resolved_file = (base_path / file_path).resolve()

        # Ensure file is within base directory
        resolved_file.relative_to(resolved_base)

        # Check for suspicious path components
        path_str = str(resolved_file)
        if any(component in path_str for component in ['..', '~', '$']):
            raise SecurityError(f"Unsafe path component in: {file_path}")

        return resolved_file

    except ValueError:
        raise SecurityError(f"Path traversal attempt: {file_path}")
    except Exception as e:
        raise SecurityError(f"Invalid file path: {file_path} - {e}")


def secure_yaml_load(file_path: Path) -> Dict[str, Any]:
    """Securely load YAML file with validation.

    Args:
        file_path: Path to YAML file

    Returns:
        Parsed YAML content as dictionary

    Raises:
        SecurityError: If file is unsafe or invalid
        ConfigError: If YAML is malformed
    """
    if not file_path.exists():
        return {}

    # Validate file size (prevent DoS)
    file_size = file_path.stat().st_size
    if file_size > 1024 * 1024:  # 1MB limit
        raise SecurityError("Configuration file too large")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Use safe_load to prevent code execution
            content = yaml.safe_load(f)

        # Validate content type
        if content is None:
            return {}

        if not isinstance(content, dict):
            raise SecurityError("Configuration must be a dictionary")

        return content

    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML syntax: {e}")
    except Exception as e:
        raise SecurityError(f"Failed to load configuration: {e}")


class Config:
    """Configuration manager for AI Commit Generator."""

    # Default configuration values
    DEFAULT_CONFIG = {
        "api": {
            "provider": "groq",
            "models": {
                "groq": {
                    "default": "llama-3.3-70b-versatile",
                    "alternatives": ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
                },
                "openrouter": {
                    "default": "meta-llama/llama-3.1-70b-instruct",
                    "alternatives": [
                        "anthropic/claude-3.5-sonnet",
                        "google/gemini-pro-1.5",
                    ],
                },
                "cohere": {
                    "default": "command-r-plus",
                    "alternatives": ["command-r", "command-light"],
                },
            },
        },
        "commit": {
            "max_chars": 72,
            "types": [
                "feat",
                "fix",
                "docs",
                "style",
                "refactor",
                "perf",
                "test",
                "build",
                "ci",
                "chore",
                "revert",
            ],
            "scopes": [
                "api",
                "auth",
                "ui",
                "db",
                "config",
                "deps",
                "security",
                "performance",
                "i18n",
                "tests",
            ],
        },
        "processing": {
            "max_diff_size": 4000,  # Reduced for security
            "exclude_patterns": [
                "*.key",
                "*.pem",
                "*.p12",
                "*.env*",
                "secrets/*",
                "*.lock",
                "*.log",
                "node_modules/*",
                ".git/*",
                "dist/*",
                "build/*",
                "*.min.js",
                "*.min.css",
            ],
            "truncate_files": True,
            "max_file_lines": 100,
        },
        "security": {
            "validate_inputs": True,
            "sanitize_logs": True,
            "max_log_size": 10485760,  # 10MB
            "timeout": 30,
            "verify_ssl": True,
        },
        "fallback": {
            "default_message": "chore: update files",
            "max_retries": 3,
            "retry_delay": 1,
        },
        "debug": {
            "enabled": False,
            "log_file": ".commitgen.log",
            "save_requests": False,
        },
    }

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize configuration.

        Args:
            repo_root: Root directory of the Git repository. If None, will try to detect.

        Raises:
            SecurityError: If repository path is invalid or unsafe
            ConfigError: If configuration cannot be loaded
        """
        self.repo_root = repo_root or self._find_repo_root()

        # Validate repository root
        self._validate_repo_root()

        # Securely validate configuration file paths
        self.config_file = validate_file_path(self.repo_root, Path(".commitgen.yml"))
        self.env_file = validate_file_path(self.repo_root, Path(".env"))

        # Load configuration
        self._config = self._load_config()
        self._load_env()

    def _find_repo_root(self) -> Path:
        """Find the Git repository root directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise ConfigError("Not in a Git repository")

    def _validate_repo_root(self) -> None:
        """Validate repository root path for security.

        Raises:
            SecurityError: If repository path is unsafe
        """
        if not self.repo_root or not isinstance(self.repo_root, Path):
            raise SecurityError("Invalid repository root")

        # Resolve path and check existence
        try:
            resolved_path = self.repo_root.resolve()
        except Exception as e:
            raise SecurityError(f"Cannot resolve repository path: {e}")

        if not resolved_path.exists():
            raise SecurityError("Repository path does not exist")

        if not (resolved_path / ".git").exists():
            raise SecurityError("Not a Git repository")

        # Check for suspicious path components
        path_str = str(resolved_path)
        if any(suspicious in path_str for suspicious in ['/proc/', '/sys/', '/dev/']):
            raise SecurityError("Access to system directories not allowed")

        # Update repo_root to resolved path
        self.repo_root = resolved_path

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from .commitgen.yml file securely."""
        config = self.DEFAULT_CONFIG.copy()

        if self.config_file.exists():
            try:
                # Use secure YAML loading
                user_config = secure_yaml_load(self.config_file)
                config = self._merge_config(config, user_config)
                logger.debug(f"Loaded configuration from {self.config_file}")
            except (SecurityError, ConfigError):
                # Re-raise security and config errors as-is
                raise
            except Exception as e:
                raise ConfigError(f"Error reading {self.config_file}: {e}")
        else:
            logger.debug("No configuration file found, using defaults")

        return config

    def _merge_config(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.debug(f"Loaded environment from {self.env_file}")

    @property
    def provider(self) -> str:
        """Get the configured AI provider."""
        return self._config["api"]["provider"]

    @property
    def model(self) -> str:
        """Get the model for the current provider."""
        provider = self.provider
        models = self._config["api"]["models"].get(provider, {})

        # Check for environment variable override
        env_var = f"{provider.upper()}_MODEL"
        env_model = os.getenv(env_var)
        if env_model:
            return env_model

        return models.get("default", "llama-3.3-70b-versatile")

    @property
    def api_key(self) -> str:
        """Get the API key for the current provider."""
        provider = self.provider
        env_var = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_var)

        if not api_key:
            raise ConfigError(
                f"API key not found. Please set {env_var} in your .env file"
            )

        return api_key

    @property
    def max_chars(self) -> int:
        """Get maximum characters for commit message."""
        return self._config["commit"]["max_chars"]

    @property
    def commit_types(self) -> List[str]:
        """Get allowed commit types."""
        return self._config["commit"]["types"]

    @property
    def commit_scopes(self) -> List[str]:
        """Get allowed commit scopes."""
        return self._config["commit"]["scopes"]

    @property
    def max_diff_size(self) -> int:
        """Get maximum diff size to send to AI."""
        return self._config["processing"]["max_diff_size"]

    @property
    def exclude_patterns(self) -> List[str]:
        """Get file patterns to exclude from diff."""
        return self._config["processing"]["exclude_patterns"]

    @property
    def max_retries(self) -> int:
        """Get maximum number of API retries."""
        return self._config["fallback"]["max_retries"]

    @property
    def retry_delay(self) -> int:
        """Get delay between retries in seconds."""
        return self._config["fallback"]["retry_delay"]

    @property
    def default_message(self) -> str:
        """Get default fallback commit message."""
        return self._config["fallback"]["default_message"]

    @property
    def debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return (
            self._config["debug"]["enabled"]
            or os.getenv("DEBUG_ENABLED", "").lower() == "true"
        )

    @property
    def log_file(self) -> Path:
        """Get debug log file path."""
        return self.repo_root / self._config["debug"]["log_file"]

    def get_prompt_template(self) -> str:
        """Get the prompt template for AI generation."""
        template = self._config.get("prompt", {}).get("template")
        if not template:
            # Default template
            template = """Generate a conventional commit message under {max_chars} characters for the following git diff.

Use one of these types: {types}

If applicable, include a scope in parentheses after the type.

Format: type(scope): description

Be concise and descriptive. Focus on WHAT changed, not HOW.

Git diff:
{diff}

Respond with ONLY the commit message, no explanations or additional text."""

        return template

    def validate(self) -> None:
        """Validate the configuration with security checks."""
        # Validate provider
        valid_providers = ["groq", "openrouter", "cohere"]
        if self.provider not in valid_providers:
            raise ConfigError(
                f"Invalid provider '{self.provider}'. Must be one of: {valid_providers}"
            )

        # Validate API key exists and format
        try:
            api_key = self.api_key
            if len(api_key) < 20 or len(api_key) > 200:
                raise SecurityError("API key length is suspicious")
        except ConfigError:
            raise ConfigError(f"API key not configured for provider '{self.provider}'")

        # Validate numeric values with security limits
        if self.max_chars <= 0 or self.max_chars > 500:
            raise ConfigError("max_chars must be between 1 and 500")
        if self.max_diff_size <= 0 or self.max_diff_size > 50000:
            raise SecurityError("max_diff_size must be between 1 and 50000")
        if self.max_retries < 0 or self.max_retries > 10:
            raise ConfigError("max_retries must be between 0 and 10")
        if self.retry_delay < 0 or self.retry_delay > 60:
            raise ConfigError("retry_delay must be between 0 and 60 seconds")

        # Validate security settings
        security_config = self._config.get("security", {})
        timeout = security_config.get("timeout", 30)
        if timeout <= 0 or timeout > 300:
            raise SecurityError("timeout must be between 1 and 300 seconds")

        max_log_size = security_config.get("max_log_size", 10485760)
        if max_log_size <= 0 or max_log_size > 104857600:  # 100MB max
            raise SecurityError("max_log_size must be between 1 and 100MB")
