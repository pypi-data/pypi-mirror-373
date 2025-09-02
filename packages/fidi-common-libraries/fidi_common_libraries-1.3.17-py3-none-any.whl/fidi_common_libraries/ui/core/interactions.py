"""
Utilitários para interações com elementos da interface.

Fornece métodos seguros e robustos para interagir com elementos da UI,
incluindo cliques, digitação, seleção e outras operações comuns.
"""

import logging
import time
from typing import Optional, Union, List, Any
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.keyboard import send_keys

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIInteractionError
from .waits import UIWaits
from ..utils.screenshot import capture_screenshot_on_error
from ..utils.validation import validate_text_input, validate_element_state


logger = logging.getLogger(__name__)


class UIInteractions:
    """
    Utilitários para interações seguras com elementos da interface.
    
    Encapsula operações comuns de interação com a UI, fornecendo
    tratamento de erros robusto e logging detalhado.
    """
    
    def __init__(self):
        self.config = get_ui_config()
        self.waits = UIWaits()
    
    def safe_click(
        self,
        element: HwndWrapper,
        wait_before: Optional[float] = None,
        wait_after: Optional[float] = None,
        double_click: bool = False,
        right_click: bool = False,
        verify_enabled: bool = True
    ) -> None:
        """
        Realiza um clique seguro em um elemento.
        
        Args:
            element: Elemento a ser clicado.
            wait_before: Tempo de espera antes do clique.
            wait_after: Tempo de espera após o clique.
            double_click: Se deve realizar duplo clique.
            right_click: Se deve realizar clique direito.
            verify_enabled: Se deve verificar se o elemento está habilitado.
            
        Raises:
            UIInteractionError: Se o clique falhar.
        """
        wait_before = wait_before or self.config.wait_before_click
        wait_after = wait_after or self.config.wait_after_click
        
        try:
            # Validações pré-clique
            if verify_enabled:
                validate_element_state(element, enabled=True)
            
            self.waits.wait_for_element_ready(element)
            
            if wait_before > 0:
                time.sleep(wait_before)
            
            # Executa o clique apropriado
            if double_click:
                logger.debug("Executando duplo clique")
                element.double_click()
            elif right_click:
                logger.debug("Executando clique direito")
                element.right_click()
            else:
                logger.debug("Executando clique simples")
                element.click()
            
            if self.config.log_interactions:
                logger.info(f"Clique realizado com sucesso no elemento")
            
            if wait_after > 0:
                time.sleep(wait_after)
                
        except Exception as e:
            error_msg = f"Erro ao clicar no elemento"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("click_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def safe_type_text(
        self,
        element: HwndWrapper,
        text: str,
        clear_first: bool = True,
        with_spaces: bool = True,
        use_send_keys: bool = False,
        validate_input: bool = True
    ) -> None:
        """
        Digita texto em um elemento de forma segura.
        
        Args:
            element: Elemento onde digitar.
            text: Texto a ser digitado.
            clear_first: Se deve limpar o campo antes.
            with_spaces: Se deve preservar espaços.
            use_send_keys: Se deve usar send_keys em vez de type_keys.
            validate_input: Se deve validar a entrada.
            
        Raises:
            UIInteractionError: Se a digitação falhar.
        """
        try:
            if validate_input:
                validate_text_input(text)
                validate_element_state(element, enabled=True)
            
            self.waits.wait_for_element_ready(element)
            
            # Foca no elemento
            element.set_focus()
            
            if clear_first:
                self._clear_field(element)
            
            if not with_spaces:
                text = text.replace(" ", "")
            
            # Escolhe o método de digitação
            if use_send_keys:
                send_keys(text)
            else:
                element.type_keys(text, with_spaces=with_spaces)
            
            if self.config.log_interactions:
                logger.info(f"Texto digitado com sucesso: '{text[:20]}{'...' if len(text) > 20 else ''}'")
                
        except Exception as e:
            error_msg = f"Erro ao digitar texto"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("type_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def _clear_field(self, element: HwndWrapper) -> None:
        """Limpa um campo de texto."""
        try:
            # Tenta diferentes métodos de limpeza
            element.set_text("")
        except:
            try:
                element.select()
                send_keys("{DELETE}")
            except:
                send_keys("^a{DELETE}")
    
    def select_from_dropdown(
        self,
        dropdown_element: HwndWrapper,
        option_text: str,
        by_index: bool = False
    ) -> None:
        """
        Seleciona uma opção de um dropdown.
        
        Args:
            dropdown_element: Elemento dropdown.
            option_text: Texto da opção ou índice (se by_index=True).
            by_index: Se deve selecionar por índice.
            
        Raises:
            UIInteractionError: Se a seleção falhar.
        """
        try:
            self.waits.wait_for_element_ready(dropdown_element)
            
            if by_index:
                index = int(option_text)
                dropdown_element.select(index)
                logger.info(f"Opção selecionada por índice: {index}")
            else:
                dropdown_element.select(option_text)
                logger.info(f"Opção selecionada: '{option_text}'")
                
        except Exception as e:
            error_msg = f"Erro ao selecionar opção do dropdown"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("dropdown_selection_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def check_checkbox(
        self,
        checkbox_element: HwndWrapper,
        check: bool = True
    ) -> None:
        """
        Marca ou desmarca um checkbox.
        
        Args:
            checkbox_element: Elemento checkbox.
            check: True para marcar, False para desmarcar.
            
        Raises:
            UIInteractionError: Se a operação falhar.
        """
        try:
            self.waits.wait_for_element_ready(checkbox_element)
            
            current_state = checkbox_element.get_check_state()
            target_state = 1 if check else 0
            
            if current_state != target_state:
                checkbox_element.click()
                action = "marcado" if check else "desmarcado"
                logger.info(f"Checkbox {action} com sucesso")
            else:
                action = "já estava marcado" if check else "já estava desmarcado"
                logger.debug(f"Checkbox {action}")
                
        except Exception as e:
            error_msg = f"Erro ao {'marcar' if check else 'desmarcar'} checkbox"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("checkbox_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def scroll_element(
        self,
        element: HwndWrapper,
        direction: str = "down",
        clicks: int = 3
    ) -> None:
        """
        Realiza scroll em um elemento.
        
        Args:
            element: Elemento para fazer scroll.
            direction: Direção do scroll ("up", "down", "left", "right").
            clicks: Número de cliques do scroll.
            
        Raises:
            UIInteractionError: Se o scroll falhar.
        """
        try:
            self.waits.wait_for_element_ready(element)
            
            direction_map = {
                "up": "up",
                "down": "down", 
                "left": "left",
                "right": "right"
            }
            
            if direction not in direction_map:
                raise ValueError(f"Direção inválida: {direction}")
            
            element.scroll(direction_map[direction], "wheel", clicks)
            logger.debug(f"Scroll {direction} realizado com {clicks} cliques")
            
        except Exception as e:
            error_msg = f"Erro ao fazer scroll"
            logger.error(f"{error_msg}: {e}")
            raise UIInteractionError(error_msg, str(e))
    
    def drag_and_drop(
        self,
        source_element: HwndWrapper,
        target_element: HwndWrapper
    ) -> None:
        """
        Realiza operação de arrastar e soltar.
        
        Args:
            source_element: Elemento origem.
            target_element: Elemento destino.
            
        Raises:
            UIInteractionError: Se a operação falhar.
        """
        try:
            self.waits.wait_for_element_ready(source_element)
            self.waits.wait_for_element_ready(target_element)
            
            source_rect = source_element.rectangle()
            target_rect = target_element.rectangle()
            
            source_element.drag_mouse_input(
                dst=(target_rect.mid_point().x, target_rect.mid_point().y)
            )
            
            logger.info("Drag and drop realizado com sucesso")
            
        except Exception as e:
            error_msg = f"Erro ao realizar drag and drop"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("drag_drop_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def get_element_text(self, element: HwndWrapper) -> str:
        """
        Obtém o texto de um elemento.
        
        Args:
            element: Elemento para obter o texto.
            
        Returns:
            str: Texto do elemento.
            
        Raises:
            UIInteractionError: Se não conseguir obter o texto.
        """
        try:
            self.waits.wait_for_element_ready(element)
            
            # Tenta diferentes métodos para obter o texto
            try:
                return element.window_text()
            except:
                try:
                    return element.texts()[0] if element.texts() else ""
                except:
                    return element.get_value()
                    
        except Exception as e:
            error_msg = f"Erro ao obter texto do elemento"
            logger.error(f"{error_msg}: {e}")
            raise UIInteractionError(error_msg, str(e))