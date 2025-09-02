"""Módulo de acesso a dados para o sistema de RPA para a FIDI.

Este módulo implementa classes e funções para acesso a bancos de dados,
incluindo configuração de conexão, operações CRUD e consultas com proteção
contra SQL injection.
"""

from .db_data import (
    DatabaseConfig,
    DatabaseOperations,
    ProcessosRpaInserter,
    ProcessosRpaUpdater,
    DatabaseQuery,
    ProcedureExecutor,
    ProcedureHelpers
)

__all__ = [
    'DatabaseConfig',
    'DatabaseOperations',
    'ProcessosRpaInserter',
    'ProcessosRpaUpdater',
    'DatabaseQuery',
    'ProcedureExecutor',
    'ProcedureHelpers'
]