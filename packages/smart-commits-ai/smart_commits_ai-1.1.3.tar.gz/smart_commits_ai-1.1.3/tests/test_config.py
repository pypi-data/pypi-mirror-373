"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from ai_commit_generator.config import Config, ConfigError


class TestConfig:
    """Test configuration loading and validation."""

    def test_default_config(self):
        """Test that default configuration loads correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            config = Config(repo_root=repo_dir)

            assert config.provider == "groq"
            assert config.max_chars == 72
            assert "feat" in config.commit_types
            assert config.max_retries == 3

    def test_custom_config_loading(self):
        """Test loading custom configuration from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            # Create custom config
            config_file = repo_dir / ".commitgen.yml"
            custom_config = {
                "api": {"provider": "openrouter"},
                "commit": {"max_chars": 50},
            }
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)

            config = Config(repo_root=repo_dir)

            assert config.provider == "openrouter"
            assert config.max_chars == 50

    def test_env_loading(self):
        """Test environment variable loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            # Create .env file
            env_file = repo_dir / ".env"
            env_file.write_text("GROQ_API_KEY=test_key_123\n")

            config = Config(repo_root=repo_dir)

            assert config.api_key == "test_key_123"

    def test_missing_api_key_error(self):
        """Test that missing API key raises appropriate error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            # Clear any existing API key environment variables
            import os

            old_groq_key = os.environ.pop("GROQ_API_KEY", None)
            old_openrouter_key = os.environ.pop("OPENROUTER_API_KEY", None)
            old_cohere_key = os.environ.pop("COHERE_API_KEY", None)

            try:
                config = Config(repo_root=repo_dir)

                with pytest.raises(ConfigError, match="API key not found"):
                    config.api_key
            finally:
                # Restore environment variables
                if old_groq_key:
                    os.environ["GROQ_API_KEY"] = old_groq_key
                if old_openrouter_key:
                    os.environ["OPENROUTER_API_KEY"] = old_openrouter_key
                if old_cohere_key:
                    os.environ["COHERE_API_KEY"] = old_cohere_key

    def test_validation(self):
        """Test configuration validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            # Create valid config with API key
            env_file = repo_dir / ".env"
            env_file.write_text("GROQ_API_KEY=test_key\n")

            config = Config(repo_root=repo_dir)

            # Should not raise
            config.validate()

    def test_invalid_provider_validation(self):
        """Test validation with invalid provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            git_dir = repo_dir / ".git"
            git_dir.mkdir()

            # Create config with invalid provider
            config_file = repo_dir / ".commitgen.yml"
            custom_config = {"api": {"provider": "invalid_provider"}}
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)

            config = Config(repo_root=repo_dir)

            with pytest.raises(ConfigError, match="Invalid provider"):
                config.validate()

    def test_not_in_git_repo_error(self):
        """Test error when not in a Git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # No .git directory
            repo_dir = Path(temp_dir)

            # Change to the temp directory so _find_repo_root is called
            import os

            old_cwd = os.getcwd()
            try:
                os.chdir(repo_dir)
                with pytest.raises(ConfigError, match="Not in a Git repository"):
                    Config()  # Don't pass repo_root so it tries to find it
            finally:
                os.chdir(old_cwd)
