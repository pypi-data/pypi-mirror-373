"""Módulo para gerenciamento de configurações e parâmetros.

Este módulo fornece funcionalidades para gerenciamento de configurações e parâmetros
do sistema de RPA para a FIDI, com suporte a cache, tipagem forte e tratamento
de parâmetros sensíveis.
"""

from .parametros import Parametros

__all__ = [
    'Parametros'
]