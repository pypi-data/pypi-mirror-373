"""Utilitários comuns para os projetos FIDI.

Este módulo fornece funções e classes utilitárias para os projetos FIDI,
incluindo sistema de logging estruturado para múltiplos SGBDs.
"""

from .logger import registrar_log_banco

__all__ = [
    'registrar_log_banco'
]