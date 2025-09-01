"""Core commit message generation logic.

This module contains the main CommitGenerator class that orchestrates the entire
process of generating AI-powered commit messages from Git diffs.

The process involves:
1. Loading configuration and validating settings
2. Checking for merge commits (which are skipped)
3. Getting staged changes from Git
4. Processing and filtering the diff content
5. Sending the diff to AI APIs for message generation
6. Cleaning and validating the generated message
7. Providing fallback messages if AI generation fails

Example:
    generator = CommitGenerator()
    message = generator.generate_commit_message()
    print(message)  # "feat(auth): add JWT token validation"
"""

import fnmatch
import logging
import re
import subprocess
import functools
from pathlib import Path
from typing import Optional

from .api_clients import APIError, create_client
from .config import Config

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Exception raised for security-related errors."""
    pass


class GitError(Exception):
    """Exception raised for Git-related errors."""
    pass


def secure_subprocess_run(cmd: list, cwd: Optional[Path] = None, timeout: int = 30, **kwargs) -> subprocess.CompletedProcess:
    """Secure wrapper for subprocess.run with validation and timeouts."""

    # Validate command
    if not cmd or not isinstance(cmd, list):
        raise SecurityError("Invalid command")

    # Validate all command components are strings
    if not all(isinstance(arg, str) for arg in cmd):
        raise SecurityError("All command arguments must be strings")

    # Validate working directory
    if cwd is not None:
        if not isinstance(cwd, Path):
            cwd = Path(cwd)
        cwd = cwd.resolve()
        if not cwd.exists():
            raise SecurityError(f"Working directory does not exist: {cwd}")
        if not (cwd / ".git").exists():
            raise SecurityError("Not a Git repository")

    # Set secure defaults
    secure_kwargs = {
        'capture_output': True,
        'text': True,
        'check': True,
        'timeout': timeout,
        'shell': False,  # Never use shell
        **kwargs
    }

    try:
        return subprocess.run(cmd, cwd=cwd, **secure_kwargs)
    except subprocess.TimeoutExpired:
        raise SecurityError(f"Command timed out after {timeout} seconds")
    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e}")


def sanitize_repo_path(path: str) -> Path:
    """Sanitize and validate repository path."""
    if not path or not isinstance(path, str):
        raise SecurityError("Invalid repository path")

    # Convert to Path and resolve
    try:
        clean_path = Path(path).resolve()
    except Exception as e:
        raise SecurityError(f"Invalid path: {e}")

    # Check if path exists
    if not clean_path.exists():
        raise SecurityError("Repository path does not exist")

    # Check if it's a Git repository
    if not (clean_path / ".git").exists():
        raise SecurityError("Not a Git repository")

    # Additional security checks
    path_str = str(clean_path)
    if any(suspicious in path_str for suspicious in ['/proc/', '/sys/', '/dev/']):
        raise SecurityError("Access to system directories not allowed")

    return clean_path


class GitError(Exception):
    """Git-related errors."""

    pass


class CommitGenerator:
    """Main class for generating AI-powered commit messages."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the commit generator.

        Args:
            config: Configuration object. If None, will create from current directory.
        """
        self.config = config or Config()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging based on configuration."""
        if self.config.debug_enabled:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(self.config.log_file),
                    logging.StreamHandler(),
                ],
            )
        else:
            logging.basicConfig(level=logging.WARNING)

    def generate_commit_message(self, commit_msg_file: Optional[str] = None) -> str:
        """Generate a commit message for staged changes.

        Args:
            commit_msg_file: Path to commit message file (for Git hook usage)

        Returns:
            Generated commit message

        Raises:
            GitError: If Git operations fail
            ConfigError: If configuration is invalid
            APIError: If AI API calls fail
        """
        logger.info("Starting commit message generation")

        # Validate configuration
        self.config.validate()

        # Check if this is a merge commit
        if self._is_merge_commit():
            logger.info("Merge commit detected, skipping AI generation")
            return ""

        # Get staged changes
        diff = self._get_staged_diff()
        if not diff.strip():
            logger.info("No staged changes found")
            return ""

        # Process and truncate diff if necessary
        processed_diff = self._process_diff(diff)

        # Generate commit message using AI
        message = self._generate_with_ai(processed_diff)

        # Write to commit message file if provided
        if commit_msg_file:
            with open(commit_msg_file, "w", encoding="utf-8") as f:
                f.write(message)

        logger.info(f"Generated commit message: {message}")
        return message

    def _is_merge_commit(self) -> bool:
        """Check if this is a merge commit."""
        try:
            # Check if MERGE_HEAD exists
            merge_head = self.config.repo_root / ".git" / "MERGE_HEAD"
            return merge_head.exists()
        except Exception as e:
            logger.warning(f"Could not check for merge commit: {e}")
            return False

    def _get_staged_diff(self) -> str:
        """Get the diff of staged changes.

        Returns:
            Git diff output as string

        Raises:
            GitError: If git command fails
            SecurityError: If repository path is invalid
        """
        try:
            # Validate and sanitize repository path
            repo_path = sanitize_repo_path(str(self.config.repo_root))

            # Use secure subprocess wrapper
            result = secure_subprocess_run(
                ["git", "diff", "--cached"],
                cwd=repo_path,
                timeout=30
            )
            return result.stdout
        except (SecurityError, GitError):
            # Re-raise security and git errors as-is
            raise
        except FileNotFoundError:
            raise GitError("Git command not found. Please ensure Git is installed.")
        except Exception as e:
            raise GitError(f"Failed to get staged diff: {e}")

    def _process_diff(self, diff: str) -> str:
        """Process and filter the diff content.

        Args:
            diff: Raw git diff output

        Returns:
            Processed diff content
        """
        # Filter out excluded patterns
        filtered_diff = self._filter_excluded_files(diff)

        # Truncate if too large
        if len(filtered_diff) > self.config.max_diff_size:
            logger.debug(
                f"Diff size ({len(filtered_diff)}) exceeds limit ({self.config.max_diff_size}), truncating"
            )
            filtered_diff = (
                filtered_diff[: self.config.max_diff_size] + "\n... [truncated]"
            )

        return filtered_diff

    def _filter_excluded_files(self, diff: str) -> str:
        """Filter out files matching exclude patterns.

        Args:
            diff: Git diff content

        Returns:
            Filtered diff content
        """
        if not self.config.exclude_patterns:
            return diff

        lines = diff.split("\n")
        filtered_lines = []
        current_file = None
        skip_file = False

        for line in lines:
            # Check for file headers
            if line.startswith("diff --git"):
                # Extract filename from diff header
                match = re.search(r"diff --git a/(.*?) b/", line)
                if match:
                    current_file = match.group(1)
                    skip_file = self._should_exclude_file(current_file)
                else:
                    skip_file = False

            # Include line if not skipping current file
            if not skip_file:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _should_exclude_file(self, filename: str) -> bool:
        """Check if a file should be excluded based on patterns.

        Args:
            filename: File path to check

        Returns:
            True if file should be excluded
        """
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                logger.debug(f"Excluding file {filename} (matches pattern {pattern})")
                return True
        return False

    def _generate_with_ai(self, diff: str) -> str:
        """Generate commit message using AI API.

        Args:
            diff: Processed git diff content

        Returns:
            Generated commit message

        Raises:
            APIError: If AI generation fails after all retries
        """
        # Build prompt
        prompt = self._build_prompt(diff)

        # Create API client
        client = create_client(
            provider=self.config.provider,
            api_key=self.config.api_key,
            model=self.config.model,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
        )

        # Try to generate message with retries
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                message = client.generate_commit_message(prompt)

                # Clean and validate message
                cleaned_message = self._clean_message(message)
                if self._validate_message(cleaned_message):
                    return cleaned_message
                else:
                    logger.warning(
                        f"Generated message failed validation: {cleaned_message}"
                    )

            except APIError as e:
                last_error = e
                logger.warning(f"API attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries:
                    logger.info(f"Retrying in {self.config.retry_delay} seconds...")
                    import time

                    time.sleep(self.config.retry_delay)

        # If all attempts failed, return fallback message
        logger.error(f"All AI generation attempts failed. Last error: {last_error}")
        return self.config.default_message

    def _build_prompt(self, diff: str) -> str:
        """Build the prompt for AI generation.

        Args:
            diff: Git diff content

        Returns:
            Formatted prompt string
        """
        template = self.config.get_prompt_template()

        # Format template with configuration values
        return template.format(
            diff=diff,
            max_chars=self.config.max_chars,
            types=", ".join(self.config.commit_types),
            scopes=", ".join(self.config.commit_scopes),
        )

    def _clean_message(self, message: str) -> str:
        """Clean and normalize the generated message with security validation.

        Args:
            message: Raw message from AI

        Returns:
            Cleaned and validated message

        Raises:
            SecurityError: If message contains suspicious content
        """
        if not message or not isinstance(message, str):
            raise SecurityError("Invalid message input")

        # Remove leading/trailing whitespace
        message = message.strip()

        # Take only the first line
        message = message.split("\n")[0]

        # Remove quotes if present
        message = message.strip("\"'")

        # Security validation - check for suspicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'\x00',  # Null bytes
            r'\.\./',  # Path traversal
            r'\\\\',   # UNC paths
            r'[;&|`$]',  # Command injection characters
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected in message: {pattern}")
                raise SecurityError(f"Message contains suspicious content")

        # Remove potentially dangerous characters
        message = re.sub(r'[^\w\s\(\)\:\-\.\,\!]', '', message)

        # Validate length constraints
        if len(message) < 5:
            raise SecurityError("Message too short (minimum 5 characters)")

        # Ensure it doesn't exceed max length
        if len(message) > self.config.max_chars:
            message = message[:self.config.max_chars].rstrip()

        return message

    def _validate_message(self, message: str) -> bool:
        """Validate the generated commit message.

        Args:
            message: Commit message to validate

        Returns:
            True if message is valid
        """
        if not message or len(message) < 5:
            return False

        # Check if it follows conventional commit format using configured types
        types_pattern = "|".join(self.config.commit_types)
        pattern = rf"^({types_pattern})(\(.+\))?: .+"
        if not re.match(pattern, message):
            logger.debug(f"Message doesn't match conventional commit format: {message}")
            return False

        return True
