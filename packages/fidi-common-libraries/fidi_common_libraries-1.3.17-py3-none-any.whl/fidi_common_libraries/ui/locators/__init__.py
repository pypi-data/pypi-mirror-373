"""
Módulo de locators para automação de UI.

Este módulo contém mapeamentos de elementos da interface do usuário,
organizados por aplicação e tela, facilitando a manutenção e atualização
dos identificadores de elementos. Inclui serviços para carregamento
e consulta de locators a partir de arquivos YAML.
"""

from .locator_service import LocatorService, LocatorMode

__all__ = ["LocatorService", "LocatorMode"]