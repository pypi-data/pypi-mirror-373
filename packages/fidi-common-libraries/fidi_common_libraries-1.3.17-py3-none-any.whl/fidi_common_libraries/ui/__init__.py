"""
Biblioteca de Interação com Interface do Usuário para Sistema RM.

Esta biblioteca encapsula operações comuns do Pywinauto para tornar o código
mais robusto, legível e manutenível, seguindo as melhores práticas de automação de UI.

"""

from .core.application import RMApplication
from .core.element_finder import ElementFinder
from .core.interactions import UIInteractions
from .core.waits import UIWaits
from .core.position_finder import PositionFinder, ScreenRegion, PositionReference
from .core.image_finder import ImageFinder, ImageMatchResult
from .core.rm_navigator import RMNavigator
from .core.rm_login_env_selector import RMLoginEnvSelector
from .core.rm_dual_connect import RMDualConnect
from .core.rm_start_login import RMStartLogin
from .core.rm_progress_monitor import RMProgressMonitor
from .core.rm_adapt_navigator import RMAdaptNavigator, RMAdaptativeNavigator
from .core.rm_close import RMClose
from .core.rm_planilha_net import RMPlanilhaNet
from .core.rm_single_connect import RMSingleConnect, connect_single
from .locators.locator_service import LocatorService, LocatorMode
from .exceptions.ui_exceptions import (
    UIConnectionError,
    UIElementNotFoundError,
    UIInteractionError,
    UITimeoutError
)

__version__ = "1.3.17"
__all__ = [
    "RMApplication",
    "ElementFinder", 
    "UIInteractions",
    "UIWaits",
    "PositionFinder",
    "ImageFinder",
    "RMNavigator",
    "RMLoginEnvSelector",
    "RMDualConnect",
    "RMStartLogin",
    "RMProgressMonitor",
    "RMAdaptNavigator",
    "RMAdaptativeNavigator",
    "RMClose",
    "RMPlanilhaNet",
    "RMSingleConnect",
    "connect_single",
    "LocatorService",
    "LocatorMode",
    "ScreenRegion",
    "PositionReference",
    "ImageMatchResult",
    "UIConnectionError",
    "UIElementNotFoundError", 
    "UIInteractionError",
    "UITimeoutError"
]