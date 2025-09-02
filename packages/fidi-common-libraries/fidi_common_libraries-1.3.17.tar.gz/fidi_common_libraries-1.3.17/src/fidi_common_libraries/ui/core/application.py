"""
Gerenciamento de conexão com aplicações.

Fornece funcionalidades robustas para conectar e gerenciar aplicações,
com tratamento de erros e recuperação automática.
"""

import logging
import os
import time
from typing import Optional, Union
import psutil

from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


class RMApplication:
    """
    Gerenciador de conexão com a aplicação RM.
    
    Encapsula a lógica de conexão, reconexão e gerenciamento do ciclo de vida
    da aplicação RM, fornecendo uma interface robusta e confiável.
    """
    
    def __init__(self):
        self.config = get_ui_config()
        self._app: Optional[Application] = None
        self._process_id: Optional[int] = None
        self._is_connected: bool = False
        self._started_by_us: bool = False  # Flag para saber se iniciamos a aplicação
    
    @property
    def app(self) -> Application:
        """
        Retorna a instância da aplicação, conectando se necessário.
        
        Returns:
            Application: Instância da aplicação conectada.
            
        Raises:
            UIConnectionError: Se não for possível conectar à aplicação.
        """
        if not self._is_connected or not self._app:
            self.connect()
        return self._app
    
    def start_application(
        self, 
        executable_path: Optional[str] = None,
        wait_time: int = 5,
        window_title_pattern: str = ".*TOTVS.*"
    ) -> Application:
        """
        Inicia a aplicação RM a partir do executável.
        
        Args:
            executable_path: Caminho para o executável RM. Se None, usa configuração padrão.
            wait_time: Tempo de espera após iniciar a aplicação (segundos).
            window_title_pattern: Padrão regex para identificar a janela principal.
            
        Returns:
            Application: Instância da aplicação iniciada.
            
        Raises:
            UIConnectionError: Se não for possível iniciar a aplicação.
        """
        # Define o caminho padrão se não fornecido
        if not executable_path:
            executable_path = os.getenv(
                'RM_EXECUTABLE_PATH', 
                r"C:\totvs\CorporeRM\RM.Net\RM.exe"
            )
        
        try:
            logger.info(f"Iniciando aplicação RM: {executable_path}")
            
            # Verifica se o arquivo executável existe
            if not os.path.exists(executable_path):
                raise UIConnectionError(f"Executável não encontrado: {executable_path}")
            
            # Inicia a aplicação
            self._app = Application().start(executable_path)
            self._started_by_us = True
            
            logger.info(f"Aplicação iniciada, aguardando {wait_time} segundos...")
            time.sleep(wait_time)
            
            # Tenta encontrar a janela principal
            totvs_window = self._find_totvs_window(window_title_pattern)
            
            if totvs_window:
                self._is_connected = True
                logger.info("Aplicação RM iniciada e janela principal encontrada")
                return self._app
            else:
                logger.warning("Aplicação iniciada mas janela principal não encontrada")
                self._is_connected = True  # Marca como conectado mesmo assim
                return self._app
                
        except Exception as e:
            error_msg = f"Erro ao iniciar aplicação RM: {str(e)}"
            logger.error(error_msg)
            capture_screenshot_on_error("start_application_failed")
            raise UIConnectionError(error_msg, str(e))
    
    def _find_totvs_window(
        self, 
        title_pattern: str = ".*TOTVS.*", 
        timeout: int = 30
    ):
        """
        Busca a janela principal do TOTVS/RM.
        
        Args:
            title_pattern: Padrão regex para o título da janela.
            timeout: Timeout para encontrar a janela.
            
        Returns:
            HwndWrapper: Janela encontrada ou None.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Tenta encontrar janela com padrão TOTVS
                totvs_window = self._app.window(title_re=title_pattern)
                totvs_window.wait('ready', timeout=2)
                logger.info(f"Janela TOTVS encontrada: {totvs_window.window_text()}")
                return totvs_window
            except (ElementNotFoundError, Exception):
                time.sleep(1)
                continue
        
        logger.warning(f"Janela TOTVS não encontrada após {timeout} segundos")
        return None
    
    def connect(
        self, 
        process_id: Optional[int] = None,
        window_title: Optional[str] = None,
        try_start_if_not_found: bool = True
    ) -> Application:
        """
        Conecta-se à aplicação RM.
        
        Args:
            process_id: ID específico do processo. Se None, tenta encontrar automaticamente.
            window_title: Título específico da janela. Se None, usa o padrão da configuração.
            try_start_if_not_found: Se deve tentar iniciar a aplicação se não encontrada.
            
        Returns:
            Application: Instância da aplicação conectada.
            
        Raises:
            UIConnectionError: Se não for possível conectar após todas as tentativas.
        """
        window_title = window_title or self.config.window_title
        
        for attempt in range(1, self.config.max_connection_attempts + 1):
            try:
                logger.info(f"Tentativa {attempt}/{self.config.max_connection_attempts} de conexão")
                
                if process_id:
                    self._app = self._connect_by_process_id(process_id)
                elif self._process_id:
                    self._app = self._connect_by_process_id(self._process_id)
                else:
                    self._app = self._connect_by_title_or_process()
                
                self._is_connected = True
                logger.info("Conexão estabelecida com sucesso")
                return self._app
                
            except Exception as e:
                logger.warning(f"Tentativa {attempt} falhou: {e}")
                
                # Se é a última tentativa e deve tentar iniciar
                if (attempt == self.config.max_connection_attempts and 
                    try_start_if_not_found and 
                    not self._started_by_us):
                    
                    logger.info("Tentando iniciar a aplicação RM...")
                    try:
                        return self.start_application()
                    except Exception as start_error:
                        logger.error(f"Falha ao iniciar aplicação: {start_error}")
                
                if attempt == self.config.max_connection_attempts:
                    error_msg = f"Falha ao conectar após {self.config.max_connection_attempts} tentativas"
                    capture_screenshot_on_error("connection_failed")
                    raise UIConnectionError(error_msg, str(e))
                
                time.sleep(self.config.wait_between_retries)
    
    def connect_or_start(
        self,
        executable_path: Optional[str] = None,
        force_start: bool = False
    ) -> Application:
        """
        Conecta à aplicação RM existente ou inicia uma nova.
        
        Args:
            executable_path: Caminho para o executável (se precisar iniciar).
            force_start: Se deve forçar o início de uma nova instância.
            
        Returns:
            Application: Instância da aplicação.
        """
        if force_start:
            logger.info("Forçando início de nova instância da aplicação")
            return self.start_application(executable_path)
        
        try:
            # Primeiro tenta conectar a uma instância existente
            return self.connect(try_start_if_not_found=False)
        except UIConnectionError:
            # Se não conseguir conectar, tenta iniciar
            logger.info("Não foi possível conectar, tentando iniciar aplicação")
            return self.start_application(executable_path)
    
    def _connect_by_process_id(self, process_id: int) -> Application:
        """Conecta pela ID do processo."""
        logger.debug(f"Conectando pelo PID: {process_id}")
        app = Application(backend=self.config.backend).connect(process=process_id)
        self._process_id = process_id
        return app
    
    def _connect_by_title_or_process(self) -> Application:
        """Conecta pelo título da janela ou nome do processo."""
        try:
            # Primeira tentativa: por título da janela
            logger.debug(f"Conectando pelo título: {self.config.window_title}")
            app = Application(backend=self.config.backend).connect(title=self.config.window_title)
            return app
        except ElementNotFoundError:
            # Segunda tentativa: por nome do processo
            logger.debug(f"Conectando pelo processo: {self.config.process_name}")
            return self._connect_by_process_name()
    
    def _connect_by_process_name(self) -> Application:
        """Conecta pelo nome do processo."""
        rm_processes = [p for p in psutil.process_iter(['pid', 'name']) 
                       if p.info['name'].lower() == self.config.process_name.lower()]
        
        if not rm_processes:
            raise UIConnectionError(f"Processo {self.config.process_name} não encontrado")
        
        # Usa o primeiro processo encontrado
        process_id = rm_processes[0].info['pid']
        logger.debug(f"Processo RM encontrado com PID: {process_id}")
        return self._connect_by_process_id(process_id)
    
    def close_application(self, force: bool = False) -> None:
        """
        Fecha a aplicação RM.
        
        Args:
            force: Se deve forçar o fechamento (kill process).
        """
        if not self._app:
            logger.info("Nenhuma aplicação para fechar")
            return
        
        try:
            if self._started_by_us or force:
                logger.info("Fechando aplicação RM...")
                
                if force:
                    # Força o fechamento matando o processo
                    if self._process_id:
                        import signal
                        os.kill(self._process_id, signal.SIGTERM)
                    else:
                        # Tenta matar pela aplicação
                        self._app.kill()
                else:
                    # Tenta fechar normalmente
                    try:
                        main_window = self.get_main_window()
                        main_window.close()
                    except:
                        # Se não conseguir fechar normalmente, mata o processo
                        self._app.kill()
                
                logger.info("Aplicação RM fechada")
            else:
                logger.info("Aplicação não foi iniciada por nós, apenas desconectando")
                
        except Exception as e:
            logger.warning(f"Erro ao fechar aplicação: {e}")
        finally:
            self.disconnect()
    
    def disconnect(self) -> None:
        """Desconecta da aplicação."""
        if self._app:
            logger.info("Desconectando da aplicação")
            self._app = None
            self._is_connected = False
            self._process_id = None
            self._started_by_us = False
    
    def is_connected(self) -> bool:
        """
        Verifica se a conexão está ativa.
        
        Returns:
            bool: True se conectado, False caso contrário.
        """
        if not self._is_connected or not self._app:
            return False
        
        try:
            # Tenta uma operação simples para verificar se a conexão ainda é válida
            _ = self._app.windows()
            return True
        except Exception:
            logger.warning("Conexão perdida, marcando como desconectado")
            self._is_connected = False
            return False
    
    def reconnect(self) -> Application:
        """
        Força uma reconexão com a aplicação.
        
        Returns:
            Application: Nova instância da aplicação conectada.
        """
        logger.info("Forçando reconexão")
        self.disconnect()
        return self.connect()
    
    def get_main_window(self, title_pattern: Optional[str] = None):
        """
        Retorna a janela principal da aplicação.
        
        Args:
            title_pattern: Padrão para buscar a janela. Se None, usa configuração padrão.
            
        Returns:
            HwndWrapper: Janela principal da aplicação.
        """
        if title_pattern:
            return self.app.window(title_re=title_pattern)
        else:
            # Tenta primeiro com o título configurado
            try:
                return self.app.window(title=self.config.window_title)
            except ElementNotFoundError:
                # Se não encontrar, tenta com padrão TOTVS
                return self.app.window(title_re=".*TOTVS.*")
    
    def get_totvs_window(self):
        """
        Retorna especificamente a janela TOTVS.
        
        Returns:
            HwndWrapper: Janela TOTVS encontrada.
        """
        return self.app.window(title_re=".*TOTVS.*")
    
    def wait_for_application_ready(self, timeout: int = 60) -> bool:
        """
        Aguarda a aplicação ficar completamente pronta.
        
        Args:
            timeout: Timeout em segundos.
            
        Returns:
            bool: True se a aplicação ficou pronta, False se timeout.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Verifica se consegue encontrar a janela principal
                main_window = self.get_main_window()
                main_window.wait('ready', timeout=2)
                
                # Verifica se a janela está responsiva
                if main_window.is_enabled() and main_window.is_visible():
                    logger.info("Aplicação RM está pronta")
                    return True
                    
            except Exception:
                time.sleep(2)
                continue
        
        logger.warning(f"Timeout aguardando aplicação ficar pronta após {timeout}s")
        return False
    
    def get_application_info(self) -> dict:
        """
        Retorna informações sobre a aplicação conectada.
        
        Returns:
            dict: Informações da aplicação.
        """
        info = {
            'connected': self._is_connected,
            'started_by_us': self._started_by_us,
            'process_id': self._process_id,
            'backend': self.config.backend
        }
        
        if self._app:
            try:
                windows = self._app.windows()
                info['window_count'] = len(windows)
                info['main_window_title'] = self.get_main_window().window_text()
            except Exception as e:
                info['error'] = str(e)
        
        return info