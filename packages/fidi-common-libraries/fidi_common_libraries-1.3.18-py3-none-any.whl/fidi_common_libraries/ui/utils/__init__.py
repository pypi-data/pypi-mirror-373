"""
Módulo de utilitários para automação de UI.

Este módulo contém funções e classes auxiliares para automação de UI,
incluindo captura de screenshots, validação de entradas e estados,
e outras ferramentas de suporte.
"""

from .screenshot import capture_screenshot, capture_screenshot_on_error
from .validation import validate_text_input, validate_element_state, validate_numeric_input

__all__ = [
    "capture_screenshot",
    "capture_screenshot_on_error",
    "validate_text_input",
    "validate_element_state",
    "validate_numeric_input"
]