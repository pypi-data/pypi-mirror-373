"""Módulo para navegação e seleção da Planilha Net no sistema TOTVS RM.

Este módulo fornece funcionalidades para navegar pelos filtros da Planilha Net
e selecionar planilhas específicas no sistema TOTVS RM.
"""

import logging
import time
from typing import Optional
from pywinauto.keyboard import send_keys
from pywinauto.base_wrapper import BaseWrapper
from pywinauto import mouse

from .rm_adapt_navigator import RMAdaptNavigator
from ..exceptions import UIElementNotFoundError, UIInteractionError
from ..utils.screenshot import capture_screenshot_on_error
from .waits import UIWaits

logger = logging.getLogger(__name__)


class RMPlanilhaNet:
    """Classe para gerenciar navegação e seleção da Planilha Net no sistema TOTVS RM.
    
    Esta classe fornece métodos para navegar pelos filtros da Planilha Net
    e selecionar planilhas específicas de forma automatizada.
    """
    
    def __init__(self, parent_element: BaseWrapper, app: Optional[BaseWrapper] = None, id_planilha: Optional[str] = None) -> None:
        """Inicializa o gerenciador da Planilha Net.
        
        Args:
            parent_element: Elemento pai para operações na Planilha Net.
            app: Aplicação RM (opcional, para execução automática).
            id_planilha: ID da planilha (opcional, para execução automática).
        """
        self.parent_element = parent_element
        self.navigator = RMAdaptNavigator(parent_element)
        self.waits = UIWaits()
        self.app = app
        self.id_planilha = id_planilha
        logger.info("RMPlanilhaNet inicializado")
        
        # Se app e id_planilha foram fornecidos, executa o processo completo
        if self.app and self.id_planilha:
            self.execute_full_process()
    
    def execute_full_process(self, app: Optional[BaseWrapper] = None, id_planilha: Optional[str] = None, timeout: int = 60) -> bool:
        """Executa o processo completo: navega pelos filtros e seleciona a planilha.
        
        Args:
            app: Aplicação RM (usa o app do construtor se não fornecido).
            id_planilha: ID da planilha (usa o id_planilha do construtor se não fornecido).
            timeout: Tempo limite para aguardar a janela de filtros (segundos).
            
        Returns:
            bool: True se todo o processo foi executado com sucesso, False caso contrário.
            
        Raises:
            UIElementNotFoundError: Se algum elemento necessário não for encontrado.
            UIInteractionError: Se houver erro durante a interação.
        """
        try:
            # Usa os parâmetros fornecidos ou os do construtor
            app_to_use = app or self.app
            id_to_use = id_planilha or self.id_planilha
            
            if not app_to_use:
                raise UIInteractionError("App não fornecido nem no construtor nem no método")
            
            if not id_to_use:
                raise UIInteractionError("ID da planilha não fornecido nem no construtor nem no método")
            
            logger.info(f"Executando processo completo da Planilha Net para: {id_to_use}")
            
            # Passo 1: Navegar pelos filtros
            if not self.navigate_filters(app_to_use, timeout):
                return False
            
            # Passo 2: Selecionar a planilha
            if not self.select_planilha(id_to_use):
                return False
            
            logger.info(f"Processo completo da Planilha Net executado com sucesso para: {id_to_use}")
            return True
            
        except Exception as e:
            error_msg = f"Erro no processo completo da Planilha Net: {str(e)}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_planilha_net_full_process_error")
            
            if isinstance(e, (UIElementNotFoundError, UIInteractionError)):
                raise
            raise UIInteractionError(error_msg) from e
    
    def navigate_filters(self, app: BaseWrapper, timeout: int = 60) -> bool:
        """Navega pelos filtros da Planilha Net e seleciona 'Todos'.
        
        Args:
            app: Aplicação RM para localizar a janela de filtros.
            timeout: Tempo limite para aguardar a janela de filtros (segundos).
            
        Returns:
            bool: True se a navegação foi bem-sucedida, False caso contrário.
            
        Raises:
            UIElementNotFoundError: Se a janela de filtros não for encontrada.
            UIInteractionError: Se houver erro durante a interação.
        """
        try:
            logger.info("Iniciando navegação pelos filtros da Planilha Net")
            
            # Aguarda a janela de filtros aparecer
            start_time = time.time()
            filtros_window = None
            
            while time.time() - start_time < timeout:
                try:
                    filtros_window = app.window(title="Filtros - Planilha Net")
                    if filtros_window.exists():
                        break
                except:
                    pass
                time.sleep(1)
            
            if not filtros_window or not filtros_window.exists():
                raise UIElementNotFoundError("Janela 'Filtros - Planilha Net' não encontrada")
            
            # Navega para selecionar 'Todos'
            send_keys('{LEFT}')
            time.sleep(0.1)
            send_keys('{SPACE}')
            time.sleep(0.1)
            send_keys('{ENTER}')
            time.sleep(0.1)
            
            logger.info("Filtros da Planilha Net configurados com sucesso")
            return True
            
        except Exception as e:
            error_msg = f"Erro ao navegar pelos filtros da Planilha Net: {str(e)}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_planilha_net_filters_error")
            
            if isinstance(e, (UIElementNotFoundError, UIInteractionError)):
                raise
            raise UIInteractionError(error_msg) from e
    
    def select_planilha(self, id_planilha: str) -> bool:
        """Seleciona uma planilha específica na Planilha Net.
        
        Args:
            id_planilha: ID da planilha a ser selecionada.
            
        Returns:
            bool: True se a planilha foi selecionada com sucesso, False caso contrário.
            
        Raises:
            UIElementNotFoundError: Se algum elemento necessário não for encontrado.
            UIInteractionError: Se houver erro durante a interação.
        """
        try:
            logger.info(f"Iniciando seleção da planilha: {id_planilha}")
            
            # Localiza a aba Planilhas
            planilhas_tab = self.navigator.navigate_to_element(
                title="Planilhas",
                control_type="Tab",
                click_element=False
            )
            
            if not planilhas_tab:
                raise UIElementNotFoundError("Aba 'Planilhas' não encontrada")
            
            # Localiza o formulário da Planilha Net
            form_view = self.navigator.navigate_to_element(
                auto_id="GlbPlanilhaNetFormView",
                control_type="Window",
                click_element=False
            )
            
            if not form_view:
                raise UIElementNotFoundError("Formulário 'GlbPlanilhaNetFormView' não encontrado")
            
            # Navega para a toolbar
            form_navigator = RMAdaptNavigator(form_view)
            toolbar_pane = form_navigator.navigate_to_element(
                title="RMSToolBar",
                control_type="Pane",
                click_element=False
            )
            
            if not toolbar_pane:
                raise UIElementNotFoundError("Painel 'RMSToolBar' não encontrado")
            
            # Localiza a toolbar
            toolbar_navigator = RMAdaptNavigator(toolbar_pane)
            toolbar = toolbar_navigator.navigate_to_element(
                auto_id="toolBar",
                control_type="ToolBar",
                click_element=False
            )
            
            if not toolbar:
                raise UIElementNotFoundError("ToolBar não encontrada")
            
            # Localiza o botão "Próxima Página" para referência de posição
            toolbar_nav = RMAdaptNavigator(toolbar)
            proxima_pagina = toolbar_nav.navigate_to_element(
                title="Próxima Página",
                control_type="Button",
                click_element=False
            )
            
            if proxima_pagina:
                # Clica ao lado do botão para posicionamento
                rect = proxima_pagina.rectangle()
                offset = 50
                x = rect.right + offset
                y = (rect.top + rect.bottom) // 2
                mouse.click(button='left', coords=(x, y))
            
            # Localiza e preenche a barra de pesquisa
            search_bar = toolbar_nav.navigate_to_element(
                auto_id="tbxSearch",
                control_type="ComboBox",
                click_element=False
            )
            
            if not search_bar:
                raise UIElementNotFoundError("Barra de pesquisa não encontrada")
            
            search_bar.draw_outline()
            search_bar.set_focus()
            send_keys(id_planilha)
            
            # Clica no botão de pesquisa
            search_button = toolbar_nav.navigate_to_element(
                auto_id="btnSearch",
                control_type="Button",
                click_element=True
            )
            
            if not search_button:
                raise UIElementNotFoundError("Botão de pesquisa não encontrado")
            
            # Ativa o filtro de pesquisa
            filter_button = toolbar_nav.navigate_to_element(
                auto_id="chkFilterOnSearch",
                control_type="Button",
                click_element=True
            )
            
            if not filter_button:
                raise UIElementNotFoundError("Botão de filtro não encontrado")
            
            # Navega para o painel de dados
            panel_client = form_navigator.navigate_to_element(
                auto_id="panelClient",
                control_type="Pane",
                click_element=False
            )
            
            if not panel_client:
                raise UIElementNotFoundError("Painel de cliente não encontrado")
            
            # Localiza a árvore de dados
            panel_navigator = RMAdaptNavigator(panel_client)
            tree_list = panel_navigator.navigate_to_element(
                title="treeList",
                auto_id="treeList",
                control_type="Tree",
                click_element=False
            )
            
            if not tree_list:
                raise UIElementNotFoundError("Lista em árvore não encontrada")
            
            # Localiza o grupo de dados
            tree_navigator = RMAdaptNavigator(tree_list)
            data_group = tree_navigator.navigate_to_element(
                title="Painel de dados",
                control_type="Group",
                click_element=False
            )
            
            if not data_group:
                raise UIElementNotFoundError("Grupo de dados não encontrado")
            
            # Localiza e clica duplo no item Nó0
            group_navigator = RMAdaptNavigator(data_group)
            no0_item = group_navigator.navigate_to_element(
                title="Nó0",
                control_type="TreeItem",
                click_element=False
            )
            
            if not no0_item:
                raise UIElementNotFoundError("Item 'Nó0' não encontrado")
            
            # Clique duplo no item
            no0_item.draw_outline()
            no0_item.click_input(double=True)
            
            logger.info(f"Planilha '{id_planilha}' selecionada com sucesso")
            return True
            
        except Exception as e:
            error_msg = f"Erro ao selecionar planilha '{id_planilha}': {str(e)}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_planilha_net_select_error")
            
            if isinstance(e, (UIElementNotFoundError, UIInteractionError)):
                raise
            raise UIInteractionError(error_msg) from e


# Funções de compatibilidade (deprecated)
def navigate_filters_planilha_net(app: BaseWrapper) -> bool:
    """Navega pelos filtros da Planilha Net (função deprecated).
    
    Args:
        app: Aplicação RM.
        
    Returns:
        bool: True se navegação foi bem-sucedida.
        
    Note:
        Esta função está deprecated. Use RMPlanilhaNet.navigate_filters() em vez disso.
    """
    import warnings
    warnings.warn(
        "navigate_filters_planilha_net() está deprecated. Use RMPlanilhaNet.navigate_filters() em vez disso.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Usa uma janela temporária para criar a instância
    temp_window = app.top_window()
    planilha_net = RMPlanilhaNet(temp_window)
    return planilha_net.navigate_filters(app)


def select_planilha_net(window: BaseWrapper, id_planilha: str) -> bool:
    """Seleciona uma planilha na Planilha Net (função deprecated).
    
    Args:
        window: Janela da aplicação.
        id_planilha: ID da planilha.
        
    Returns:
        bool: True se seleção foi bem-sucedida.
        
    Note:
        Esta função está deprecated. Use RMPlanilhaNet.select_planilha() em vez disso.
    """
    import warnings
    warnings.warn(
        "select_planilha_net() está deprecated. Use RMPlanilhaNet.select_planilha() em vez disso.",
        DeprecationWarning,
        stacklevel=2
    )
    
    planilha_net = RMPlanilhaNet(window)
    return planilha_net.select_planilha(id_planilha)