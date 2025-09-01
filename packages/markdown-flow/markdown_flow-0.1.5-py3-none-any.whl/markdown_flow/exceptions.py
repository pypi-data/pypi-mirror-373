"""
Markdown-Flow Exception Definitions

Defines exception types that may be raised by various operations in the component,
used for error handling and debugging.
"""


class MarkdownFlowError(Exception):
    """
    Base exception class for Markdown-Flow components.

    All Markdown-Flow related exceptions inherit from this class for unified
    exception handling and catching.
    """


class BlockIndexError(MarkdownFlowError):
    """
    Block index error exception.

    Raised when attempting to access a non-existent block index.

    Triggered by:
        - Accessing block index out of range
        - Accessing negative index
    """


class ValidationError(MarkdownFlowError):
    """
    Validation error exception.

    Raised when errors occur during input validation process.

    Triggered by:
        - Invalid validation rule configuration
        - Validation process execution failure
        - Attempting validation on non-interactive blocks
    """
