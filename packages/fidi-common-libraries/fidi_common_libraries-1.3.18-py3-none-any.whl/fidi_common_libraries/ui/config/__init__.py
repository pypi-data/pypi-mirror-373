"""
Módulo de configuração para automação de UI.

Este módulo contém classes e funções para configurar e personalizar
o comportamento da automação de UI, incluindo timeouts, estratégias de espera,
e configurações específicas para aplicações.
"""

from .ui_config import UIConfig, get_ui_config

__all__ = ["UIConfig", "get_ui_config"]