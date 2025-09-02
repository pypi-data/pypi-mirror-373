"""
Módulo de exceções para automação de UI.

Este módulo define exceções específicas para diferentes tipos de falhas
na automação de UI, permitindo tratamento de erros mais granular e informativo.
"""

from .ui_exceptions import (
    UIBaseException,
    UIConnectionError,
    UIElementNotFoundError,
    UIInteractionError,
    UITimeoutError,
    UIValidationError
)

__all__ = [
    "UIBaseException",
    "UIConnectionError",
    "UIElementNotFoundError",
    "UIInteractionError",
    "UITimeoutError",
    "UIValidationError"
]