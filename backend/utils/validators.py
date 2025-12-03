"""
Validation utilities.
Input validation logic separated from business logic.
"""
from typing import Optional, Tuple


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_message(message: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a chat message.

    Args:
        message: The message to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message:
        return False, "Message cannot be empty"

    if not isinstance(message, str):
        return False, "Message must be a string"

    if len(message) > 10000:
        return False, "Message exceeds maximum length of 10000 characters"

    return True, None


def validate_conversation_id(conversation_id: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate a conversation ID.

    Args:
        conversation_id: The conversation ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if conversation_id is None:
        return True, None  # Optional field

    if not isinstance(conversation_id, str):
        return False, "Conversation ID must be a string"

    if len(conversation_id) == 0:
        return False, "Conversation ID cannot be empty"

    return True, None


def validate_model_params(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate model parameters.

    Args:
        temperature: Temperature parameter
        max_tokens: Max tokens parameter

    Returns:
        Tuple of (is_valid, error_message)
    """
    if temperature is not None:
        if not isinstance(temperature, (int, float)):
            return False, "Temperature must be a number"
        if temperature < 0 or temperature > 2:
            return False, "Temperature must be between 0 and 2"

    if max_tokens is not None:
        if not isinstance(max_tokens, int):
            return False, "Max tokens must be an integer"
        if max_tokens < 1 or max_tokens > 32000:
            return False, "Max tokens must be between 1 and 32000"

    return True, None
