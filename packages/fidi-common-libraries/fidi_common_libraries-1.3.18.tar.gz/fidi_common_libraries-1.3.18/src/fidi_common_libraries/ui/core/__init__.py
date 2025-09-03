"""
Módulo core para automação de UI.

Este módulo contém as classes e funções principais para interação com interfaces gráficas,
incluindo gerenciamento de aplicações, localização de elementos, interações com elementos,
mecanismos de espera, localização por posição e reconhecimento de imagem.
"""

from .application import RMApplication
from .element_finder import ElementFinder
from .interactions import UIInteractions
from .waits import UIWaits
from .position_finder import PositionFinder, ScreenRegion, PositionReference
from .image_finder import ImageFinder, ImageMatchResult
from .rm_navigator import RMNavigator
from .rm_login_env_selector import RMLoginEnvSelector
from .rm_dual_connect import RMDualConnect
from .rm_start_login import RMStartLogin
from .rm_progress_monitor import RMProgressMonitor
from .rm_adapt_navigator import RMAdaptNavigator
from .rm_close import RMClose
from .rm_planilha_net import RMPlanilhaNet
from .rm_single_connect import RMSingleConnect, connect_single

__all__ = [
    "RMApplication",
    "ElementFinder",
    "UIInteractions",
    "UIWaits",
    "PositionFinder",
    "ScreenRegion",
    "PositionReference",
    "ImageFinder",
    "ImageMatchResult",
    "RMNavigator",
    "RMLoginEnvSelector",
    "RMDualConnect",
    "RMStartLogin",
    "RMProgressMonitor",
    "RMAdaptNavigator",
    "RMClose",
    "RMPlanilhaNet",
    "RMSingleConnect",
    "connect_single"
]