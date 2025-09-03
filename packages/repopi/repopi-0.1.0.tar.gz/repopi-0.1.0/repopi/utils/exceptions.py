"""Custom exceptions for RepoPi."""

from __future__ import annotations


class RepopiError(Exception):
    """Base exception for RepoPi."""
    
    def __init__(self, message: str, exit_code: int = 1) -> None:
        """Initialize RepoPi error.
        
        Args:
            message: Error message
            exit_code: Exit code for CLI
        """
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code


class ConfigurationError(RepopiError):
    """Configuration-related errors."""
    
    def __init__(self, message: str) -> None:
        super().__init__(f"Configuration error: {message}", exit_code=2)


class GitError(RepopiError):
    """Git operation errors."""
    
    def __init__(self, message: str) -> None:
        super().__init__(f"Git error: {message}", exit_code=3)


class GitHubError(RepopiError):
    """GitHub API errors."""
    
    def __init__(self, message: str) -> None:
        super().__init__(f"GitHub error: {message}", exit_code=4)


class GitLabError(RepopiError):
    """GitLab API errors."""
    
    def __init__(self, message: str) -> None:
        super().__init__(f"GitLab error: {message}", exit_code=5)


class AIError(RepopiError):
    """AI service errors."""
    
    def __init__(self, message: str) -> None:
        super().__init__(f"AI error: {message}", exit_code=6)


class ValidationError(RepopiError):
    """Input validation errors."""
    
    def __init__(self, message: str) -> None:
        super().__init__(f"Validation error: {message}", exit_code=7)


class DependencyError(RepopiError):
    """Missing dependency errors."""
    
    def __init__(self, dependency: str, install_hint: str = "") -> None:
        message = f"Missing dependency: {dependency}"
        if install_hint:
            message += f". Install with: {install_hint}"
        super().__init__(message, exit_code=8)
