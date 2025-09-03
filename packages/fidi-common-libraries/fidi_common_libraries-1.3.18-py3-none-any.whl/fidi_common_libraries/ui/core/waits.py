"""
Utilitários para esperas e sincronização.

Fornece funcionalidades robustas de espera para diferentes condições
da interface do usuário, garantindo sincronização adequada.
"""

import logging
import time
from typing import Callable, Any, Optional, Union
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UITimeoutError, UIElementNotFoundError


logger = logging.getLogger(__name__)


class UIWaits:
    """
    Utilitários para esperas e sincronização em operações de UI.
    
    Fornece métodos para aguardar diferentes condições da interface,
    com timeouts configuráveis e tratamento de erros robusto.
    """
    
    def __init__(self):
        self.config = get_ui_config()
    
    def wait_for_element_ready(
        self, 
        element: HwndWrapper, 
        timeout: Optional[int] = None
    ) -> HwndWrapper:
        """
        Aguarda um elemento ficar pronto para interação.
        
        Args:
            element: Elemento a ser aguardado.
            timeout: Timeout em segundos. Se None, usa o padrão.
            
        Returns:
            HwndWrapper: Elemento pronto para interação.
            
        Raises:
            UITimeoutError: Se o elemento não ficar pronto no tempo esperado.
        """
        timeout = timeout or self.config.element_timeout
        
        try:
            logger.debug(f"Aguardando elemento ficar pronto (timeout: {timeout}s)")
            element.wait('ready', timeout=timeout)
            return element
        except Exception as e:
            error_msg = f"Elemento não ficou pronto em {timeout}s"
            logger.error(error_msg)
            raise UITimeoutError(error_msg, str(e))
    
    def wait_for_element_visible(
        self, 
        element: HwndWrapper, 
        timeout: Optional[int] = None
    ) -> HwndWrapper:
        """
        Aguarda um elemento ficar visível.
        
        Args:
            element: Elemento a ser aguardado.
            timeout: Timeout em segundos. Se None, usa o padrão.
            
        Returns:
            HwndWrapper: Elemento visível.
            
        Raises:
            UITimeoutError: Se o elemento não ficar visível no tempo esperado.
        """
        timeout = timeout or self.config.element_timeout
        
        try:
            logger.debug(f"Aguardando elemento ficar visível (timeout: {timeout}s)")
            element.wait('visible', timeout=timeout)
            return element
        except Exception as e:
            error_msg = f"Elemento não ficou visível em {timeout}s"
            logger.error(error_msg)
            raise UITimeoutError(error_msg, str(e))
    
    def wait_for_element_enabled(
        self, 
        element: HwndWrapper, 
        timeout: Optional[int] = None
    ) -> HwndWrapper:
        """
        Aguarda um elemento ficar habilitado.
        
        Args:
            element: Elemento a ser aguardado.
            timeout: Timeout em segundos. Se None, usa o padrão.
            
        Returns:
            HwndWrapper: Elemento habilitado.
            
        Raises:
            UITimeoutError: Se o elemento não ficar habilitado no tempo esperado.
        """
        timeout = timeout or self.config.element_timeout
        
        try:
            logger.debug(f"Aguardando elemento ficar habilitado (timeout: {timeout}s)")
            element.wait('enabled', timeout=timeout)
            return element
        except Exception as e:
            error_msg = f"Elemento não ficou habilitado em {timeout}s"
            logger.error(error_msg)
            raise UITimeoutError(error_msg, str(e))
    
    def wait_for_condition(
        self,
        condition_func: Callable[[], bool],
        timeout: Optional[int] = None,
        check_interval: float = 0.5,
        condition_description: str = "condição personalizada"
    ) -> bool:
        """
        Aguarda uma condição personalizada ser atendida.
        
        Args:
            condition_func: Função que retorna True quando a condição é atendida.
            timeout: Timeout em segundos. Se None, usa o padrão.
            check_interval: Intervalo entre verificações em segundos.
            condition_description: Descrição da condição para logs.
            
        Returns:
            bool: True se a condição foi atendida.
            
        Raises:
            UITimeoutError: Se a condição não for atendida no tempo esperado.
        """
        timeout = timeout or self.config.default_timeout
        start_time = time.time()
        
        logger.debug(f"Aguardando {condition_description} (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    logger.debug(f"Condição '{condition_description}' atendida")
                    return True
            except Exception as e:
                logger.debug(f"Erro ao verificar condição: {e}")
            
            time.sleep(check_interval)
        
        elapsed = time.time() - start_time
        error_msg = f"Timeout ({elapsed:.1f}s) aguardando {condition_description}"
        logger.error(error_msg)
        raise UITimeoutError(error_msg)
    
    def wait_for_window_to_appear(
        self,
        app,
        window_title: str,
        timeout: Optional[int] = None
    ):
        """
        Aguarda uma janela específica aparecer.
        
        Args:
            app: Instância da aplicação.
            window_title: Título da janela a ser aguardada.
            timeout: Timeout em segundos. Se None, usa o padrão.
            
        Returns:
            HwndWrapper: Janela encontrada.
            
        Raises:
            UITimeoutError: Se a janela não aparecer no tempo esperado.
        """
        timeout = timeout or self.config.default_timeout
        
        def window_exists():
            try:
                window = app.window(title=window_title)
                window.wait('ready', timeout=1)
                return window
            except (ElementNotFoundError, Exception):
                return None
        
        logger.info(f"Aguardando janela '{window_title}' aparecer")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            window = window_exists()
            if window:
                logger.info(f"Janela '{window_title}' encontrada")
                return window
            time.sleep(1)
        
        elapsed = time.time() - start_time
        error_msg = f"Janela '{window_title}' não apareceu em {elapsed:.1f}s"
        logger.error(error_msg)
        raise UITimeoutError(error_msg)
    
    def wait_for_window_to_disappear(
        self,
        app,
        window_title: str,
        timeout: Optional[int] = None
    ) -> bool:
        """
        Aguarda uma janela específica desaparecer.
        
        Args:
            app: Instância da aplicação.
            window_title: Título da janela.
            timeout: Timeout em segundos. Se None, usa o padrão.
            
        Returns:
            bool: True se a janela desapareceu.
            
        Raises:
            UITimeoutError: Se a janela não desaparecer no tempo esperado.
        """
        timeout = timeout or self.config.default_timeout
        
        def window_not_exists():
            try:
                app.window(title=window_title)
                return False
            except ElementNotFoundError:
                return True
        
        return self.wait_for_condition(
            window_not_exists,
            timeout,
            condition_description=f"janela '{window_title}' desaparecer"
        )