"""Módulo de inicialização e login automatizado para aplicação TOTVS RM.

Este módulo fornece funcionalidades completas para inicialização da aplicação
TOTVS RM e execução de login automatizado, incluindo:
- Inicialização da aplicação RM
- Localização da janela de login
- Obtenção de credenciais via sistema de parâmetros
- Preenchimento automático de campos de usuário e senha
- Seleção automática de ambiente baseada em configurações
- Execução do processo de login com validações

O módulo integra-se com o sistema de parâmetros da FIDI para obter credenciais
e utiliza o RMLoginEnvSelector para seleção automática de ambientes.

Example:
    Uso básico para login automatizado:
    
    >>> from fidi_common_libraries.ui.core.rm_start_login import RMStartLogin
    >>> from fidi_common_libraries.ui.locators.locator_service import LocatorService
    >>> 
    >>> locator_service = LocatorService("locators.yaml")
    >>> login_manager = RMStartLogin(locator_service)
    >>> success, rm_app = login_manager.start_and_login("HML", "FIDI-ferias")
    >>> 
    >>> if success:
    ...     print("Login realizado com sucesso!")
    ...     main_window = rm_app.get_main_window()

Note:
    - Requer configuração prévia de parâmetros APP_USER e APP_PASSWORD
    - Utiliza RMApplication para gerenciamento do ciclo de vida da aplicação
    - Integra-se com RMLoginEnvSelector para seleção de ambiente
    - Captura screenshots automaticamente em caso de erro
    - Suporta ambientes HML e PROD
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
    """Gerenciador de inicialização e login automatizado para TOTVS RM.
    
    Esta classe orquestra o processo completo de inicialização da aplicação
    TOTVS RM e execução de login automatizado. Integra múltiplos componentes
    para fornecer uma interface simplificada para automação de login.
    
    A classe gerencia:
    - Ciclo de vida da aplicação RM (inicialização e conexão)
    - Localização e interação com elementos da interface de login
    - Integração com sistema de parâmetros para credenciais
    - Seleção automática de ambiente baseada em configurações
    - Tratamento de erros com captura de screenshots
    
    Attributes:
        locator_service (LocatorService): Serviço para localização de elementos UI.
        config: Configurações da interface do usuário.
        waits (UIWaits): Utilitário para aguardar elementos ficarem prontos.
        rm_app (RMApplication): Instância da aplicação RM gerenciada.
    
    Example:
        Inicialização e uso completo:
        
        >>> locator_service = LocatorService("locators.yaml")
        >>> login_manager = RMStartLogin(locator_service)
        >>> 
        >>> # Login automatizado
        >>> success, rm_app = login_manager.start_and_login("HML", "FIDI-ferias")
        >>> 
        >>> if success:
        ...     # Aplicação pronta para uso
        ...     main_window = rm_app.get_main_window()
        ...     print(f"Aplicação iniciada: {main_window}")
        ... else:
        ...     print("Falha no login - verificar logs e screenshots")
    
    Note:
        - Requer LocatorService configurado com arquivo de locators válido
        - Depende de parâmetros APP_USER e APP_PASSWORD configurados no sistema
        - Utiliza RMLoginEnvSelector internamente para seleção de ambiente
        - Captura screenshots automaticamente para debugging em caso de erro
    """
    
    def __init__(self, locator_service: LocatorService) -> None:
        """Inicializa o gerenciador de login RM.
        
        Configura todos os componentes necessários para execução do login
        automatizado, incluindo serviço de locators, configurações UI,
        utilitários de espera e instância da aplicação RM.
        
        Args:
            locator_service (LocatorService): Serviço configurado para localização
                de elementos da interface. Deve estar inicializado com arquivo
                de locators válido contendo mapeamentos para elementos de login.
        
        Raises:
            ValueError: Quando locator_service é None ou inválido.
        
        Example:
            Inicialização com locator service:
            
            >>> from fidi_common_libraries.ui.locators.locator_service import LocatorService
            >>> locator_service = LocatorService("rm_locators.yaml")
            >>> login_manager = RMStartLogin(locator_service)
            
            Verificação de inicialização:
            
            >>> assert login_manager.locator_service is not None
            >>> assert login_manager.rm_app is not None
            >>> print(f"Login manager inicializado: {login_manager}")
        
        Note:
            - O locator_service deve estar configurado com mapeamentos para login
            - A configuração UI é carregada automaticamente via get_ui_config()
            - Uma nova instância de RMApplication é criada para gerenciamento
            - UIWaits é inicializado para operações de espera robustas
        """
        if locator_service is None:
            raise ValueError("Parâmetro 'locator_service' não pode ser None")
            
        self.locator_service = locator_service
        self.config = get_ui_config()
        self.waits = UIWaits()
        self.rm_app = RMApplication()
    
    def start_and_login(self, ambiente: str, produto: str) -> Tuple[bool, Optional[RMApplication]]:
        """Executa o processo completo de inicialização e login na aplicação RM.
        
        Orquestra todo o fluxo de login automatizado em 7 etapas sequenciais:
        1. Inicialização da aplicação RM
        2. Localização da janela de login
        3. Obtenção de credenciais via sistema de parâmetros
        4. Preenchimento automático dos campos de usuário e senha
        5. Seleção automática do ambiente baseada em configurações
        6. Execução do clique no botão de login
        7. Aguardo da conclusão do processo de login
        
        O método implementa validações robustas e tratamento de erros em cada
        etapa, com captura automática de screenshots para debugging.
        
        Args:
            ambiente (str): Ambiente de destino para login. Deve ser 'HML' para
                homologação ou 'PROD' para produção. Case-insensitive.
            produto (str): Nome do produto usado para buscar parâmetros específicos
                no sistema de configuração. Ex: 'FIDI-ferias', 'FIDI-comum'.
        
        Returns:
            Tuple[bool, Optional[RMApplication]]: Tupla contendo:
                - bool: True se login foi executado com sucesso, False caso contrário
                - Optional[RMApplication]: Instância da aplicação RM se sucesso,
                  None se falha. A aplicação retornada está pronta para uso.
        
        Raises:
            ValueError: Quando ambiente não é 'HML' ou 'PROD', ou produto é vazio.
            UIConnectionError: Quando falha na inicialização ou conexão com a aplicação.
            UIElementNotFoundError: Quando elementos da interface não são encontrados.
            UIInteractionError: Quando ocorre erro durante interação com elementos.
        
        Example:
            Login em ambiente de homologação:
            
            >>> login_manager = RMStartLogin(locator_service)
            >>> success, rm_app = login_manager.start_and_login("HML", "FIDI-ferias")
            >>> 
            >>> if success:
            ...     print("Login realizado com sucesso!")
            ...     main_window = rm_app.get_main_window()
            ...     # Continuar com automação...
            ... else:
            ...     print("Falha no login - verificar logs")
            
            Login em produção com tratamento de erro:
            
            >>> try:
            ...     success, rm_app = login_manager.start_and_login("PROD", "FIDI-comum")
            ...     if success:
            ...         # Aplicação pronta para automação
            ...         pass
            ... except ValueError as e:
            ...     print(f"Parâmetros inválidos: {e}")
            ... except UIConnectionError as e:
            ...     print(f"Erro de conexão: {e}")
        
        Note:
            - Requer parâmetros APP_USER e APP_PASSWORD configurados no sistema
            - Captura screenshots automaticamente em 'rm_start_login_failed.png'
            - Utiliza logging estruturado para auditoria de todas as etapas
            - O ambiente é normalizado para uppercase internamente
            - Timeout configurável via configurações UI
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
        """Inicia a aplicação TOTVS RM usando configurações do sistema.
        
        Utiliza a instância RMApplication para inicializar a aplicação com
        o caminho do executável e tempo de espera configurados no sistema.
        
        Raises:
            UIConnectionError: Quando falha na inicialização da aplicação,
                incluindo executável não encontrado, permissões insuficientes
                ou timeout na inicialização.
        
        Note:
            - Utiliza self.config.rm_executable_path para localizar o executável
            - Tempo de espera configurado via self.config.start_wait_time
            - Logs estruturados para auditoria do processo de inicialização
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
        """Localiza e retorna a janela de login da aplicação TOTVS RM.
        
        Busca por janela com padrão de título contendo 'TOTVS' e aguarda
        que a janela fique pronta para interação usando UIWaits.
        
        Returns:
            WindowSpecification: Janela de login da aplicação RM pronta
                para interação. A janela é validada e aguardada até ficar
                completamente carregada.
        
        Raises:
            UIElementNotFoundError: Quando a janela de login não é encontrada
                após timeout, ou quando a aplicação não está executando.
        
        Note:
            - Utiliza regex '.*TOTVS.*' para localizar a janela
            - Aguarda elemento ficar pronto via UIWaits
            - Type ignore necessário devido a limitações do pywinauto
        """
        try:
            # Busca janela com padrão TOTVS
            login_window = self.rm_app.app.window(title_re=".*TOTVS.*")
            self.waits.wait_for_element_ready(login_window)  # type: ignore
            
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