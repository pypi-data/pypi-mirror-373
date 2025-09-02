"""FIDI Common Libraries - Bibliotecas compartilhadas entre os projetos da FIDI.

Bibliotecas reutilizáveis para automação, integração AWS, processamento de dados
e utilitários comuns utilizados nos projetos da FIDI.
"""

__version__ = "1.3.17"
__author__ = "FIDI Team"

# Importações principais para facilitar o uso
from . import aws, config, constants, data, ui, utils

__all__ = ["aws", "config", "constants", "data", "ui", "utils"]