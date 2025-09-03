"""
Módulo de automação da Planilha Net no sistema TOTVS RM.

Este módulo fornece a classe RMPlanilhaNet que implementa automação completa
da funcionalidade Planilha Net do sistema TOTVS RM, incluindo navegação pelos
filtros, pesquisa e seleção de planilhas específicas.

A Planilha Net é uma funcionalidade do TOTVS RM que permite visualizar e
gerenciar planilhas de dados. Este módulo automatiza o processo de:
1. Navegação pelos filtros (seleção de "Todos")
2. Pesquisa por ID de planilha específica
3. Seleção e abertura da planilha encontrada

Classes:
    RMPlanilhaNet: Classe principal para automação da Planilha Net

Funções:
    navigate_filters_planilha_net: Função de compatibilidade (deprecated)
    select_planilha_net: Função de compatibilidade (deprecated)

Exemplo:
    Uso básico com execução automática:
    
    >>> planilha_net = RMPlanilhaNet(main_window, app, "PLAN001")
    # Executa automaticamente navegação e seleção
    
    Uso manual passo a passo:
    
    >>> planilha_net = RMPlanilhaNet(main_window)
    >>> success = planilha_net.navigate_filters(app, timeout=60)
    >>> if success:
    ...     success = planilha_net.select_planilha("PLAN001")
"""

import logging
import time
from typing import Optional
from pywinauto.keyboard import send_keys
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.controls.hwndwrapper import HwndWrapper
from typing import Union
from pywinauto import mouse

from .rm_adapt_navigator import RMAdaptNavigator
from ..exceptions import UIElementNotFoundError, UIInteractionError
from ..utils.screenshot import capture_screenshot_on_error
from .waits import UIWaits

logger = logging.getLogger(__name__)


class RMPlanilhaNet:
    """
    Classe para automação completa da Planilha Net no sistema TOTVS RM.
    
    Esta classe implementa automação robusta da funcionalidade Planilha Net,
    fornecendo três formas de uso: execução automática no construtor,
    execução manual passo a passo, ou execução completa sob demanda.
    
    A classe gerencia toda a sequência necessária para localizar e selecionar
    uma planilha específica:
    1. Aguarda e navega pela janela de filtros
    2. Configura filtros para "Todos"
    3. Localiza elementos da interface (abas, toolbars, paineis)
    4. Executa pesquisa por ID da planilha
    5. Seleciona e abre a planilha encontrada
    
    Attributes:
        parent_element (BaseWrapper): Elemento pai para operações na interface.
        navigator (RMAdaptNavigator): Navegador adaptativo para localização de elementos.
        waits (UIWaits): Utilitário para esperas inteligentes.
        app (Optional[BaseWrapper]): Aplicação RM para execução automática.
        id_planilha (Optional[str]): ID da planilha para execução automática.
    
    Example:
        Execução automática (recomendado):
        
        >>> planilha_net = RMPlanilhaNet(main_window, app, "PLAN001")
        # Todo o processo é executado automaticamente
        
        Execução manual passo a passo:
        
        >>> planilha_net = RMPlanilhaNet(main_window)
        >>> success = planilha_net.navigate_filters(app, timeout=60)
        >>> if success:
        ...     success = planilha_net.select_planilha("PLAN001")
        
        Execução completa sob demanda:
        
        >>> planilha_net = RMPlanilhaNet(main_window)
        >>> success = planilha_net.execute_full_process(app, "PLAN001")
    
    Note:
        A classe inclui tratamento robusto de erros, logging detalhado e
        captura automática de screenshots para debugging.
    """
    
    def __init__(self, parent_element: BaseWrapper, app: Optional[BaseWrapper] = None, id_planilha: Optional[str] = None) -> None:
        """
        Inicializa o gerenciador da Planilha Net com opção de execução automática.
        
        Configura o gerenciador com o elemento pai e opcionalmente executa
        o processo completo se app e id_planilha forem fornecidos. Isso permite
        três padrões de uso diferentes conforme a necessidade.
        
        Args:
            parent_element (BaseWrapper): Elemento pai da interface onde serão
                realizadas as operações de navegação. Tipicamente a janela principal
                do TOTVS RM.
            app (BaseWrapper, optional): Instância da aplicação RM. Se fornecido
                junto com id_planilha, executa automaticamente o processo completo.
                Defaults to None.
            id_planilha (str, optional): ID da planilha a ser selecionada.
                Se fornecido junto com app, executa automaticamente o processo
                completo. Defaults to None.
        
        Example:
            Inicialização para uso manual:
            
            >>> planilha_net = RMPlanilhaNet(main_window)
            
            Inicialização com execução automática:
            
            >>> planilha_net = RMPlanilhaNet(main_window, app, "PLAN001")
            # Processo completo executado automaticamente
        
        Note:
            Se app e id_planilha forem fornecidos, o processo completo é
            executado imediatamente no construtor.
        """
        self.parent_element = parent_element
        self.navigator = RMAdaptNavigator(parent_element)  # type: ignore[arg-type]
        self.waits = UIWaits()
        self.app = app
        self.id_planilha = id_planilha
        logger.info("RMPlanilhaNet inicializado")
        
        # Se app e id_planilha foram fornecidos, executa o processo completo
        if self.app and self.id_planilha:
            self.execute_full_process()
    
    def execute_full_process(self, app: Optional[BaseWrapper] = None, id_planilha: Optional[str] = None, timeout: int = 60) -> bool:
        """
        Executa o processo completo de navegação e seleção da Planilha Net.
        
        Método de conveniência que executa toda a sequência necessária:
        1. Navega pelos filtros da Planilha Net
        2. Seleciona a planilha especificada
        
        Utiliza os parâmetros fornecidos ou os valores definidos no construtor
        como fallback, proporcionando flexibilidade de uso.
        
        Args:
            app (BaseWrapper, optional): Instância da aplicação RM. Se não
                fornecido, usa o app definido no construtor. Defaults to None.
            id_planilha (str, optional): ID da planilha a ser selecionada.
                Se não fornecido, usa o id_planilha definido no construtor.
                Defaults to None.
            timeout (int, optional): Tempo limite em segundos para aguardar
                a janela de filtros aparecer. Defaults to 60.
        
        Returns:
            bool: True se todo o processo foi executado com sucesso,
                False se algum passo falhou.
        
        Raises:
            UIElementNotFoundError: Se algum elemento necessário não for
                encontrado durante o processo.
            UIInteractionError: Se houver erro durante a interação com
                elementos da interface, ou se app/id_planilha não forem fornecidos.
        
        Example:
            Execução com parâmetros:
            
            >>> success = planilha_net.execute_full_process(app, "PLAN001", 90)
            >>> if success:
            ...     print("Planilha selecionada com sucesso")
            
            Execução usando valores do construtor:
            
            >>> planilha_net = RMPlanilhaNet(main_window, app, "PLAN001")
            >>> success = planilha_net.execute_full_process()  # Usa valores do construtor
        
        Note:
            Este método é chamado automaticamente no construtor se app e
            id_planilha forem fornecidos.
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
        """
        Navega pelos filtros da Planilha Net e configura para "Todos".
        
        Aguarda a janela de filtros da Planilha Net aparecer e executa a
        sequência de teclas necessária para selecionar "Todos" nos filtros,
        permitindo visualizar todas as planilhas disponíveis.
        
        Sequência executada:
        1. Aguarda janela "Filtros - Planilha Net" aparecer
        2. Pressiona LEFT para navegar
        3. Pressiona SPACE para selecionar
        4. Pressiona ENTER para confirmar
        
        Args:
            app (BaseWrapper): Instância da aplicação RM usada para localizar
                a janela de filtros.
            timeout (int, optional): Tempo limite em segundos para aguardar
                a janela de filtros aparecer. Defaults to 60.
        
        Returns:
            bool: True se a navegação pelos filtros foi bem-sucedida,
                False caso contrário.
        
        Raises:
            UIElementNotFoundError: Se a janela "Filtros - Planilha Net"
                não for encontrada dentro do tempo limite.
            UIInteractionError: Se houver erro durante a interação com
                os filtros (envio de teclas).
        
        Example:
            >>> success = planilha_net.navigate_filters(app, timeout=90)
            >>> if success:
            ...     print("Filtros configurados para 'Todos'")
        
        Note:
            Este método usa polling para aguardar a janela aparecer,
            verificando a existência a cada segundo até o timeout.
        """
        try:
            logger.info("Iniciando navegação pelos filtros da Planilha Net")
            
            # Aguarda a janela de filtros aparecer
            start_time = time.time()
            filtros_window = None
            
            while time.time() - start_time < timeout:
                try:
                    filtros_window = app.window(title="Filtros - Planilha Net")  # type: ignore[attr-defined]
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
        """
        Localiza e seleciona uma planilha específica na Planilha Net.
        
        Executa uma sequência complexa de navegação pela interface da Planilha Net
        para localizar, pesquisar e selecionar uma planilha específica pelo seu ID.
        
        Sequência de operações:
        1. Localiza a aba "Planilhas"
        2. Encontra o formulário "GlbPlanilhaNetFormView"
        3. Navega para a toolbar de pesquisa
        4. Preenche o campo de pesquisa com o ID da planilha
        5. Executa a pesquisa e ativa o filtro
        6. Localiza o resultado na árvore de dados
        7. Executa clique duplo para selecionar a planilha
        
        Args:
            id_planilha (str): ID único da planilha a ser localizada e
                selecionada. Deve corresponder exatamente ao ID na base de dados.
        
        Returns:
            bool: True se a planilha foi localizada e selecionada com sucesso,
                False caso contrário.
        
        Raises:
            UIElementNotFoundError: Se algum elemento necessário da interface
                não for encontrado (aba, formulário, toolbar, campos, etc.).
            UIInteractionError: Se houver erro durante qualquer interação
                com elementos da interface (cliques, preenchimento, etc.).
        
        Example:
            >>> success = planilha_net.select_planilha("PLAN001")
            >>> if success:
            ...     print("Planilha PLAN001 selecionada")
            ... else:
            ...     print("Falha ao selecionar planilha")
        
        Note:
            O método navega por uma estrutura hierárquica complexa da interface
            do TOTVS RM, incluindo múltiplos paineis, toolbars e árvores de dados.
            Inclui posicionamento de mouse para elementos que requerem foco.
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
    """
    Navega pelos filtros da Planilha Net (função deprecated).
    
    Função de compatibilidade que mantém a interface funcional antiga.
    Internamente cria uma instância de RMPlanilhaNet e delega a operação
    para a nova implementação baseada em classe.
    
    Warning:
        Esta função está marcada como deprecated e será removida em versões
        futuras. Use a classe RMPlanilhaNet diretamente.
    
    Args:
        app (BaseWrapper): Instância da aplicação RM.
    
    Returns:
        bool: True se a navegação pelos filtros foi bem-sucedida.
    
    Example:
        >>> # Uso deprecated (evitar)
        >>> success = navigate_filters_planilha_net(app)
        
        >>> # Uso recomendado
        >>> planilha_net = RMPlanilhaNet(main_window)
        >>> success = planilha_net.navigate_filters(app)
    
    Note:
        Esta função emite um DeprecationWarning quando chamada.
    """
    import warnings
    warnings.warn(
        "navigate_filters_planilha_net() está deprecated. Use RMPlanilhaNet.navigate_filters() em vez disso.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Usa uma janela temporária para criar a instância
    temp_window = app.top_window()  # type: ignore[attr-defined]
    planilha_net = RMPlanilhaNet(temp_window)
    return planilha_net.navigate_filters(app)


def select_planilha_net(window: BaseWrapper, id_planilha: str) -> bool:
    """
    Seleciona uma planilha na Planilha Net (função deprecated).
    
    Função de compatibilidade que mantém a interface funcional antiga.
    Internamente cria uma instância de RMPlanilhaNet e delega a operação
    para a nova implementação baseada em classe.
    
    Warning:
        Esta função está marcada como deprecated e será removida em versões
        futuras. Use a classe RMPlanilhaNet diretamente.
    
    Args:
        window (BaseWrapper): Janela da aplicação onde realizar as operações.
        id_planilha (str): ID da planilha a ser selecionada.
    
    Returns:
        bool: True se a planilha foi selecionada com sucesso.
    
    Example:
        >>> # Uso deprecated (evitar)
        >>> success = select_planilha_net(window, "PLAN001")
        
        >>> # Uso recomendado
        >>> planilha_net = RMPlanilhaNet(window)
        >>> success = planilha_net.select_planilha("PLAN001")
    
    Note:
        Esta função emite um DeprecationWarning quando chamada.
    """
    import warnings
    warnings.warn(
        "select_planilha_net() está deprecated. Use RMPlanilhaNet.select_planilha() em vez disso.",
        DeprecationWarning,
        stacklevel=2
    )
    
    planilha_net = RMPlanilhaNet(window)
    return planilha_net.select_planilha(id_planilha)