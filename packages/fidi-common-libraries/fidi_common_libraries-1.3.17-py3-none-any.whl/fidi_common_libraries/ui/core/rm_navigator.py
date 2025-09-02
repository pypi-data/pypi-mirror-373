"""
Navegador para aplicação TOTVS RM.

Fornece funcionalidades para navegação automática na interface do sistema RM,
incluindo navegação por abas, barras de ferramentas e botões.
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
    Utilitário para desenhar bordas ao redor de elementos UIA.
    
    Simula o comportamento do draw_outline() para elementos UIA
    usando a API do Windows para desenhar retângulos na tela.
    """
    
    @staticmethod
    def highlight(rect, color=(255, 0, 0), thickness=3, duration=0.5):
        """
        Desenha uma borda no retângulo informado.
        
        Args:
            rect: Objeto Rectangle do pywinauto (tem left, top, right, bottom).
            color (tuple): Cor RGB (default vermelho).
            thickness (int): Espessura da borda.
            duration (float): Segundos que a borda ficará na tela.
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
    Navegador para aplicação TOTVS RM.
    
    Fornece métodos para navegação automática na interface do sistema RM,
    incluindo navegação por abas, barras de ferramentas e botões.
    """
    
    def __init__(self, app: Application, main_window: Union[HwndWrapper, UIAWrapper, WindowSpecification]):
        """
        Inicializa o navegador RM.
        
        Args:
            app: Instância da aplicação pywinauto.
            main_window: Janela principal da aplicação RM (HwndWrapper, UIAWrapper, WindowSpecification ou HybridWrapper).
            
        Raises:
            ValueError: Se app ou main_window forem None.
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
        Detecta o backend baseado no tipo do elemento.
        
        Args:
            element: Elemento para detectar o backend.
            
        Returns:
            str: "win32" ou "uia"
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
        Desenha contorno do elemento de forma segura.
        
        Args:
            element: Elemento para desenhar contorno.
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
        Clica no elemento de forma segura.
        
        Args:
            element: Elemento para clicar.
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
        Método seguro para encontrar elementos filhos.
        
        Args:
            parent: Elemento pai.
            **criteria: Critérios de busca.
            
        Returns:
            Union[HwndWrapper, UIAWrapper]: Elemento encontrado.
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
        Navega até um elemento específico na aplicação TOTVS RM.
        
        Executa navegação sequencial: aba -> barra de ferramentas -> botão.
        Utiliza estrutura padrão do RM: mdiRibbonControl -> Ribbon Tabs -> Lower Ribbon.

        Args:
            tab_item_criteria: Critérios para encontrar a aba do sistema RM.
                             Ex: {"title": "Encargos", "control_type": "TabItem"}
            toolbar_criteria: Critérios para encontrar o grupo/toolbar na aba.
                            Ex: {"title": "Contabilização", "control_type": "ToolBar"}
            button_criteria: Critérios para encontrar o botão no grupo.
                           Ex: {"title": "Geração dos Encargos", "control_type": "Button"}
                           
        Returns:
            Tuple[bool, Optional[str]]: 
                - (True, texto_do_botao) se navegação bem-sucedida
                - (False, None) se falhar
                
        Raises:
            UIElementNotFoundError: Se algum elemento não for encontrado.
            UIInteractionError: Se houver erro na interação com elementos.
            ValueError: Se critérios forem inválidos.
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
        Obtém o controle ribbon principal.
        
        Returns:
            Union[HwndWrapper, UIAWrapper]: Controle ribbon principal.
            
        Raises:
            UIElementNotFoundError: Se o controle não for encontrado.
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
        Obtém o controle de abas do ribbon.
        
        Args:
            ribbon_control: Controle ribbon principal.
            
        Returns:
            Union[HwndWrapper, UIAWrapper]: Controle de abas.
            
        Raises:
            UIElementNotFoundError: Se o controle não for encontrado.
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
        Obtém o Lower Ribbon onde ficam as toolbars.
        
        Args:
            ribbon_control: Controle ribbon principal.
            
        Returns:
            Union[HwndWrapper, UIAWrapper]: Lower Ribbon.
            
        Raises:
            UIElementNotFoundError: Se o controle não for encontrado.
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
        Encontra e clica em uma aba.
        
        Args:
            ribbon_tabs: Controle de abas.
            criteria: Critérios para encontrar a aba.
            
        Returns:
            Union[HwndWrapper, UIAWrapper]: Aba encontrada.
            
        Raises:
            UIElementNotFoundError: Se a aba não for encontrada.
            UIInteractionError: Se houver erro ao clicar.
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
        Encontra uma toolbar no Lower Ribbon.
        
        Navega pela estrutura: Lower Ribbon -> Pane(tab_title) -> Toolbar
        
        Args:
            lower_ribbon: Lower Ribbon.
            criteria: Critérios para encontrar a toolbar.
            tab_title: Título da aba para encontrar o Pane intermediário.
            
        Returns:
            Union[HwndWrapper, UIAWrapper]: Toolbar encontrada.
            
        Raises:
            UIElementNotFoundError: Se a toolbar não for encontrada.
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
        Encontra e clica em um botão na toolbar.
        
        Args:
            toolbar: Toolbar onde buscar o botão.
            criteria: Critérios para encontrar o botão.
            
        Returns:
            Union[HwndWrapper, UIAWrapper]: Botão encontrado.
            
        Raises:
            UIElementNotFoundError: Se o botão não for encontrado.
            UIInteractionError: Se houver erro ao clicar.
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
    Exemplo de uso do RMNavigator.
    
    Este exemplo demonstra como usar o navegador para navegar
    até um elemento específico no sistema RM.
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