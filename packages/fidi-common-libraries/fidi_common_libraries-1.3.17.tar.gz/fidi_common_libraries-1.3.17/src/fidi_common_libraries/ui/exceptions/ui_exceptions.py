"""
Exceções customizadas para operações de UI.

Define exceções específicas para diferentes tipos de falhas na automação de UI,
permitindo tratamento de erros mais granular e informativo.
"""


class UIBaseException(Exception):
    """Exceção base para todas as operações de UI."""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class UIConnectionError(UIBaseException):
    """Exceção para falhas de conexão com a aplicação."""
    pass


class UIElementNotFoundError(UIBaseException):
    """Exceção para elementos não encontrados na interface."""
    pass


class UIInteractionError(UIBaseException):
    """Exceção para falhas durante interações com elementos."""
    pass


class UITimeoutError(UIBaseException):
    """Exceção para timeouts em operações de UI."""
    pass


class UIValidationError(UIBaseException):
    """Exceção para falhas de validação de entrada."""
    pass