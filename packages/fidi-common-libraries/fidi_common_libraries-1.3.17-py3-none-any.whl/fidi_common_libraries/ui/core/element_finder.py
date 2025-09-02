"""
Utilitários para localização de elementos na interface.

Fornece funcionalidades robustas para encontrar elementos da UI
com múltiplos critérios e estratégias de fallback.
"""

import logging
from typing import Any, Dict, Optional, List, Union
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError
from .waits import UIWaits
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


class ElementFinder:
    """
    Localizador robusto de elementos da interface.
    
    Fornece métodos para encontrar elementos com múltiplos critérios,
    estratégias de fallback e tratamento de erros abrangente.
    """
    
    def __init__(self):
        self.config = get_ui_config()
        self.waits = UIWaits()
    
    def find_element(
        self,
        parent: HwndWrapper,
        primary_criteria: Dict[str, Any],
        fallback_criteria: Optional[List[Dict[str, Any]]] = None,
        wait_for_ready: bool = True,
        timeout: Optional[int] = None
    ) -> HwndWrapper:
        """
        Encontra um elemento usando critérios primários e de fallback.
        
        Args:
            parent: Elemento pai onde buscar.
            primary_criteria: Critérios primários para localização.
            fallback_criteria: Lista de critérios alternativos.
            wait_for_ready: Se deve aguardar o elemento ficar pronto.
            timeout: Timeout para a operação.
            
        Returns:
            HwndWrapper: Elemento encontrado.
            
        Raises:
            UIElementNotFoundError: Se o elemento não for encontrado.
        """
        timeout = timeout or self.config.element_timeout
        all_criteria = [primary_criteria]
        
        if fallback_criteria:
            all_criteria.extend(fallback_criteria)
        
        last_error = None
        
        for i, criteria in enumerate(all_criteria):
            try:
                logger.debug(f"Tentativa {i+1}: Buscando elemento com critérios: {criteria}")
                element = self._find_with_retry(parent, criteria, timeout)
                
                if wait_for_ready:
                    element = self.waits.wait_for_element_ready(element, timeout)
                
                logger.debug(f"Elemento encontrado com critérios: {criteria}")
                return element
                
            except Exception as e:
                last_error = e
                logger.debug(f"Critérios {criteria} falharam: {e}")
                continue
        
        # Se chegou aqui, nenhum critério funcionou
        error_msg = f"Elemento não encontrado com nenhum dos critérios fornecidos"
        logger.error(error_msg)
        capture_screenshot_on_error("element_not_found")
        raise UIElementNotFoundError(error_msg, str(last_error))
    
    def _find_with_retry(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: int
    ) -> HwndWrapper:
        """
        Encontra elemento com tentativas de retry.
        
        Args:
            parent: Elemento pai.
            criteria: Critérios de busca.
            timeout: Timeout total.
            
        Returns:
            HwndWrapper: Elemento encontrado.
        """
        import time
        
        start_time = time.time()
        last_error = None
        
        while time.time() - start_time < timeout:
            try:
                element = parent.child_window(**criteria)
                # Tenta uma operação simples para verificar se o elemento é válido
                _ = element.exists()
                return element
            except Exception as e:
                last_error = e
                time.sleep(0.5)
        
        raise last_error or ElementNotFoundError(f"Elemento não encontrado: {criteria}")
    
    def find_elements(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> List[HwndWrapper]:
        """
        Encontra múltiplos elementos que correspondem aos critérios.
        
        Args:
            parent: Elemento pai onde buscar.
            criteria: Critérios para localização.
            timeout: Timeout para a operação.
            
        Returns:
            List[HwndWrapper]: Lista de elementos encontrados.
        """
        timeout = timeout or self.config.element_timeout
        
        try:
            logger.debug(f"Buscando múltiplos elementos com critérios: {criteria}")
            elements = parent.children(**criteria)
            logger.debug(f"Encontrados {len(elements)} elementos")
            return elements
        except Exception as e:
            logger.error(f"Erro ao buscar múltiplos elementos: {e}")
            return []
    
    def element_exists(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: int = 5
    ) -> bool:
        """
        Verifica se um elemento existe sem lançar exceção.
        
        Args:
            parent: Elemento pai onde buscar.
            criteria: Critérios para localização.
            timeout: Timeout para verificação.
            
        Returns:
            bool: True se o elemento existe, False caso contrário.
        """
        try:
            self._find_with_retry(parent, criteria, timeout)
            return True
        except Exception:
            return False
    
    def wait_for_element_to_appear(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> HwndWrapper:
        """
        Aguarda um elemento aparecer na interface.
        
        Args:
            parent: Elemento pai onde buscar.
            criteria: Critérios para localização.
            timeout: Timeout para a operação.
            
        Returns:
            HwndWrapper: Elemento encontrado.
            
        Raises:
            UIElementNotFoundError: Se o elemento não aparecer no tempo esperado.
        """
        timeout = timeout or self.config.default_timeout
        
        def element_appears():
            return self.element_exists(parent, criteria, timeout=1)
        
        logger.debug(f"Aguardando elemento aparecer: {criteria}")
        
        if self.waits.wait_for_condition(
            element_appears,
            timeout,
            condition_description=f"elemento {criteria} aparecer"
        ):
            return self.find_element(parent, criteria, wait_for_ready=True)
    
    def wait_for_element_to_disappear(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> bool:
        """
        Aguarda um elemento desaparecer da interface.
        
        Args:
            parent: Elemento pai onde buscar.
            criteria: Critérios para localização.
            timeout: Timeout para a operação.
            
        Returns:
            bool: True se o elemento desapareceu.
        """
        timeout = timeout or self.config.default_timeout
        
        def element_disappears():
            return not self.element_exists(parent, criteria, timeout=1)
        
        logger.debug(f"Aguardando elemento desaparecer: {criteria}")
        
        return self.waits.wait_for_condition(
            element_disappears,
            timeout,
            condition_description=f"elemento {criteria} desaparecer"
        )