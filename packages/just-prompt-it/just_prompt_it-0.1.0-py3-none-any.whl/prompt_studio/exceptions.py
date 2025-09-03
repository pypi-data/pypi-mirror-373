"""Custom exceptions for Prompt Studio SDK."""


class PromptStudioError(Exception):
    """Base exception for Prompt Studio SDK."""

    pass


class PromptNotFoundError(PromptStudioError):
    """Raised when a prompt is not found."""

    pass


class TemplateRenderError(PromptStudioError):
    """Raised when template rendering fails."""

    pass
