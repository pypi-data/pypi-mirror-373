"""Módulo para fechamento de janelas e aplicações no sistema TOTVS RM.

Este módulo fornece funcionalidades para fechar janelas específicas e a aplicação
completa do sistema TOTVS RM de forma automatizada e segura.
"""

import logging
from typing import Optional
from pywinauto.keyboard import send_keys
from pywinauto.base_wrapper import BaseWrapper

from .rm_adapt_navigator import RMAdaptNavigator
from ..exceptions import UIElementNotFoundError, UIInteractionError
from ..utils.screenshot import capture_screenshot_on_error

logger = logging.getLogger(__name__)


class RMClose:
    """Classe para gerenciar o fechamento de janelas e aplicações no sistema TOTVS RM.
    
    Esta classe fornece métodos para fechar janelas específicas e a aplicação completa
    do sistema TOTVS RM, incluindo confirmações automáticas quando necessário.
    """
    
    def __init__(self, parent_element: BaseWrapper) -> None:
        """Inicializa o gerenciador de fechamento RM.
        
        Args:
            parent_element: Elemento pai (janela principal ou específica) para operações de fechamento.
        """
        self.parent_element = parent_element
        self.navigator = RMAdaptNavigator(parent_element)
        logger.info("RMClose inicializado")
    
    def close_window(self) -> bool:
        """Fecha a janela atual do sistema RM.
        
        Localiza e clica no botão "Fechar" da janela atual, seguido de confirmações
        automáticas via teclado para confirmar o fechamento.
        
        Returns:
            bool: True se a janela foi fechada com sucesso, False caso contrário.
            
        Raises:
            UIElementNotFoundError: Se o botão de fechar não for encontrado.
            UIInteractionError: Se houver erro durante a interação.
        """
        try:
            logger.info("Iniciando fechamento da janela atual")
            
            # Localiza e clica no botão Fechar
            close_button = self.navigator.navigate_to_element(
                title="Fechar", 
                control_type="Button", 
                click_element=True
            )
            
            if not close_button:
                raise UIElementNotFoundError("Botão 'Fechar' não encontrado")
            
            # Confirmações via teclado
            send_keys('{ENTER}')
            send_keys('{RIGHT}')
            send_keys('{ENTER}')
            
            logger.info("Janela fechada com sucesso")
            return True
            
        except Exception as e:
            error_msg = f"Erro ao fechar janela: {str(e)}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_close_window_error")
            
            if isinstance(e, (UIElementNotFoundError, UIInteractionError)):
                raise
            raise UIInteractionError(error_msg) from e
    
    def close_application(self) -> bool:
        """Fecha a aplicação completa do sistema TOTVS RM.
        
        Navega pela estrutura da aplicação para localizar o botão de fechar principal
        e executa o fechamento completo da aplicação com confirmações automáticas.
        
        Returns:
            bool: True se a aplicação foi fechada com sucesso, False caso contrário.
            
        Raises:
            UIElementNotFoundError: Se algum elemento necessário não for encontrado.
            UIInteractionError: Se houver erro durante a interação.
        """
        try:
            logger.info("Iniciando fechamento da aplicação RM")
            
            # Localiza o controle MDI Ribbon
            mdi_ribbon_control = self.navigator.navigate_to_element(
                title="mdiRibbonControl", 
                click_element=False
            )
            
            if not mdi_ribbon_control:
                raise UIElementNotFoundError("Controle 'mdiRibbonControl' não encontrado")
            
            # Localiza a barra de título com botões
            ribbon_navigator = RMAdaptNavigator(mdi_ribbon_control)
            ribbon_title_bar = ribbon_navigator.navigate_to_element(
                title="Ribbon Form Buttons", 
                control_type="TitleBar", 
                click_element=False
            )
            
            if not ribbon_title_bar:
                raise UIElementNotFoundError("Barra de título 'Ribbon Form Buttons' não encontrada")
            
            # Localiza e clica no botão Close
            title_bar_navigator = RMAdaptNavigator(ribbon_title_bar)
            close_button = title_bar_navigator.navigate_to_element(
                title="Close", 
                control_type="Button", 
                click_element=True
            )
            
            if not close_button:
                raise UIElementNotFoundError("Botão 'Close' não encontrado")
            
            # Confirmações via teclado
            send_keys('{ENTER}')
            send_keys('{RIGHT}')
            send_keys('{ENTER}')
            
            logger.info("Aplicação RM fechada com sucesso")
            return True
            
        except Exception as e:
            error_msg = f"Erro ao fechar aplicação RM: {str(e)}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_close_application_error")
            
            if isinstance(e, (UIElementNotFoundError, UIInteractionError)):
                raise
            raise UIInteractionError(error_msg) from e


# Funções de compatibilidade (deprecated)
def close_windows(window: BaseWrapper) -> bool:
    """Fecha a janela atual (função deprecated).
    
    Args:
        window: Janela a ser fechada.
        
    Returns:
        bool: True se fechada com sucesso.
        
    Note:
        Esta função está deprecated. Use RMClose.close_window() em vez disso.
    """
    import warnings
    warnings.warn(
        "close_windows() está deprecated. Use RMClose.close_window() em vez disso.",
        DeprecationWarning,
        stacklevel=2
    )
    
    closer = RMClose(window)
    return closer.close_window()


def close_app(main_window: BaseWrapper) -> bool:
    """Fecha a aplicação completa (função deprecated).
    
    Args:
        main_window: Janela principal da aplicação.
        
    Returns:
        bool: True se fechada com sucesso.
        
    Note:
        Esta função está deprecated. Use RMClose.close_application() em vez disso.
    """
    import warnings
    warnings.warn(
        "close_app() está deprecated. Use RMClose.close_application() em vez disso.",
        DeprecationWarning,
        stacklevel=2
    )
    
    closer = RMClose(main_window)
    return closer.close_application()