"""Constantes e enums compartilhados para o projeto FIDI.

Este módulo centraliza constantes e enumeradores utilizados em diferentes
contextos do projeto, facilitando a manutenção e garantindo consistência.
"""

from .status import (
    DBStatus,
    LogStatus,
    HubStatus,
    convert_status,
    HUB_TO_LOG_MAP,
    LOG_TO_HUB_MAP,
    DB_TO_LOG_MAP
)

__all__ = [
    'DBStatus',
    'LogStatus',
    'HubStatus',
    'convert_status',
    'HUB_TO_LOG_MAP',
    'LOG_TO_HUB_MAP',
    'DB_TO_LOG_MAP'
]