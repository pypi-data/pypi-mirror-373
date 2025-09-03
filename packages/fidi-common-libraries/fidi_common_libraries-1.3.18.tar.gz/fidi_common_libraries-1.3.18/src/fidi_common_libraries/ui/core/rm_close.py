"""Módulo para fechamento automatizado de janelas e aplicações TOTVS RM.

Este módulo fornece uma interface robusta para o fechamento controlado de janelas
específicas e da aplicação completa do sistema TOTVS RM. Inclui navegação adaptativa,
confirmações automáticas via teclado e tratamento de erros com captura de screenshots.

O módulo utiliza o RMAdaptNavigator para localização de elementos e implementa
padrões de retry para garantir operações confiáveis mesmo em interfaces instáveis.

Example:
    Uso básico para fechar janela atual:
    
    >>> from fidi_common_libraries.ui.core.rm_close import RMClose
    >>> closer = RMClose(main_window)
    >>> success = closer.close_window()
    >>> print(f"Janela fechada: {success}")
    
    Fechamento completo da aplicação:
    
    >>> success = closer.close_application()
    >>> print(f"Aplicação fechada: {success}")

Note:
    - Requer que a aplicação TOTVS RM esteja ativa e acessível
    - Utiliza confirmações automáticas via teclado (ENTER, RIGHT, ENTER)
    - Captura screenshots automaticamente em caso de erro
    - Suporta tanto janelas específicas quanto fechamento completo da aplicação
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
    """Gerenciador de fechamento para janelas e aplicações TOTVS RM.
    
    Esta classe implementa estratégias robustas para fechamento controlado de janelas
    e aplicações do sistema TOTVS RM. Utiliza navegação adaptativa para localizar
    elementos de interface e executa sequências de confirmação automática via teclado.
    
    A classe mantém referência ao elemento pai e utiliza um RMAdaptNavigator interno
    para operações de localização e interação com elementos da interface.
    
    Attributes:
        parent_element (BaseWrapper): Elemento pai para operações de fechamento.
        navigator (RMAdaptNavigator): Navegador adaptativo para localização de elementos.
    
    Example:
        Inicialização e uso básico:
        
        >>> closer = RMClose(main_window)
        >>> 
        >>> # Fechar janela atual
        >>> if closer.close_window():
        ...     print("Janela fechada com sucesso")
        >>> 
        >>> # Fechar aplicação completa
        >>> if closer.close_application():
        ...     print("Aplicação fechada completamente")
    
    Note:
        - Automaticamente captura screenshots em caso de erro
        - Utiliza logging estruturado para auditoria de operações
        - Implementa retry automático através do RMAdaptNavigator
        - Suporta confirmações automáticas via sequências de teclado
    """
    
    def __init__(self, parent_element: BaseWrapper) -> None:
        """Inicializa o gerenciador de fechamento RM.
        
        Configura o gerenciador com o elemento pai fornecido e inicializa o navegador
        adaptativo interno para operações de localização de elementos.
        
        Args:
            parent_element (BaseWrapper): Elemento pai da interface (janela principal,
                dialog ou qualquer container) que servirá como contexto para as
                operações de fechamento. Deve ser um elemento válido e acessível.
        
        Example:
            Inicialização com janela principal:
            
            >>> from pywinauto import Application
            >>> app = Application().connect(title="TOTVS")
            >>> main_window = app.top_window()
            >>> closer = RMClose(main_window)
            
            Inicialização com dialog específico:
            
            >>> dialog = main_window.child_window(title="Configurações")
            >>> closer = RMClose(dialog)
        
        Note:
            - O parent_element deve estar acessível no momento da inicialização
            - O RMAdaptNavigator é configurado automaticamente com o elemento fornecido
            - Logging é inicializado para rastreamento de operações
        """
        self.parent_element = parent_element
        self.navigator = RMAdaptNavigator(parent_element)  # type: ignore
        logger.info("RMClose inicializado")
    
    def close_window(self) -> bool:
        """Fecha a janela atual do sistema RM com confirmações automáticas.
        
        Executa uma sequência completa de fechamento de janela, incluindo:
        1. Localização do botão "Fechar" usando navegação adaptativa
        2. Clique no botão de fechamento
        3. Confirmações automáticas via teclado (ENTER, RIGHT, ENTER)
        4. Verificação de sucesso da operação
        
        O método utiliza o RMAdaptNavigator para localizar o botão de forma robusta,
        com retry automático em caso de elementos temporariamente indisponíveis.
        
        Returns:
            bool: True se a janela foi fechada com sucesso, False em caso de falha.
                O retorno True indica que todas as etapas foram executadas sem exceções.
        
        Raises:
            UIElementNotFoundError: Quando o botão "Fechar" não é encontrado após
                todas as tentativas de localização do navegador adaptativo.
            UIInteractionError: Quando ocorre erro durante a interação com elementos
                ou execução das confirmações via teclado.
        
        Example:
            Fechamento simples de janela:
            
            >>> closer = RMClose(dialog_window)
            >>> try:
            ...     if closer.close_window():
            ...         print("Janela fechada com sucesso")
            ...     else:
            ...         print("Falha no fechamento")
            ... except UIElementNotFoundError:
            ...     print("Botão de fechar não encontrado")
            ... except UIInteractionError as e:
            ...     print(f"Erro na interação: {e}")
            
            Uso em contexto de automação:
            
            >>> # Após abrir um dialog de configuração
            >>> config_dialog = main_window.child_window(title="Configurações")
            >>> closer = RMClose(config_dialog)
            >>> closer.close_window()  # Fecha o dialog automaticamente
        
        Note:
            - Captura screenshot automaticamente em caso de erro
            - Utiliza logging para auditoria da operação
            - As confirmações via teclado seguem o padrão TOTVS RM
            - Funciona com qualquer janela que tenha botão "Fechar" padrão
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
        
        Executa uma sequência completa de fechamento da aplicação principal,
        navegando pela estrutura hierárquica da interface TOTVS RM:
        
        1. Localiza o controle MDI Ribbon principal (mdiRibbonControl)
        2. Navega para a barra de título com botões (Ribbon Form Buttons)
        3. Localiza e clica no botão "Close" da aplicação
        4. Executa confirmações automáticas via teclado
        
        Este método é específico para a arquitetura de interface do TOTVS RM,
        que utiliza controles MDI (Multiple Document Interface) com Ribbon.
        
        Returns:
            bool: True se a aplicação foi fechada completamente com sucesso.
                False indica falha em alguma etapa do processo de fechamento.
        
        Raises:
            UIElementNotFoundError: Quando algum elemento da hierarquia não é
                encontrado (mdiRibbonControl, Ribbon Form Buttons, ou botão Close).
            UIInteractionError: Quando ocorre erro durante navegação, clique
                ou execução das confirmações via teclado.
        
        Example:
            Fechamento completo da aplicação:
            
            >>> app = RMApplication()
            >>> app.connect_or_start()
            >>> main_window = app.get_main_window()
            >>> 
            >>> closer = RMClose(main_window)
            >>> try:
            ...     if closer.close_application():
            ...         print("Aplicação TOTVS RM fechada completamente")
            ...     else:
            ...         print("Falha no fechamento da aplicação")
            ... except UIElementNotFoundError as e:
            ...     print(f"Elemento não encontrado: {e}")
            ... except UIInteractionError as e:
            ...     print(f"Erro na interação: {e}")
            
            Uso em cleanup de automação:
            
            >>> def cleanup_rm_session():
            ...     try:
            ...         closer = RMClose(main_window)
            ...         return closer.close_application()
            ...     except Exception as e:
            ...         logger.error(f"Erro no cleanup: {e}")
            ...         return False
        
        Note:
            - Específico para arquitetura MDI Ribbon do TOTVS RM
            - Navega pela hierarquia completa da interface
            - Captura screenshots em cada etapa de erro
            - Utiliza múltiplos navegadores para diferentes níveis da hierarquia
            - Confirmações seguem padrão TOTVS (ENTER, RIGHT, ENTER)
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
    
    Esta função mantém compatibilidade com código legado, mas está marcada
    para remoção em versões futuras. Internamente utiliza a classe RMClose.
    
    Args:
        window (BaseWrapper): Elemento da janela a ser fechada. Deve ser um
            wrapper válido de janela ou dialog do sistema TOTVS RM.
    
    Returns:
        bool: True se a janela foi fechada com sucesso, False caso contrário.
            O comportamento é idêntico ao método RMClose.close_window().
    
    Raises:
        UIElementNotFoundError: Se o botão de fechar não for encontrado.
        UIInteractionError: Se houver erro durante a interação.
    
    Example:
        Uso deprecated (não recomendado):
        
        >>> success = close_windows(dialog_window)  # Deprecated
        
        Uso recomendado:
        
        >>> closer = RMClose(dialog_window)
        >>> success = closer.close_window()
    
    Warning:
        Esta função está deprecated desde a versão 1.3.0 e será removida
        na versão 2.0.0. Migre para RMClose.close_window() para evitar
        problemas de compatibilidade futura.
    
    Note:
        - Emite DeprecationWarning quando utilizada
        - Funcionalidade idêntica à RMClose.close_window()
        - Mantida apenas para compatibilidade com código legado
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
    
    Esta função mantém compatibilidade com código legado para fechamento
    completo da aplicação TOTVS RM, mas está marcada para remoção futura.
    
    Args:
        main_window (BaseWrapper): Elemento da janela principal da aplicação
            TOTVS RM. Deve ser a janela raiz da aplicação com controles MDI.
    
    Returns:
        bool: True se a aplicação foi fechada completamente com sucesso,
            False caso contrário. Comportamento idêntico ao RMClose.close_application().
    
    Raises:
        UIElementNotFoundError: Se elementos da hierarquia MDI não forem encontrados.
        UIInteractionError: Se houver erro durante navegação ou interação.
    
    Example:
        Uso deprecated (não recomendado):
        
        >>> success = close_app(main_window)  # Deprecated
        
        Uso recomendado:
        
        >>> closer = RMClose(main_window)
        >>> success = closer.close_application()
    
    Warning:
        Esta função está deprecated desde a versão 1.3.0 e será removida
        na versão 2.0.0. Migre para RMClose.close_application() para evitar
        problemas de compatibilidade futura.
    
    Note:
        - Emite DeprecationWarning quando utilizada
        - Funcionalidade idêntica à RMClose.close_application()
        - Específica para arquitetura MDI Ribbon do TOTVS RM
        - Mantida apenas para compatibilidade com código legado
    """
    import warnings
    warnings.warn(
        "close_app() está deprecated. Use RMClose.close_application() em vez disso.",
        DeprecationWarning,
        stacklevel=2
    )
    
    closer = RMClose(main_window)
    return closer.close_application()