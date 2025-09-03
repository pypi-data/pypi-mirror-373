"""
Gerenciamento avançado de conexão e ciclo de vida de aplicações.

Este módulo implementa um sistema robusto para gerenciamento de aplicações
externas, especificamente otimizado para o sistema TOTVS RM. Oferece
funcionalidades completas de conexão, inicialização, monitoramento e
fechamento de aplicações com tratamento de erros abrangente.

O módulo suporta múltiplas estratégias de conexão:
- Conexão por ID de processo
- Conexão por título de janela
- Conexão por nome do processo
- Inicialização automática quando necessário

Características principais:
- Retry automático com timeouts configuráveis
- Detecção automática de aplicações existentes
- Gerenciamento inteligente do ciclo de vida
- Recuperação automática de conexões perdidas
- Logging detalhado para auditoria e debugging

Example:
    Uso básico do gerenciador de aplicação:
    
    >>> rm_app = RMApplication()
    >>> app = rm_app.connect_or_start()
    >>> main_window = rm_app.get_main_window()
    
    Inicialização forçada:
    
    >>> app = rm_app.start_application("/path/to/rm.exe")
    >>> rm_app.wait_for_application_ready(timeout=60)
    
    Verificação de status:
    
    >>> if rm_app.is_connected():
    ...     info = rm_app.get_application_info()
    ...     print(f"Conectado ao PID: {info['process_id']}")

Note:
    Este módulo requer pywinauto e psutil para funcionar corretamente.
    É otimizado para aplicações Windows e sistema TOTVS RM.
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
    Gerenciador completo de conexão e ciclo de vida da aplicação TOTVS RM.
    
    Esta classe implementa um sistema abrangente para gerenciamento de
    aplicações TOTVS RM, incluindo conexão inteligente, inicialização
    automática, monitoramento de estado e fechamento controlado.
    
    A classe oferece múltiplas estratégias de conexão com fallback
    automático, garantindo máxima confiabilidade na comunicação com
    a aplicação RM. Inclui funcionalidades avançadas como detecção
    de aplicações existentes, retry automático e recuperação de falhas.
    
    Attributes:
        config: Configuração de UI carregada do sistema.
        _app: Instância atual da aplicação pywinauto.
        _process_id: ID do processo da aplicação conectada.
        _is_connected: Flag indicando se há conexão ativa.
        _started_by_us: Flag indicando se iniciamos a aplicação.
    
    Example:
        Inicialização e uso básico:
        
        >>> rm_app = RMApplication()
        >>> app = rm_app.connect_or_start()
        >>> if rm_app.is_connected():
        ...     main_window = rm_app.get_main_window()
        
        Conexão com parâmetros específicos:
        
        >>> app = rm_app.connect(
        ...     process_id=1234,
        ...     try_start_if_not_found=True
        ... )
        
        Gerenciamento do ciclo de vida:
        
        >>> rm_app.wait_for_application_ready()
        >>> # ... usar aplicação ...
        >>> rm_app.close_application()
    
    Note:
        A classe gerencia automaticamente o estado da conexão e
        oferece reconexão automática quando necessário.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de aplicação RM com configurações padrão.
        
        Carrega as configurações de UI do sistema e inicializa o estado
        interno para gerenciamento da conexão com a aplicação RM.
        """
        self.config = get_ui_config()
        self._app: Optional[Application] = None
        self._process_id: Optional[int] = None
        self._is_connected: bool = False
        self._started_by_us: bool = False  # Flag para saber se iniciamos a aplicação
    
    @property
    def app(self) -> Application:
        """
        Propriedade que retorna a instância da aplicação com conexão automática.
        
        Garante que sempre há uma conexão ativa com a aplicação RM.
        Se não houver conexão, tenta conectar automaticamente antes
        de retornar a instância.
        
        Returns:
            Application: Instância da aplicação pywinauto conectada e pronta.
            
        Raises:
            UIConnectionError: Se não for possível estabelecer conexão
                com a aplicação após todas as tentativas.
        
        Example:
            Acesso transparente à aplicação:
            
            >>> rm_app = RMApplication()
            >>> main_window = rm_app.app.window(title="TOTVS")
            >>> # Conexão é estabelecida automaticamente se necessário
        
        Note:
            Esta propriedade implementa lazy loading, conectando apenas
            quando necessário e reutilizando conexões existentes.
        """
        if not self._is_connected or not self._app:
            self.connect()
        if self._app is None:
            raise UIConnectionError("Falha ao conectar à aplicação")
        return self._app
    
    def start_application(
        self, 
        executable_path: Optional[str] = None,
        wait_time: int = 5,
        window_title_pattern: str = ".*TOTVS.*"
    ) -> Application:
        """
        Inicia nova instância da aplicação TOTVS RM a partir do executável.
        
        Executa o processo de inicialização completo da aplicação RM,
        incluindo verificação de existência do executável, inicialização
        do processo, aguardo de carregamento e detecção da janela principal.
        
        Args:
            executable_path (Optional[str], optional): Caminho completo para
                o executável RM. Se None, usa variável de ambiente
                RM_EXECUTABLE_PATH ou caminho padrão. Defaults to None.
            wait_time (int, optional): Tempo de espera em segundos após
                iniciar a aplicação para permitir carregamento completo.
                Defaults to 5.
            window_title_pattern (str, optional): Padrão regex para identificar
                a janela principal da aplicação. Defaults to ".*TOTVS.*".
            
        Returns:
            Application: Instância da aplicação pywinauto iniciada e conectada.
            
        Raises:
            UIConnectionError: Se o executável não for encontrado, se a
                inicialização falhar ou se ocorrer erro durante o processo.
        
        Example:
            Inicialização com caminho padrão:
            
            >>> rm_app = RMApplication()
            >>> app = rm_app.start_application()
            >>> rm_app.wait_for_application_ready()
            
            Inicialização com caminho personalizado:
            
            >>> app = rm_app.start_application(
            ...     executable_path="C:/Custom/Path/RM.exe",
            ...     wait_time=10
            ... )
            
            Inicialização com padrão de janela específico:
            
            >>> app = rm_app.start_application(
            ...     window_title_pattern=".*RM Sistema.*"
            ... )
        
        Note:
            A aplicação é marcada como iniciada por nós (_started_by_us=True)
            para controle adequado do ciclo de vida. Screenshot é capturado
            automaticamente em caso de erro.
        """
        # Define o caminho padrão se não fornecido
        if not executable_path:
            executable_path = os.getenv(
                'RM_EXECUTABLE_PATH', 
                r"C:\totvs\CorporeRM\RM.Net\RM.exe"
            ) or r"C:\totvs\CorporeRM\RM.Net\RM.exe"
        
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
        title_pattern: str = "MainForm", 
        timeout: int = 30
    ):
        """
        Localiza a janela principal do TOTVS/RM com retry automático.
        
        Método interno que implementa busca persistente pela janela
        principal da aplicação RM usando padrão regex. Inclui retry
        automático e aguardo de carregamento completo.
        
        Args:
            title_pattern (str, optional): Padrão regex para identificar
                o título da janela principal. Defaults to ".*TOTVS.*".
            timeout (int, optional): Tempo limite em segundos para
                encontrar a janela. Defaults to 30.
            
        Returns:
            HwndWrapper | None: Janela encontrada e pronta para uso,
                ou None se não encontrada dentro do timeout.
        
        Note:
            Este é um método interno que implementa retry com intervalo
            de 1 segundo entre tentativas. Aguarda a janela ficar
            completamente pronta antes de retornar.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Tenta encontrar janela com padrão TOTVS
                if self._app is not None:
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
        Estabelece conexão com aplicação RM existente usando múltiplas estratégias.
        
        Implementa sistema robusto de conexão com retry automático e
        múltiplas estratégias de localização. Tenta conectar por ID de
        processo, título de janela ou nome do processo, com fallback
        para inicialização automática se necessário.
        
        Args:
            process_id (Optional[int], optional): ID específico do processo
                RM para conectar. Se fornecido, tenta conexão direta.
                Defaults to None.
            window_title (Optional[str], optional): Título específico da
                janela para localizar a aplicação. Se None, usa configuração
                padrão. Defaults to None.
            try_start_if_not_found (bool, optional): Se True, tenta iniciar
                nova instância da aplicação se não encontrar existente.
                Defaults to True.
            
        Returns:
            Application: Instância da aplicação pywinauto conectada e validada.
            
        Raises:
            UIConnectionError: Se não for possível conectar após todas as
                tentativas configuradas, incluindo falha na inicialização
                automática se habilitada.
        
        Example:
            Conexão automática:
            
            >>> rm_app = RMApplication()
            >>> app = rm_app.connect()
            
            Conexão por PID específico:
            
            >>> app = rm_app.connect(process_id=1234)
            
            Conexão sem inicialização automática:
            
            >>> app = rm_app.connect(try_start_if_not_found=False)
        
        Note:
            O método tenta múltiplas estratégias em sequência e inclui
            retry automático com delays configuráveis. Screenshot é
            capturado em caso de falha final.
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
        
        # Se chegou aqui, todas as tentativas falharam
        raise UIConnectionError("Falha ao conectar após todas as tentativas")
    
    def connect_or_start(
        self,
        executable_path: Optional[str] = None,
        force_start: bool = False
    ) -> Application:
        """
        Conecta a aplicação existente ou inicia nova instância automaticamente.
        
        Método de conveniência que implementa a estratégia mais comum:
        tentar conectar a uma instância existente e, se não encontrar,
        iniciar uma nova automaticamente. Oferece opção de forçar
        inicialização de nova instância.
        
        Args:
            executable_path (Optional[str], optional): Caminho para o
                executável RM caso seja necessário iniciar nova instância.
                Se None, usa configuração padrão. Defaults to None.
            force_start (bool, optional): Se True, força inicialização de
                nova instância sem tentar conectar a existente.
                Defaults to False.
            
        Returns:
            Application: Instância da aplicação conectada, seja existente
                ou recém-iniciada.
        
        Example:
            Uso típico (conectar ou iniciar):
            
            >>> rm_app = RMApplication()
            >>> app = rm_app.connect_or_start()
            
            Forçar nova instância:
            
            >>> app = rm_app.connect_or_start(force_start=True)
            
            Com executável personalizado:
            
            >>> app = rm_app.connect_or_start(
            ...     executable_path="/custom/path/RM.exe"
            ... )
        
        Note:
            Este é o método recomendado para uso geral, pois oferece
            máxima flexibilidade e confiabilidade.
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
        """
        Conecta diretamente a um processo específico pelo ID.
        
        Método interno que estabelece conexão direta com processo
        RM usando o ID do processo. Mais rápido quando o PID é conhecido.
        
        Args:
            process_id (int): ID do processo RM para conectar.
            
        Returns:
            Application: Instância da aplicação conectada ao processo.
        
        Note:
            Este é um método interno que atualiza _process_id após
            conexão bem-sucedida.
        """
        logger.debug(f"Conectando pelo PID: {process_id}")
        app = Application(backend=self.config.backend).connect(process=process_id)
        self._process_id = process_id
        return app
    
    def _connect_by_title_or_process(self) -> Application:
        """
        Conecta usando título de janela com fallback para nome do processo.
        
        Método interno que implementa estratégia de conexão em duas etapas:
        primeiro tenta por título de janela configurado, depois por nome
        do processo como fallback.
        
        Returns:
            Application: Instância da aplicação conectada.
        
        Raises:
            UIConnectionError: Se não conseguir conectar por nenhum método.
        
        Note:
            Este método implementa a estratégia de fallback automático
            entre diferentes métodos de localização.
        """
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
        """
        Localiza e conecta ao processo RM pelo nome do executável.
        
        Método interno que busca processos ativos com nome correspondente
        ao configurado e conecta ao primeiro encontrado.
        
        Returns:
            Application: Instância da aplicação conectada.
        
        Raises:
            UIConnectionError: Se nenhum processo RM for encontrado.
        
        Note:
            Usa psutil para enumerar processos e conecta ao primeiro
            processo RM encontrado.
        """
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
        Fecha a aplicação RM de forma controlada ou forçada.
        
        Implementa fechamento inteligente da aplicação, tentando primeiro
        fechamento normal através da interface e, se necessário, forçando
        término do processo. Respeita se a aplicação foi iniciada por nós.
        
        Args:
            force (bool, optional): Se True, força fechamento matando o
                processo independentemente de quem iniciou. Se False,
                só fecha se iniciamos a aplicação. Defaults to False.
        
        Example:
            Fechamento normal:
            
            >>> rm_app.close_application()
            
            Fechamento forçado:
            
            >>> rm_app.close_application(force=True)
        
        Note:
            Sempre chama disconnect() no final para limpar estado interno.
            Aplicações não iniciadas por nós são apenas desconectadas.
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
                        if self._app is not None:
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
        """
        Desconecta da aplicação e limpa estado interno.
        
        Remove a conexão com a aplicação e reseta todos os flags
        e referências internas para estado inicial.
        
        Note:
            Este método não fecha a aplicação, apenas remove a conexão.
            Use close_application() para fechar a aplicação.
        """
        if self._app:
            logger.info("Desconectando da aplicação")
            self._app = None
            self._is_connected = False
            self._process_id = None
            self._started_by_us = False
    
    def is_connected(self) -> bool:
        """
        Verifica se há conexão ativa e válida com a aplicação.
        
        Realiza verificação ativa da conexão tentando uma operação
        simples na aplicação. Atualiza automaticamente o estado
        interno se a conexão foi perdida.
        
        Returns:
            bool: True se há conexão ativa e válida, False caso contrário.
        
        Example:
            Verificação de status:
            
            >>> if rm_app.is_connected():
            ...     print("Aplicação conectada")
            ... else:
            ...     print("Sem conexão")
        
        Note:
            Este método é não-destrutivo e atualiza automaticamente
            o estado interno se detectar perda de conexão.
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
        Força reconexão completa com a aplicação RM.
        
        Desconecta da instância atual e estabelece nova conexão,
        útil para recuperar de estados inconsistentes ou conexões
        perdidas.
        
        Returns:
            Application: Nova instância da aplicação conectada.
        
        Raises:
            UIConnectionError: Se não conseguir estabelecer nova conexão.
        
        Example:
            Recuperação de conexão perdida:
            
            >>> try:
            ...     app = rm_app.reconnect()
            ...     print("Reconexão bem-sucedida")
            ... except UIConnectionError:
            ...     print("Falha na reconexão")
        
        Note:
            Este método sempre força nova conexão, mesmo se já conectado.
        """
        logger.info("Forçando reconexão")
        self.disconnect()
        result = self.connect()
        if result is None:
            raise UIConnectionError("Falha na reconexão")
        return result
    
    def get_main_window(self, title_pattern: Optional[str] = None):
        """
        Localiza e retorna a janela principal da aplicação RM.
        
        Busca a janela principal usando título configurado ou padrão
        personalizado, com fallback automático para padrão TOTVS.
        
        Args:
            title_pattern (Optional[str], optional): Padrão regex personalizado
                para localizar a janela. Se None, usa título configurado
                com fallback para ".*TOTVS.*". Defaults to None.
            
        Returns:
            HwndWrapper: Janela principal da aplicação encontrada.
        
        Raises:
            ElementNotFoundError: Se nenhuma janela correspondente for encontrada.
        
        Example:
            Obter janela principal padrão:
            
            >>> main_window = rm_app.get_main_window()
            >>> print(main_window.window_text())
            
            Buscar com padrão personalizado:
            
            >>> window = rm_app.get_main_window(".*Sistema RM.*")
        
        Note:
            Implementa fallback automático entre título configurado
            e padrão TOTVS genérico.
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
        Localiza especificamente a janela com padrão TOTVS.
        
        Método de conveniência para localizar janela usando padrão
        TOTVS genérico, útil quando há múltiplas janelas da aplicação.
        
        Returns:
            HwndWrapper: Janela TOTVS encontrada.
        
        Raises:
            ElementNotFoundError: Se nenhuma janela TOTVS for encontrada.
        
        Example:
            >>> totvs_window = rm_app.get_totvs_window()
            >>> print(f"Janela TOTVS: {totvs_window.window_text()}")
        
        Note:
            Equivale a get_main_window(".*TOTVS.*").
        """
        return self.app.window(title_re=".*TOTVS.*")
    
    def wait_for_application_ready(self, timeout: int = 60) -> bool:
        """
        Aguarda a aplicação RM ficar completamente carregada e responsiva.
        
        Monitora o estado da aplicação até que esteja completamente
        carregada, com janela principal visível, habilitada e responsiva.
        Essencial após inicialização para garantir estabilidade.
        
        Args:
            timeout (int, optional): Tempo limite em segundos para aguardar
                a aplicação ficar pronta. Defaults to 60.
            
        Returns:
            bool: True se a aplicação ficou pronta dentro do timeout,
                False se timeout foi atingido.
        
        Example:
            Aguardar após inicialização:
            
            >>> app = rm_app.start_application()
            >>> if rm_app.wait_for_application_ready(timeout=120):
            ...     print("Aplicação pronta para uso")
            ... else:
            ...     print("Timeout: aplicação pode não estar pronta")
        
        Note:
            Verifica múltiplos critérios: janela encontrada, estado ready,
            habilitada e visível. Recomendado após start_application().
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
        Coleta e retorna informações detalhadas sobre a aplicação conectada.
        
        Compila informações de status, configuração e estado da aplicação
        para debugging, monitoramento e auditoria.
        
        Returns:
            dict: Dicionário com informações da aplicação contendo:
                - connected: Status da conexão
                - started_by_us: Se iniciamos a aplicação
                - process_id: ID do processo
                - backend: Backend pywinauto usado
                - window_count: Número de janelas (se conectado)
                - main_window_title: Título da janela principal
                - error: Mensagem de erro se houver problema
        
        Example:
            Obter informações para debugging:
            
            >>> info = rm_app.get_application_info()
            >>> print(f"Status: {info['connected']}")
            >>> print(f"PID: {info['process_id']}")
            >>> print(f"Janelas: {info.get('window_count', 'N/A')}")
        
        Note:
            Informações de janela são coletadas apenas se há conexão ativa.
            Erros são capturados e incluídos no campo 'error'.
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