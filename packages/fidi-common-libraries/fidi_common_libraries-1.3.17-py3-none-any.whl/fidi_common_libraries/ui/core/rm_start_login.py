"""
Inicializador e login para aplicação RM.

Fornece funcionalidades para iniciar a aplicação RM e realizar login
automatizado, incluindo seleção de ambiente e preenchimento de credenciais.
"""

import logging
from typing import Tuple, Optional
from pywinauto.findwindows import ElementNotFoundError

from ...config.parametros import Parametros
from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError, UIElementNotFoundError, UIInteractionError
from ..utils.screenshot import capture_screenshot_on_error
from ..locators.locator_service import LocatorService, LocatorMode
from .application import RMApplication
from .rm_login_env_selector import RMLoginEnvSelector
from .waits import UIWaits


logger = logging.getLogger(__name__)


class RMStartLogin:
    """
    Inicializador e login para aplicação RM.
    
    Fornece métodos para iniciar a aplicação RM e realizar login
    automatizado com seleção de ambiente e preenchimento de credenciais.
    """
    
    def __init__(self, locator_service: LocatorService):
        """
        Inicializa o inicializador de login RM.
        
        Args:
            locator_service: Serviço de locators para obter elementos UI.
            
        Raises:
            ValueError: Se locator_service for None.
        """
        if locator_service is None:
            raise ValueError("Parâmetro 'locator_service' não pode ser None")
            
        self.locator_service = locator_service
        self.config = get_ui_config()
        self.waits = UIWaits()
        self.rm_app = RMApplication()
    
    def start_and_login(self, ambiente: str, produto: str) -> Tuple[bool, Optional[RMApplication]]:
        """
        Inicia aplicação RM e realiza login automatizado.
        
        Executa o fluxo completo: iniciar aplicação → aguardar tela de login →
        obter credenciais → preencher campos → selecionar ambiente → fazer login.
        
        Args:
            ambiente: Ambiente desejado ('HML' ou 'PROD').
            produto: Nome do produto para buscar parâmetros.
            
        Returns:
            Tuple[bool, Optional[RMApplication]]:
                - (True, rm_app) se login bem-sucedido
                - (False, None) se falhar
                
        Raises:
            UIConnectionError: Se não conseguir conectar à aplicação.
            UIElementNotFoundError: Se elementos não forem encontrados.
            UIInteractionError: Se houver erro na interação.
            ValueError: Se parâmetros forem inválidos.
        """
        # Validação de parâmetros
        if not ambiente or ambiente.upper() not in ['HML', 'PROD']:
            raise ValueError("Ambiente deve ser 'HML' ou 'PROD'")
        if not produto:
            raise ValueError("Produto não pode ser vazio")
        
        try:
            logger.info(f"Iniciando login RM - Ambiente: {ambiente}, Produto: {produto}")
            
            # 1. Iniciar aplicação RM
            self._start_application()
            
            # 2. Obter janela de login
            login_window = self._get_login_window()
            
            # 3. Obter credenciais via Parametros
            user, password = self._get_credentials(ambiente, produto)
            
            # 4. Preencher campos de login
            self._fill_login_fields(login_window, user, password)
            
            # 5. Selecionar ambiente
            self._select_environment(login_window, ambiente, produto)
            
            # 6. Clicar em Entrar
            self._click_login_button(login_window)
            
            # 7. Aguardar login completar
            self._wait_for_login_complete()
            
            logger.info("Login RM realizado com sucesso")
            return True, self.rm_app
            
        except Exception as e:
            error_msg = f"Erro durante login RM: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_start_login_failed")
            return False, None
    
    def _start_application(self) -> None:
        """
        Inicia a aplicação RM.
        
        Raises:
            UIConnectionError: Se não conseguir iniciar a aplicação.
        """
        try:
            logger.info("Iniciando aplicação RM...")
            
            executable_path = self.config.rm_executable_path
            self.rm_app.start_application(
                executable_path=executable_path,
                wait_time=self.config.start_wait_time
            )
            
            logger.info("Aplicação RM iniciada com sucesso")
            
        except Exception as e:
            raise UIConnectionError(f"Falha ao iniciar aplicação RM: {e}", str(e))
    
    def _get_login_window(self):
        """
        Obtém a janela de login da aplicação RM.
        
        Returns:
            HwndWrapper: Janela de login.
            
        Raises:
            UIElementNotFoundError: Se a janela não for encontrada.
        """
        try:
            # Busca janela com padrão TOTVS
            login_window = self.rm_app.app.window(title_re=".*TOTVS.*")
            self.waits.wait_for_element_ready(login_window)
            
            logger.info("Janela de login encontrada")
            return login_window
            
        except Exception as e:
            raise UIElementNotFoundError("Falha ao obter janela de login", str(e))
    
    def _get_credentials(self, ambiente: str, produto: str) -> Tuple[str, str]:
        """
        Obtém credenciais via Parametros.
        
        Args:
            ambiente: Ambiente para buscar parâmetros.
            produto: Produto para buscar parâmetros.
            
        Returns:
            Tuple[str, str]: (user, password)
            
        Raises:
            ValueError: Se credenciais não forem encontradas.
        """
        try:
            parametros = Parametros(ambiente=ambiente, produto=produto)
            
            user = parametros.get_parametro("APP_USER")
            password = parametros.get_parametro("APP_PASSWORD")
            
            if not user or not password:
                raise ValueError("Credenciais 'APP_USER' ou 'APP_PASSWORD' não encontradas nos parâmetros")
            
            logger.info(f"Credenciais obtidas para usuário: {user}")
            return user, password
            
        except Exception as e:
            raise ValueError(f"Erro ao obter credenciais: {e}")
    
    def _fill_login_fields(self, login_window, user: str, password: str) -> None:
        """
        Preenche os campos de usuário e senha.
        
        Args:
            login_window: Janela de login.
            user: Nome do usuário.
            password: Senha do usuário.
            
        Raises:
            UIElementNotFoundError: Se campos não forem encontrados.
            UIInteractionError: Se houver erro ao preencher.
        """
        try:
            # Campo usuário
            user_field = login_window.child_window(
                auto_id="cUser", 
                control_type="RM.Lib.WinForms.Controls.RMSButtonEdit"
            )
            self.waits.wait_for_element_ready(user_field)
            user_field.draw_outline()
            user_field.type_keys(user)
            logger.debug("Campo usuário preenchido")
            
            # Campo senha
            password_field = login_window.child_window(
                auto_id="cPassword", 
                control_type="RM.Lib.WinForms.Controls.RMSButtonEdit"
            )
            self.waits.wait_for_element_ready(password_field)
            password_field.draw_outline()
            password_field.type_keys(password)
            logger.debug("Campo senha preenchido")
            
        except ElementNotFoundError as e:
            raise UIElementNotFoundError("Campos de login não encontrados", str(e))
        except Exception as e:
            raise UIInteractionError("Erro ao preencher campos de login", str(e))
    
    def _select_environment(self, login_window, ambiente: str, produto: str) -> None:
        """
        Seleciona o ambiente usando RMLoginEnvSelector.
        
        Args:
            login_window: Janela de login.
            ambiente: Ambiente desejado.
            produto: Nome do produto.
            
        Raises:
            UIInteractionError: Se falhar na seleção do ambiente.
        """
        try:
            env_selector = RMLoginEnvSelector(login_window, self.locator_service)
            success, selected_alias = env_selector.select_environment(ambiente, produto)
            
            if not success:
                raise UIInteractionError("Falha na seleção do ambiente")
            
            logger.info(f"Ambiente selecionado: {selected_alias}")
            
        except Exception as e:
            raise UIInteractionError(f"Erro na seleção do ambiente: {e}", str(e))
    
    def _click_login_button(self, login_window) -> None:
        """
        Clica no botão Entrar.
        
        Args:
            login_window: Janela de login.
            
        Raises:
            UIElementNotFoundError: Se botão não for encontrado.
            UIInteractionError: Se houver erro ao clicar.
        """
        try:
            login_button = login_window.child_window(
                title="Entrar", 
                control_type="System.Windows.Forms.Button"
            )
            self.waits.wait_for_element_ready(login_button)
            login_button.draw_outline()
            login_button.click()
            
            # Aguardar antes da próxima janela
            import time
            wait_time = getattr(self.config, 'wait_before_next_window', 10.0)
            time.sleep(wait_time)
            
            logger.info("Botão Entrar clicado")
            
        except ElementNotFoundError as e:
            raise UIElementNotFoundError("Botão Entrar não encontrado", str(e))
        except Exception as e:
            raise UIInteractionError("Erro ao clicar no botão Entrar", str(e))
    
    def _wait_for_login_complete(self) -> None:
        """
        Aguarda o login ser completado.
        
        Aguarda a aplicação ficar pronta após o login.
        
        Raises:
            UITimeoutError: Se timeout for atingido.
        """
        try:
            # Aguarda aplicação ficar pronta
            if not self.rm_app.get_main_window():
                raise UIInteractionError("Timeout aguardando aplicação ficar pronta após login")
            
            logger.info("Login completado - aplicação pronta")
            
        except Exception as e:
            raise UIInteractionError(f"Erro aguardando login completar: {e}", str(e))


# Exemplo de uso
if __name__ == "__main__":
    """
    Exemplo de uso do RMStartLogin.
    
    Este exemplo demonstra como usar o inicializador para
    fazer login automatizado na aplicação RM.
    """
    try:
        # Criar locator service
        locator_service = LocatorService("locators.yaml")
        
        # Criar inicializador
        login_manager = RMStartLogin(locator_service)
        
        # Realizar login
        success, rm_app = login_manager.start_and_login("HML", "FIDI-ferias")
        
        if success:
            assert rm_app is not None  # Garante para Pylance (e para execução)
            print("Login realizado com sucesso!")
            print(f"Aplicação RM: {rm_app}")
            
            # Usar a aplicação...
            main_window = rm_app.get_main_window()
            print(f"Main Window: {main_window}")
        else:
            print("Falha no login")
            
    except Exception as e:
        print(f"Erro no exemplo: {e}")