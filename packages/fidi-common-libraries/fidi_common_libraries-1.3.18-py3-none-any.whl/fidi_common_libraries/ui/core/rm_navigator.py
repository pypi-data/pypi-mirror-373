"""
Módulo de navegação automática para aplicação TOTVS RM.

Este módulo fornece a classe RMNavigator que implementa navegação estruturada
na interface do sistema TOTVS RM, seguindo a hierarquia padrão do ribbon:
mdiRibbonControl -> Ribbon Tabs -> Lower Ribbon -> Toolbars -> Buttons.

O navegador é compatível com ambos os backends do pywinauto (win32 e UIA),
detectando automaticamente o tipo de elemento e aplicando as estratégias
apropriadas para interação e destaque visual.

Classes:
    UIAHighlighter: Utilitário para destaque visual em elementos UIA
    RMNavigator: Navegador principal para automação do sistema RM

Exemplo:
    Navegação básica no sistema RM:
    
    >>> navigator = RMNavigator(app, main_window)
    >>> tab_criteria = {"title": "Encargos", "control_type": "TabItem"}
    >>> toolbar_criteria = {"title": "Contabilização", "control_type": "Pane"}
    >>> button_criteria = {"title": "Geração dos Encargos", "control_type": "Button"}
    >>> success, text = navigator.navigate_to_element(
    ...     tab_criteria, toolbar_criteria, button_criteria
    ... )
    >>> print(f"Sucesso: {success}, Botão: {text}")
"""

import logging
import time
from typing import Tuple, Dict, Any, Optional, Union
from pywinauto import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.application import WindowSpecification
from pywinauto.findwindows import ElementNotFoundError

try:
    import win32gui  # type: ignore[import-untyped]
    import win32api  # type: ignore[import-untyped]
    import win32con  # type: ignore[import-untyped]
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    # Criar stubs para evitar erros quando win32 não estiver disponível
    class _Win32Stub:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    win32gui = _Win32Stub()  # type: ignore[assignment]
    win32api = _Win32Stub()  # type: ignore[assignment]
    win32con = _Win32Stub()  # type: ignore[assignment]

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UIInteractionError
from ..utils.screenshot import capture_screenshot_on_error
from .waits import UIWaits


logger = logging.getLogger(__name__)


class UIAHighlighter:
    """
    Utilitário para destaque visual de elementos UIA.
    
    Esta classe fornece funcionalidade para desenhar bordas ao redor de elementos
    UIA, simulando o comportamento do método draw_outline() disponível em
    elementos win32. Utiliza a API do Windows para desenhar retângulos coloridos
    na tela, facilitando a identificação visual durante a automação.
    
    A classe é especialmente útil para debugging e desenvolvimento de scripts
    de automação, permitindo visualizar quais elementos estão sendo
    identificados e manipulados.
    
    Note:
        Requer a biblioteca win32gui para funcionar. Se não estiver disponível,
        os métodos falham silenciosamente sem afetar a execução.
    """
    
    @staticmethod
    def highlight(rect, color=(255, 0, 0), thickness=3, duration=0.5) -> None:
        """
        Desenha uma borda colorida ao redor do retângulo especificado.
        
        Utiliza a API do Windows para desenhar uma borda temporária na tela,
        destacando visualmente a área do elemento. A borda é desenhada sobre
        todos os outros elementos e desaparece automaticamente após o tempo
        especificado.
        
        Args:
            rect: Objeto Rectangle do pywinauto contendo as coordenadas
                (left, top, right, bottom) do elemento a ser destacado.
            color (tuple, optional): Cor RGB da borda como tupla (R, G, B).
                Valores de 0-255 para cada componente. Defaults to (255, 0, 0) (vermelho).
            thickness (int, optional): Espessura da borda em pixels.
                Defaults to 3.
            duration (float, optional): Tempo em segundos que a borda
                permanecerá visível na tela. Defaults to 0.5.
        
        Example:
            Destacar elemento com borda verde:
            
            >>> element_rect = element.rectangle()
            >>> UIAHighlighter.highlight(
            ...     element_rect,
            ...     color=(0, 255, 0),
            ...     thickness=2,
            ...     duration=1.0
            ... )
        
        Note:
            Se win32gui não estiver disponível, o método falha silenciosamente.
            Erros durante o desenho são logados em nível DEBUG.
        """
        if not WIN32_AVAILABLE:
            logger.debug("win32gui não disponível, pulando highlight")
            return
            
        try:
            hwnd = win32gui.GetDesktopWindow()
            hdc = win32gui.GetWindowDC(hwnd)
            
            if not hdc:  # Verificar se hdc é válido
                return
            
            # Cria a caneta para desenhar
            pen = win32gui.CreatePen(win32con.PS_SOLID, thickness, win32api.RGB(*color))
            old_pen = win32gui.SelectObject(hdc, int(pen))  # type: ignore[arg-type]
            old_brush = win32gui.SelectObject(hdc, win32gui.GetStockObject(win32con.NULL_BRUSH))
            
            # Desenha o retângulo
            win32gui.Rectangle(hdc, rect.left, rect.top, rect.right, rect.bottom)
            
            # Espera
            time.sleep(duration)
            
            # Restaura objetos
            win32gui.SelectObject(hdc, old_pen)
            win32gui.SelectObject(hdc, old_brush)
            if pen:  # Verificar se pen não é None
                win32gui.DeleteObject(pen)
            win32gui.ReleaseDC(hwnd, hdc)
            
        except Exception as e:
            logger.debug(f"Erro ao desenhar highlight: {e}")


class RMNavigator:
    """
    Navegador estruturado para aplicação TOTVS RM.
    
    Esta classe implementa navegação automática na interface do sistema TOTVS RM,
    seguindo a hierarquia padrão do ribbon e fornecendo métodos robustos para
    localização e interação com elementos da interface.
    
    O navegador suporta ambos os backends do pywinauto (win32 e UIA), detectando
    automaticamente o tipo de elemento e aplicando as estratégias apropriadas
    para cada backend. Inclui tratamento de erros, logging detalhado e captura
    de screenshots para debugging.
    
    Hierarquia de navegação seguida:
    1. mdiRibbonControl (controle principal do ribbon)
    2. Ribbon Tabs (container das abas)
    3. TabItem (aba específica)
    4. Lower Ribbon (container das toolbars)
    5. Pane da aba (container específico da aba)
    6. Toolbar/Pane (grupo de botões)
    7. Button (botão final)
    
    Attributes:
        app (Application): Instância da aplicação pywinauto.
        main_window (Union[HwndWrapper, UIAWrapper, WindowSpecification]):
            Janela principal da aplicação RM.
        config (UIConfig): Configurações de UI carregadas.
        waits (UIWaits): Utilitário para esperas inteligentes.
        backend (str): Backend detectado ("win32" ou "uia").
    
    Example:
        Navegação completa no sistema RM:
        
        >>> navigator = RMNavigator(app, main_window)
        >>> tab_criteria = {"title": "Encargos", "control_type": "TabItem"}
        >>> toolbar_criteria = {"title": "Contabilização", "control_type": "Pane"}
        >>> button_criteria = {"title": "Geração dos Encargos", "control_type": "Button"}
        >>> success, button_text = navigator.navigate_to_element(
        ...     tab_criteria, toolbar_criteria, button_criteria
        ... )
        >>> if success:
        ...     print(f"Botão clicado: {button_text}")
    
    Note:
        A classe é thread-safe e pode ser reutilizada para múltiplas operações
        de navegação na mesma sessão da aplicação.
    """
    
    def __init__(self, app: Application, main_window: Union[HwndWrapper, UIAWrapper, WindowSpecification]) -> None:
        """
        Inicializa o navegador RM com aplicação e janela principal.
        
        Configura o navegador com a instância da aplicação e janela principal,
        detecta automaticamente o backend (win32 ou UIA) e carrega as
        configurações necessárias para operações de navegação.
        
        Args:
            app (Application): Instância da aplicação pywinauto conectada
                ao processo do TOTVS RM.
            main_window (Union[HwndWrapper, UIAWrapper, WindowSpecification]):
                Janela principal da aplicação RM. Pode ser HwndWrapper (win32),
                UIAWrapper (UIA), WindowSpecification ou HybridWrapper.
        
        Raises:
            ValueError: Se app ou main_window forem None ou inválidos.
        
        Example:
            >>> from pywinauto import Application
            >>> app = Application(backend="uia").connect(path="RM.exe")
            >>> main_window = app.window(title_re=".*TOTVS.*")
            >>> navigator = RMNavigator(app, main_window)
            >>> print(f"Backend detectado: {navigator.backend}")
        """
        if app is None:
            raise ValueError("Parâmetro 'app' não pode ser None")
        if main_window is None:
            raise ValueError("Parâmetro 'main_window' não pode ser None")
            
        self.app = app
        self.main_window = main_window
        self.config = get_ui_config()
        self.waits = UIWaits()
        
        # Detectar backend automaticamente
        self.backend = self._detect_backend(main_window)
        logger.info(f"Backend detectado: {self.backend}")
    
    def _detect_backend(self, element) -> str:
        """
        Detecta automaticamente o backend baseado no tipo do elemento.
        
        Analisa o tipo do elemento fornecido para determinar se é um wrapper
        win32 ou UIA, permitindo que o navegador aplique as estratégias
        apropriadas para cada backend.
        
        Args:
            element: Elemento para análise de tipo. Pode ser HwndWrapper,
                UIAWrapper, WindowSpecification ou HybridWrapper.
        
        Returns:
            str: "win32" se for HwndWrapper, "uia" se for UIAWrapper ou
                como fallback padrão.
        
        Note:
            Para HybridWrapper, verifica o elemento interno (_window) para
            determinar o backend real.
        """
        element_type = str(type(element))
        
        if 'HwndWrapper' in element_type:
            return "win32"
        elif 'UIAWrapper' in element_type:
            return "uia"
        elif hasattr(element, '_window'):
            # HybridWrapper - verificar o elemento interno
            inner_type = str(type(element._window))
            if 'HwndWrapper' in inner_type:
                return "win32"
            elif 'UIAWrapper' in inner_type:
                return "uia"
        
        # Fallback: assumir UIA como padrão
        return "uia"
    
    def _safe_draw_outline(self, element) -> None:
        """
        Desenha contorno do elemento de forma segura e compatível.
        
        Aplica destaque visual ao elemento usando a estratégia apropriada
        para o backend detectado. Para win32, usa o método nativo draw_outline().
        Para UIA, usa o UIAHighlighter customizado.
        
        Args:
            element: Elemento para destacar visualmente. Pode ser HwndWrapper
                ou UIAWrapper.
        
        Note:
            Falhas no destaque são logadas em nível DEBUG e não interrompem
            a execução do script.
        """
        try:
            if self.backend == "win32" and hasattr(element, 'draw_outline'):
                # Win32: usar método nativo
                element.draw_outline()
            elif self.backend == "uia":
                # UIA: usar highlighter customizado
                try:
                    rect = element.rectangle()
                    UIAHighlighter.highlight(rect, color=(0, 255, 0), thickness=2, duration=0.3)
                except Exception as highlight_error:
                    logger.debug(f"Erro ao destacar elemento UIA: {highlight_error}")
        except Exception as e:
            logger.debug(f"Não foi possível desenhar contorno: {e}")
    
    def _safe_click(self, element) -> None:
        """
        Executa clique no elemento de forma segura e compatível.
        
        Aplica a estratégia de clique apropriada para o backend detectado.
        Para win32, usa click_input() que é mais confiável. Para UIA,
        usa o método genérico click().
        
        Args:
            element: Elemento para clicar. Pode ser HwndWrapper ou UIAWrapper.
        
        Raises:
            UIInteractionError: Se houver erro durante o clique.
        
        Note:
            O método inclui tratamento de erros e logging detalhado.
        """
        try:
            if self.backend == "win32" and hasattr(element, 'click_input'):
                # Win32: usar método específico
                element.click_input()
            else:
                # UIA: usar método genérico
                element.click()
        except Exception as e:
            logger.error(f"Erro ao clicar no elemento: {e}")
            raise UIInteractionError(f"Erro ao clicar no elemento", str(e))
    
    def _safe_child_window(self, parent, **criteria) -> Union[HwndWrapper, UIAWrapper]:
        """
        Método seguro e compatível para encontrar elementos filhos.
        
        Localiza elementos filhos usando a estratégia apropriada para o tipo
        de elemento pai. Tenta primeiro child_window() e, se não estiver
        disponível, usa descendants() como fallback.
        
        Args:
            parent: Elemento pai onde buscar. Pode ser qualquer tipo de wrapper.
            **criteria: Critérios de busca como title, auto_id, control_type, etc.
        
        Returns:
            Union[HwndWrapper, UIAWrapper]: Elemento filho encontrado e pronto
                para uso.
        
        Raises:
            ElementNotFoundError: Se nenhum elemento for encontrado com os
                critérios especificados.
        
        Note:
            O método garante que sempre retorna um wrapper válido,
            aplicando wrapper_object() quando necessário.
        """
        if hasattr(parent, 'child_window'):
            element = parent.child_window(**criteria)
        else:
            # Fallback para descendants
            results = parent.descendants(**criteria)
            if results:
                element = results[0]
            else:
                raise ElementNotFoundError(f"Elemento não encontrado com critérios {criteria}")
        
        # Garantir que retornamos um wrapper válido
        if hasattr(element, 'wrapper_object'):
            return element.wrapper_object()
        return element  # type: ignore[return-value]

    def navigate_to_element(
        self,
        tab_item_criteria: Dict[str, Any],
        toolbar_criteria: Dict[str, Any],
        button_criteria: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Executa navegação estruturada até elemento específico no TOTVS RM.
        
        Implementa navegação sequencial seguindo a hierarquia padrão do sistema
        TOTVS RM: aba -> toolbar -> botão. O método navega pela estrutura
        do ribbon (mdiRibbonControl -> Ribbon Tabs -> Lower Ribbon) de forma
        robusta, com tratamento de erros e logging detalhado.
        
        Sequência de navegação:
        1. Localiza e clica na aba especificada
        2. Encontra a toolbar/grupo dentro da aba
        3. Localiza e clica no botão final
        
        Args:
            tab_item_criteria (Dict[str, Any]): Critérios para localizar a aba
                do sistema RM. Deve incluir pelo menos 'title' e 'control_type'.
                Exemplo: {"title": "Encargos", "control_type": "TabItem"}
            toolbar_criteria (Dict[str, Any]): Critérios para localizar o
                grupo/toolbar dentro da aba selecionada.
                Exemplo: {"title": "Contabilização", "control_type": "Pane"}
            button_criteria (Dict[str, Any]): Critérios para localizar o
                botão final dentro do grupo/toolbar.
                Exemplo: {"title": "Geração dos Encargos", "control_type": "Button"}
        
        Returns:
            Tuple[bool, Optional[str]]: Tupla contendo:
                - bool: True se a navegação foi bem-sucedida, False caso contrário
                - Optional[str]: Texto do botão clicado se sucesso, None se falha
        
        Raises:
            UIElementNotFoundError: Se qualquer elemento da sequência não
                for encontrado (aba, toolbar ou botão).
            UIInteractionError: Se houver erro durante a interação com
                qualquer elemento (cliques, esperas, etc.).
            ValueError: Se algum dos critérios fornecidos for inválido
                (None, vazio ou não for dicionário).
        
        Example:
            Navegação para geração de encargos:
            
            >>> tab_criteria = {"title": "Encargos", "control_type": "TabItem"}
            >>> toolbar_criteria = {"title": "Contabilização", "control_type": "Pane"}
            >>> button_criteria = {"title": "Geração dos Encargos", "control_type": "Button"}
            >>> success, button_text = navigator.navigate_to_element(
            ...     tab_criteria, toolbar_criteria, button_criteria
            ... )
            >>> if success:
            ...     print(f"Operação iniciada: {button_text}")
            ... else:
            ...     print("Falha na navegação")
        
        Note:
            O método captura screenshots automaticamente em caso de erro
            e registra logs detalhados de cada etapa da navegação.
        """
        # Validação de parâmetros
        if not tab_item_criteria or not isinstance(tab_item_criteria, dict):
            raise ValueError("tab_item_criteria deve ser um dicionário não vazio")
        if not toolbar_criteria or not isinstance(toolbar_criteria, dict):
            raise ValueError("toolbar_criteria deve ser um dicionário não vazio")
        if not button_criteria or not isinstance(button_criteria, dict):
            raise ValueError("button_criteria deve ser um dicionário não vazio")
        
        try:
            logger.info("Iniciando navegação no sistema RM")
            
            # 1. Encontrar e clicar na aba (tab item)
            ribbon_control = self._get_ribbon_control()
            ribbon_tabs = self._get_ribbon_tabs(ribbon_control)
            
            tab_item = self._find_and_click_tab(ribbon_tabs, tab_item_criteria)
            logger.info(f"Aba selecionada: {tab_item.window_text()}")
            
            # 2. Encontrar toolbar no Lower Ribbon
            lower_ribbon = self._get_lower_ribbon(ribbon_control)
            tab_title = tab_item.window_text()
            toolbar = self._find_toolbar(lower_ribbon, toolbar_criteria, tab_title)
            logger.info(f"Toolbar encontrada: {toolbar.window_text()}")
            
            # 3. Encontrar e clicar no botão
            button = self._find_and_click_button(toolbar, button_criteria)
            button_text = button.window_text()
            logger.info(f"Botão clicado: {button_text}")
            
            logger.info("Navegação concluída com sucesso")
            return True, button_text
            
        except ElementNotFoundError as e:
            error_msg = f"Elemento não encontrado durante navegação: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_navigation_element_not_found")
            return False, None
            
        except Exception as e:
            error_msg = f"Erro durante navegação no sistema RM: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_navigation_failed")
            return False, None
    
    def _get_ribbon_control(self) -> Union[HwndWrapper, UIAWrapper]:
        """
        Localiza e retorna o controle ribbon principal do TOTVS RM.
        
        Busca pelo elemento mdiRibbonControl que é o container principal
        de todos os elementos do ribbon no sistema TOTVS RM.
        
        Returns:
            Union[HwndWrapper, UIAWrapper]: Controle ribbon principal
                pronto para uso.
        
        Raises:
            UIElementNotFoundError: Se o controle mdiRibbonControl não
                for encontrado na janela principal.
        
        Note:
            Este é o primeiro passo da navegação estruturada no RM.
        """
        try:
            ribbon_control = self._safe_child_window(
                self.main_window,
                auto_id="mdiRibbonControl", 
                control_type="Pane"
            )
            self.waits.wait_for_element_ready(ribbon_control)  # type: ignore[arg-type]
            return ribbon_control
        except ElementNotFoundError as e:
            raise UIElementNotFoundError("Controle ribbon não encontrado", str(e))
    
    def _get_ribbon_tabs(self, ribbon_control: Union[HwndWrapper, UIAWrapper]) -> Union[HwndWrapper, UIAWrapper]:
        """
        Localiza o container de abas dentro do ribbon principal.
        
        Busca pelo elemento "Ribbon Tabs" que contém todas as abas
        disponíveis no sistema TOTVS RM.
        
        Args:
            ribbon_control (Union[HwndWrapper, UIAWrapper]): Controle ribbon
                principal obtido via _get_ribbon_control().
        
        Returns:
            Union[HwndWrapper, UIAWrapper]: Container de abas pronto para
                localização de abas específicas.
        
        Raises:
            UIElementNotFoundError: Se o container "Ribbon Tabs" não for
                encontrado dentro do ribbon principal.
        """
        try:
            ribbon_tabs = self._safe_child_window(
                ribbon_control,
                title="Ribbon Tabs",
                control_type="Tab"
            )
            self.waits.wait_for_element_ready(ribbon_tabs)  # type: ignore[arg-type]
            return ribbon_tabs
        except ElementNotFoundError as e:
            raise UIElementNotFoundError("Ribbon Tabs não encontrado", str(e))
    
    def _get_lower_ribbon(self, ribbon_control: Union[HwndWrapper, UIAWrapper]) -> Union[HwndWrapper, UIAWrapper]:
        """
        Localiza o Lower Ribbon onde estão as toolbars e grupos de botões.
        
        O Lower Ribbon é a área inferior do ribbon que contém os grupos
        de botões organizados por aba. É onde ficam as toolbars específicas
        de cada aba selecionada.
        
        Args:
            ribbon_control (Union[HwndWrapper, UIAWrapper]): Controle ribbon
                principal obtido via _get_ribbon_control().
        
        Returns:
            Union[HwndWrapper, UIAWrapper]: Lower Ribbon pronto para
                localização de toolbars específicas.
        
        Raises:
            UIElementNotFoundError: Se o "Lower Ribbon" não for encontrado
                dentro do ribbon principal.
        """
        try:
            lower_ribbon = self._safe_child_window(
                ribbon_control,
                title="Lower Ribbon",
                control_type="Pane"
            )
            self.waits.wait_for_element_ready(lower_ribbon)  # type: ignore[arg-type]
            return lower_ribbon
        except ElementNotFoundError as e:
            raise UIElementNotFoundError("Lower Ribbon não encontrado", str(e))
    
    def _find_and_click_tab(
        self, 
        ribbon_tabs: Union[HwndWrapper, UIAWrapper], 
        criteria: Dict[str, Any]
    ) -> Union[HwndWrapper, UIAWrapper]:
        """
        Localiza e clica em uma aba específica do ribbon.
        
        Busca pela aba usando os critérios fornecidos, aplica destaque visual
        e executa o clique para ativá-la. Inclui esperas apropriadas para
        garantir que a aba esteja pronta para interação.
        
        Args:
            ribbon_tabs (Union[HwndWrapper, UIAWrapper]): Container de abas
                obtido via _get_ribbon_tabs().
            criteria (Dict[str, Any]): Critérios para localizar a aba,
                tipicamente incluindo 'title' e 'control_type'.
        
        Returns:
            Union[HwndWrapper, UIAWrapper]: Aba encontrada e ativada.
        
        Raises:
            UIElementNotFoundError: Se a aba não for encontrada com os
                critérios especificados.
            UIInteractionError: Se houver erro durante o clique na aba.
        """
        try:
            tab_item = self._safe_child_window(ribbon_tabs, **criteria)
            self.waits.wait_for_element_ready(tab_item)  # type: ignore[arg-type]
            self._safe_draw_outline(tab_item)
            self._safe_click(tab_item)
            return tab_item
        except ElementNotFoundError as e:
            raise UIElementNotFoundError(f"Aba não encontrada com critérios {criteria}", str(e))
        except Exception as e:
            raise UIInteractionError(f"Erro ao clicar na aba", str(e))
    
    def _find_toolbar(
        self, 
        lower_ribbon: Union[HwndWrapper, UIAWrapper], 
        criteria: Dict[str, Any],
        tab_title: str
    ) -> Union[HwndWrapper, UIAWrapper]:
        """
        Localiza uma toolbar específica dentro do Lower Ribbon.
        
        Navega pela estrutura hierárquica do RM: Lower Ribbon -> Pane da aba
        -> Toolbar/Grupo. Primeiro localiza o container específico da aba
        ativa, depois busca a toolbar dentro desse container.
        
        Estrutura navegada:
        Lower Ribbon -> Pane(tab_title) -> Toolbar/Grupo
        
        Args:
            lower_ribbon (Union[HwndWrapper, UIAWrapper]): Lower Ribbon
                obtido via _get_lower_ribbon().
            criteria (Dict[str, Any]): Critérios para localizar a toolbar
                específica dentro da aba.
            tab_title (str): Título da aba ativa, usado para localizar
                o container intermediário (Pane) da aba.
        
        Returns:
            Union[HwndWrapper, UIAWrapper]: Toolbar encontrada e destacada
                visualmente.
        
        Raises:
            UIElementNotFoundError: Se a toolbar não for encontrada com os
                critérios especificados na aba indicada.
        
        Note:
            O método primeiro localiza o Pane intermediário correspondente
            à aba ativa antes de buscar a toolbar específica.
        """
        try:
            # Primeiro encontra o Pane intermediário com o título da aba
            tab_pane = self._safe_child_window(
                lower_ribbon,
                title=tab_title,
                control_type="Pane"
            )
            self.waits.wait_for_element_ready(tab_pane)  # type: ignore[arg-type]
            logger.debug(f"Pane da aba encontrado: {tab_pane.window_text()}")
            
            # Depois encontra a toolbar dentro do Pane
            toolbar = self._safe_child_window(tab_pane, **criteria)
            self.waits.wait_for_element_ready(toolbar)  # type: ignore[arg-type]
            self._safe_draw_outline(toolbar)
            return toolbar
        except ElementNotFoundError as e:
            raise UIElementNotFoundError(f"Toolbar não encontrada com critérios {criteria} na aba '{tab_title}'", str(e))
    
    def _find_and_click_button(
        self, 
        toolbar: Union[HwndWrapper, UIAWrapper], 
        criteria: Dict[str, Any]
    ) -> Union[HwndWrapper, UIAWrapper]:
        """
        Localiza e clica no botão final dentro da toolbar.
        
        Último passo da navegação estruturada: localiza o botão específico
        dentro da toolbar, aplica destaque visual e executa o clique.
        Inclui esperas apropriadas para garantir que o botão esteja pronto.
        
        Args:
            toolbar (Union[HwndWrapper, UIAWrapper]): Toolbar onde buscar
                o botão, obtida via _find_toolbar().
            criteria (Dict[str, Any]): Critérios para localizar o botão
                específico, tipicamente incluindo 'title' e 'control_type'.
        
        Returns:
            Union[HwndWrapper, UIAWrapper]: Botão encontrado e clicado.
        
        Raises:
            UIElementNotFoundError: Se o botão não for encontrado com os
                critérios especificados na toolbar.
            UIInteractionError: Se houver erro durante o clique no botão.
        
        Note:
            Este é o passo final da navegação estruturada no sistema RM.
        """
        try:
            button = self._safe_child_window(toolbar, **criteria)
            self.waits.wait_for_element_ready(button)  # type: ignore[arg-type]
            self._safe_draw_outline(button)
            self._safe_click(button)
            return button
        except ElementNotFoundError as e:
            raise UIElementNotFoundError(f"Botão não encontrado com critérios {criteria}", str(e))
        except Exception as e:
            raise UIInteractionError(f"Erro ao clicar no botão", str(e))


# Exemplo de uso
if __name__ == "__main__":
    """
    Exemplo prático de uso do RMNavigator.
    
    Este exemplo demonstra como conectar ao TOTVS RM e usar o navegador
    para executar navegação estruturada até um elemento específico,
    incluindo tratamento de erros e feedback do resultado.
    
    O exemplo está comentado para evitar execução acidental, mas mostra
    o padrão recomendado para uso em scripts de automação reais.
    """
    try:
        from pywinauto import Application
        
        # Conectar à aplicação RM
        app = Application(backend="uia").connect(path="RM.exe")
        main_window = app.window(
            title_re=".*TOTVS.*", 
            class_name="WindowsForms10.Window.8.app.0.31d2b0c_r9_ad1"
        )
        
        # Criar navegador
        navigator = RMNavigator(app, main_window)
        
        # Critérios de navegação
        tab_criteria = {"title": "Encargos", "control_type": "TabItem"}
        toolbar_criteria = {"title": "Contabilização", "control_type": "Pane"}
        button_criteria = {"title": "Geração dos Encargos", "control_type": "Button"}
        
        # Executar navegação
        success, button_text = navigator.navigate_to_element(
            tab_criteria, toolbar_criteria, button_criteria
        )
        
        if success:
            print(f"Navegação bem-sucedida. Botão clicado: {button_text}")
        else:
            print("Navegação falhou.")
            
    except Exception as e:
        print(f"Erro no exemplo: {e}")