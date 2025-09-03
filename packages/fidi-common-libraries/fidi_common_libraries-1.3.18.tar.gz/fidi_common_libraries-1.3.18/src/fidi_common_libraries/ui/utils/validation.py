"""
Utilitários para validação de entradas e estados.

Fornece funções para validar dados de entrada e estados de elementos
antes de realizar operações, prevenindo erros e melhorando a robustez.
"""

import logging
from typing import Any, Optional
from pywinauto.controls.hwndwrapper import HwndWrapper

from ..exceptions.ui_exceptions import UIValidationError


logger = logging.getLogger(__name__)


def validate_text_input(text: str, max_length: Optional[int] = None) -> None:
    """
    Valida entrada de texto.
    
    Args:
        text: Texto a ser validado.
        max_length: Comprimento máximo permitido.
        
    Raises:
        UIValidationError: Se a validação falhar.
    """
    if not isinstance(text, str):
        raise UIValidationError("Texto deve ser uma string")
    
    if max_length and len(text) > max_length:
        raise UIValidationError(f"Texto excede o comprimento máximo de {max_length} caracteres")
    
    # Verifica caracteres problemáticos
    problematic_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05']
    for char in problematic_chars:
        if char in text:
            raise UIValidationError(f"Texto contém caractere problemático: {repr(char)}")


def validate_element_state(
    element: HwndWrapper,
    enabled: Optional[bool] = None,
    visible: Optional[bool] = None,
    exists: Optional[bool] = None
) -> None:
    """
    Valida o estado de um elemento.
    
    Args:
        element: Elemento a ser validado.
        enabled: Se deve estar habilitado.
        visible: Se deve estar visível.
        exists: Se deve existir.
        
    Raises:
        UIValidationError: Se a validação falhar.
    """
    try:
        if exists is not None:
            element_exists = element.exists()
            if exists and not element_exists:
                raise UIValidationError("Elemento deveria existir mas não existe")
            elif not exists and element_exists:
                raise UIValidationError("Elemento não deveria existir mas existe")
        
        if enabled is not None:
            element_enabled = element.is_enabled()
            if enabled and not element_enabled:
                raise UIValidationError("Elemento deveria estar habilitado mas está desabilitado")
            elif not enabled and element_enabled:
                raise UIValidationError("Elemento deveria estar desabilitado mas está habilitado")
        
        if visible is not None:
            element_visible = element.is_visible()
            if visible and not element_visible:
                raise UIValidationError("Elemento deveria estar visível mas está oculto")
            elif not visible and element_visible:
                raise UIValidationError("Elemento deveria estar oculto mas está visível")
                
    except Exception as e:
        if isinstance(e, UIValidationError):
            raise
        logger.error(f"Erro ao validar estado do elemento: {e}")
        raise UIValidationError(f"Erro na validação do elemento: {e}")


def validate_numeric_input(
    value: Any,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_negative: bool = True
) -> float:
    """
    Valida entrada numérica.
    
    Args:
        value: Valor a ser validado.
        min_value: Valor mínimo permitido.
        max_value: Valor máximo permitido.
        allow_negative: Se permite valores negativos.
        
    Returns:
        float: Valor validado convertido para float.
        
    Raises:
        UIValidationError: Se a validação falhar.
    """
    try:
        # Tenta converter para float
        float_value = float(value)
        
        # Verifica se é negativo quando não permitido
        if not allow_negative and float_value < 0:
            raise UIValidationError("Valores negativos não são permitidos")
        
        # Verifica valor mínimo
        if min_value is not None and float_value < min_value:
            raise UIValidationError(f"Valor {float_value} é menor que o mínimo permitido {min_value}")
        
        # Verifica valor máximo
        if max_value is not None and float_value > max_value:
            raise UIValidationError(f"Valor {float_value} é maior que o máximo permitido {max_value}")
        
        return float_value
        
    except ValueError:
        raise UIValidationError(f"Valor '{value}' não pode ser convertido para número")
    except Exception as e:
        if isinstance(e, UIValidationError):
            raise
        logger.error(f"Erro ao validar entrada numérica: {e}")
        raise UIValidationError(f"Erro na validação numérica: {e}")