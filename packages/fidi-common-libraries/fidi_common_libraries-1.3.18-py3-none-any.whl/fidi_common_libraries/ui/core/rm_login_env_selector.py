"""
Seletor de ambiente para login RM.

Fornece funcionalidades para seleção automática de ambiente (HML/PROD)
na tela de login do sistema RM, seguindo os padrões do projeto.
"""

import logging
from typing import Tuple, Optional
from pywinauto import mouse
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import ElementNotFoundError

from ...config.parametros import Parametros
from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UIInteractionError
from ..utils.screenshot import capture_screenshot_on_error
from ..locators.locator_service import LocatorService, LocatorMode
from .waits import UIWaits


logger = logging.getLogger(__name__)


class RMLoginEnvSelector:
    """
    Seletor de ambiente para login RM.
    
    Fornece métodos para seleção automática de ambiente na tela de login
    do sistema RM, utilizando configurações de parâmetros e locators.
    """
    
    def __init__(self, login_window: HwndWrapper, locator_service: LocatorService):
        """
        Inicializa o seletor de ambiente.
        
        Args:
            login_window: Janela de login da aplicação RM.
            locator_service: Serviço de locators para obter coordenadas.
            
        Raises:
            ValueError: Se login_window ou locator_service forem None.
        """
        if login_window is None:
            raise ValueError("Parâmetro 'login_window' não pode ser None")
        if locator_service is None:
            raise ValueError("Parâmetro 'locator_service' não pode ser None")
            
        self.login_window = login_window
        self.locator_service = locator_service
        self.config = get_ui_config()
        self.waits = UIWaits()
    
    def select_environment(self, ambiente: str, produto: str) -> Tuple[bool, Optional[str]]:
        """
        Seleciona o ambiente na tela de login do RM.
        
        Args:
            ambiente: Ambiente desejado ('HML' ou 'PROD').
            produto: Nome do produto para buscar parâmetros.
            
        Returns:
            Tuple[bool, Optional[str]]:
                - (True, alias_selecionado) se seleção bem-sucedida
                - (False, None) se falhar
                
        Raises:
            UIElementNotFoundError: Se elemento não for encontrado.
            UIInteractionError: Se houver erro na interação.
            ValueError: Se parâmetros forem inválidos.
        """
        # Validação de parâmetros
        if not ambiente or ambiente.upper() not in ['HML', 'PROD']:
            raise ValueError("Ambiente deve ser 'HML' ou 'PROD'")
        if not produto:
            raise ValueError("Produto não pode ser vazio")
        
        try:
            logger.info(f"Iniciando seleção de ambiente: {ambiente} para produto: {produto}")
            
            # 1. Obter configurações via Parametros
            parametros = Parametros(ambiente=ambiente, produto=produto)
            hml_alias = parametros.get_parametro("HML_APP")
            prod_alias = parametros.get_parametro("PROD_APP")
            lista_ambientes_param = parametros.get_parametro("LISTA_AMBIENTES")
            
            if not lista_ambientes_param:
                raise ValueError("Parâmetro 'LISTA_AMBIENTES' não encontrado")
            
            # Verificar se já é lista ou se precisa fazer split
            # Corrigido na v1.3.8: compatibilidade com parâmetros que já são listas
            if isinstance(lista_ambientes_param, list):
                lista_ambientes = lista_ambientes_param
            else:
                lista_ambientes = [item.strip() for item in lista_ambientes_param.split(',')]
            
            # 2. Determinar alias esperado
            aliases = {'HML': hml_alias, 'PROD': prod_alias}
            expected_alias = aliases.get(ambiente.upper())
            
            if not expected_alias:
                raise ValueError(f"Alias não configurado para ambiente '{ambiente}'")
            
            logger.info(f"Selecionando ambiente: {expected_alias}")
            
            # 3. Obter coordenadas via LocatorService
            position = self.locator_service.get_position("rm_login_alias")
            if position is None:
                raise UIElementNotFoundError("Coordenadas do elemento 'rm_login_alias' não encontradas")
            
            combo_x, combo_y = position
            
            # 4. Clicar no ComboBox
            self._click_combo_box(combo_x, combo_y)
            
            # 5. Calcular posições dos itens da lista
            item_positions = self._calculate_item_positions(combo_x, combo_y, lista_ambientes)
            
            # 6. Selecionar o ambiente
            if expected_alias not in item_positions:
                raise ValueError(f"Ambiente '{expected_alias}' não encontrado na lista disponível")
            
            item_x, item_y = item_positions[expected_alias]
            self._click_environment_item(item_x, item_y, expected_alias)
            
            logger.info(f"Ambiente '{expected_alias}' selecionado com sucesso")
            return True, expected_alias
            
        except ElementNotFoundError as e:
            error_msg = f"Elemento não encontrado durante seleção de ambiente: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_env_selector_element_not_found")
            return False, None
            
        except Exception as e:
            error_msg = f"Erro durante seleção de ambiente: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_env_selector_failed")
            return False, None
    
    def _click_combo_box(self, x: int, y: int) -> None:
        """
        Clica no ComboBox de ambientes.
        
        Args:
            x: Coordenada X do ComboBox.
            y: Coordenada Y do ComboBox.
            
        Raises:
            UIInteractionError: Se houver erro ao clicar.
        """
        try:
            mouse.click(button='left', coords=(x, y))
            logger.debug(f"Clique realizado no ComboBox na posição ({x}, {y})")
            
            # Aguarda a lista abrir
            import time
            time.sleep(0.5)
            
        except Exception as e:
            raise UIInteractionError(f"Erro ao clicar no ComboBox", str(e))
    
    def _calculate_item_positions(self, combo_x: int, combo_y: int, lista_ambientes: list) -> dict:
        """
        Calcula as posições dos itens na lista dropdown.
        
        Args:
            combo_x: Coordenada X do ComboBox.
            combo_y: Coordenada Y do ComboBox.
            lista_ambientes: Lista de ambientes disponíveis.
            
        Returns:
            dict: Dicionário com ambiente -> (x, y) das posições.
        """
        # Parâmetros de layout da lista dropdown
        first_item_offset = 25  # Offset do primeiro item em relação ao ComboBox
        item_height = 20        # Altura de cada item na lista
        
        positions = {}
        for idx, ambiente in enumerate(lista_ambientes):
            item_x = combo_x
            item_y = combo_y + first_item_offset + (idx * item_height)
            positions[ambiente] = (item_x, item_y)
        
        logger.debug(f"Posições calculadas para {len(positions)} ambientes")
        return positions
    
    def _click_environment_item(self, x: int, y: int, ambiente: str) -> None:
        """
        Clica no item do ambiente na lista dropdown.
        
        Args:
            x: Coordenada X do item.
            y: Coordenada Y do item.
            ambiente: Nome do ambiente sendo selecionado.
            
        Raises:
            UIInteractionError: Se houver erro ao clicar.
        """
        try:
            mouse.click(button='left', coords=(x, y))
            logger.debug(f"Ambiente '{ambiente}' clicado na posição ({x}, {y})")
            
            # Aguarda a seleção efetivar
            import time
            time.sleep(0.5)
            
        except Exception as e:
            raise UIInteractionError(f"Erro ao clicar no ambiente '{ambiente}'", str(e))
