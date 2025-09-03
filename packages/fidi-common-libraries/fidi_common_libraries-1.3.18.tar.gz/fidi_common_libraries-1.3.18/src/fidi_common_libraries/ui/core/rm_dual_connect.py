"""
Módulo de conexão dupla para aplicação TOTVS RM.

Este módulo fornece a classe RMDualConnect que implementa conexão simultânea
com ambos os backends do pywinauto (win32 e UIA) para a aplicação TOTVS RM.
Permite análise comparativa entre backends e geração automática de arquivos
de locators para desenvolvimento e debugging.

A conexão dupla é especialmente útil para:
1. Desenvolvimento de scripts de automação robustos
2. Análise de diferenças entre backends
3. Geração de mapeamentos de elementos
4. Debugging de problemas de compatibilidade

Classes:
    RMDualConnect: Conector principal para conexão dupla

Exemplo:
    Conexão dupla com geração de arquivos:
    
    >>> connector = RMDualConnect(output_dir="locators_output")
    >>> success, info = connector.connect_dual()
    >>> if success:
    ...     print(f"Conectado: {info['main_window']}")
    
    Conexão dupla sem geração de arquivos:
    
    >>> connector = RMDualConnect(generate_files=False)
    >>> success, info = connector.connect_dual()
"""

import io
import logging
from contextlib import redirect_stdout
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

from pywinauto import Application
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.application import WindowSpecification
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError, UIElementNotFoundError
from ..utils.screenshot import capture_screenshot_on_error
from .waits import UIWaits


logger = logging.getLogger(__name__)


class RMDualConnect:
    """
    Conector duplo para aplicação TOTVS RM com ambos os backends.
    
    Esta classe implementa conexão simultânea com os backends win32 e UIA
    do pywinauto para a aplicação TOTVS RM, permitindo análise comparativa
    e geração automática de arquivos de mapeamento de elementos.
    
    A classe executa uma sequência estruturada de conexões:
    1. Conecta via backend win32
    2. Conecta via backend UIA
    3. Obtém janela principal
    4. Obtém controle ribbon
    5. Gera arquivos de locators (opcional)
    
    Attributes:
        config (UIConfig): Configurações de UI carregadas.
        waits (UIWaits): Utilitário para esperas inteligentes.
        generate_files (bool): Se deve gerar arquivos de locators.
        output_dir (Path): Diretório para salvar arquivos gerados.
    
    Example:
        Uso básico com geração de arquivos:
        
        >>> connector = RMDualConnect("output")
        >>> success, info = connector.connect_dual()
        >>> if success:
        ...     print(f"Apps: {info['win32_app']}, {info['uia_app']}")
        
        Uso sem geração de arquivos:
        
        >>> connector = RMDualConnect(generate_files=False)
        >>> success, info = connector.connect_dual()
        >>> print(f"Conectado: {connector.is_connected}")
    
    Note:
        A classe mantém referências internas para ambas as conexões,
        permitindo uso posterior dos objetos conectados.
    """
    
    def __init__(self, output_dir: Optional[str] = None, generate_files: bool = True) -> None:
        """
        Inicializa o conector duplo com configurações de saída.
        
        Configura o conector com diretório de saída e opção de geração
        de arquivos. Cria o diretório se necessário e inicializa o estado
        interno das conexões.
        
        Args:
            output_dir (str, optional): Diretório onde salvar arquivos de
                locators gerados. Se None, usa o diretório atual (".").
                Defaults to None.
            generate_files (bool, optional): Se deve gerar automaticamente
                arquivos de mapeamento de elementos durante a conexão.
                Defaults to True.
        
        Example:
            Conector com diretório personalizado:
            
            >>> connector = RMDualConnect("my_locators")
            
            Conector sem geração de arquivos:
            
            >>> connector = RMDualConnect(generate_files=False)
        
        Note:
            O diretório é criado automaticamente se generate_files=True
            e o diretório não existir.
        """
        self.config = get_ui_config()
        self.waits = UIWaits()
        self.generate_files = generate_files
        self.output_dir = Path(output_dir) if output_dir else Path(".")
        if generate_files:
            self.output_dir.mkdir(exist_ok=True)
        
        # Estado da conexão
        self._win32_app: Optional[Application] = None
        self._uia_app: Optional[Application] = None
        self._main_window: Optional[WindowSpecification] = None
        self._ribbon_control: Optional[WindowSpecification] = None
    
    def connect_dual(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Executa conexão dupla completa com a aplicação TOTVS RM.
        
        Realiza o fluxo completo de conexão dupla em sequência estruturada:
        1. Conecta via backend win32
        2. Conecta via backend UIA
        3. Obtém janela principal
        4. Gera arquivo de locators da janela (se habilitado)
        5. Obtém controle ribbon
        6. Gera arquivo de locators do ribbon (se habilitado)
        7. Retorna informações completas da conexão
        
        Returns:
            Tuple[bool, Dict[str, Any]]: Tupla contendo:
                - bool: True se toda a conexão foi bem-sucedida, False caso contrário
                - Dict[str, Any]: Dicionário com informações da conexão contendo:
                    - 'win32_app': Instância da aplicação win32
                    - 'uia_app': Instância da aplicação UIA
                    - 'main_window': Janela principal conectada
                    - 'ribbon_control': Controle ribbon conectado
                    - 'window_class': Classe da janela utilizada
                    - 'locator_files': Caminhos dos arquivos gerados (se habilitado)
        
        Raises:
            UIConnectionError: Se falhar ao conectar com qualquer backend
                ou ao obter foco na janela principal.
            UIElementNotFoundError: Se não conseguir localizar a janela
                principal ou o controle ribbon.
        
        Example:
            Conexão dupla básica:
            
            >>> success, info = connector.connect_dual()
            >>> if success:
            ...     win32_app = info['win32_app']
            ...     uia_app = info['uia_app']
            ...     main_window = info['main_window']
            ...     print(f"Conectado com sucesso!")
            ... else:
            ...     print("Falha na conexão")
        
        Note:
            Em caso de erro, captura screenshot automaticamente e retorna
            (False, {}) para facilitar tratamento de erros.
        """
        try:
            logger.info("Iniciando conexão dupla com aplicação RM")
            
            # 1. Conexão Win32
            self._connect_win32()
            
            # 2. Conexão UIA
            self._connect_uia()
            
            # 3. Obter janela principal
            self._get_main_window()
            
            # 4. Gerar arquivo da main_window (opcional)
            if self.generate_files:
                self._generate_main_window_file()
            
            # 5. Obter ribbon control
            self._get_ribbon_control()
            
            # 6. Gerar arquivo do ribbon control (opcional)
            if self.generate_files:
                self._generate_ribbon_control_file()
            
            # 7. Preparar informações de retorno
            connection_info = {
                'win32_app': self._win32_app,
                'uia_app': self._uia_app,
                'main_window': self._main_window,
                'ribbon_control': self._ribbon_control,
                'window_class': getattr(self.config, 'window_class', "WindowsForms10.Window.8.app.0.31d2b0c_r9_ad1"),
                'locator_files': {
                    'main_window': self.output_dir / "rm_main_window_locators.txt" if self.generate_files else None,
                    'ribbon_control': self.output_dir / "rm_window_mdiRibbonControl_locators.txt" if self.generate_files else None
                } if self.generate_files else None
            }
            
            logger.info("Conexão dupla concluída com sucesso")
            return True, connection_info
            
        except Exception as e:
            error_msg = f"Erro durante conexão dupla: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_dual_connect_failed")
            return False, {}
    
    def _connect_win32(self) -> None:
        """
        Estabelece conexão com a aplicação via backend win32.
        
        Conecta à aplicação TOTVS RM usando o backend win32 do pywinauto,
        localiza a janela principal e define foco para garantir que a
        aplicação esteja ativa e pronta para interação.
        
        Raises:
            UIConnectionError: Se falhar ao conectar com o processo RM
                ou ao localizar/focar a janela principal.
        
        Note:
            Este é o primeiro passo da conexão dupla. O backend win32
            é geralmente mais rápido para operações básicas.
        """
        try:
            logger.info("Conectando via win32...")
            
            executable_path = self.config.rm_executable_path
            self._win32_app = Application(backend="win32").connect(path=executable_path)
            
            # Obter e focar na janela principal
            window_pattern = self.config.totvs_window_pattern
            window_class = getattr(self.config, 'window_class', "WindowsForms10.Window.8.app.0.31d2b0c_r9_ad1")
            
            temp_window = self._win32_app.window(
                title_re=window_pattern,
                class_name=window_class
            )
            temp_window.set_focus()
            
            logger.info("Aplicação TOTVS conectada com sucesso via win32")
            
        except Exception as e:
            raise UIConnectionError(f"Falha na conexão win32: {e}", str(e))
    
    def _connect_uia(self) -> None:
        """
        Estabelece conexão com a aplicação via backend UIA.
        
        Conecta à aplicação TOTVS RM usando o backend UIA (UI Automation)
        do pywinauto, que oferece melhor acesso a propriedades de
        acessibilidade e elementos mais complexos.
        
        Raises:
            UIConnectionError: Se falhar ao conectar com o processo RM
                via UIA ou se a janela não for encontrada.
        
        Note:
            O backend UIA é mais lento que win32 mas oferece melhor
            acesso a elementos modernos da interface.
        """
        try:
            logger.info("Conectando via uia...")
            
            window_class = getattr(self.config, 'window_class', "WindowsForms10.Window.8.app.0.31d2b0c_r9_ad1")
            window_index = 0
            
            self._uia_app = Application(backend="uia").connect(
                class_name=window_class, 
                found_index=window_index
            )
            
            logger.info("Aplicação TOTVS conectada com sucesso via uia")
            
        except Exception as e:
            raise UIConnectionError(f"Falha na conexão uia: {e}", str(e))
    
    def _get_main_window(self) -> None:
        """
        Localiza e conecta à janela principal da aplicação TOTVS RM.
        
        Utiliza a conexão UIA para obter referência à janela principal
        da aplicação, verificando sua existência e aguardando até que
        esteja pronta para interação.
        
        Raises:
            UIElementNotFoundError: Se a conexão UIA não estiver ativa
                ou se a janela principal não for encontrada.
        
        Note:
            A janela principal é identificada pela classe da janela
            configurada e é essencial para todas as operações subsequentes.
        """
        try:
            if self._uia_app is None:
                raise UIElementNotFoundError("UIA app não conectada", "UIA app is None")
                
            window_class = getattr(self.config, 'window_class', "WindowsForms10.Window.8.app.0.31d2b0c_r9_ad1")
            window_index = 0
            
            self._main_window = self._uia_app.window(
                class_name=window_class, 
                found_index=window_index
            )
            
            # Verificar se a janela existe
            self._main_window.wait('exists', timeout=10)
            logger.info("Main Window conectada com sucesso")
            
        except Exception as e:
            raise UIElementNotFoundError("Falha ao obter main window", str(e))
    
    def _get_ribbon_control(self) -> None:
        """
        Localiza e conecta ao controle ribbon da aplicação TOTVS RM.
        
        Busca pelo elemento mdiRibbonControl dentro da janela principal,
        que é o container principal de todos os elementos do ribbon
        no sistema TOTVS RM.
        
        Raises:
            UIElementNotFoundError: Se a janela principal não estiver
                conectada ou se o controle mdiRibbonControl não for encontrado.
        
        Note:
            O ribbon control é fundamental para navegação no sistema RM
            e contém todas as abas e botões principais da interface.
        """
        try:
            if self._main_window is None:
                raise UIElementNotFoundError("Main window não conectada", "Main window is None")
                
            self._ribbon_control = self._main_window.child_window(
                auto_id="mdiRibbonControl", 
                control_type="Pane"
            )
            
            # Verificar se o controle existe
            self._ribbon_control.wait('exists', timeout=10)
            logger.info("mdiRibbonControl conectado com sucesso")
            
        except Exception as e:
            raise UIElementNotFoundError("Falha ao obter ribbon control", str(e))
    
    def _generate_main_window_file(self) -> None:
        """
        Gera arquivo de mapeamento de elementos da janela principal.
        
        Cria arquivo de texto contendo todos os identificadores de controle
        da janela principal, útil para desenvolvimento e debugging de
        scripts de automação.
        
        Note:
            O arquivo é gerado apenas se generate_files=True e se a
            janela principal estiver disponível. Falhas são logadas
            como warnings sem interromper o fluxo.
        """
        try:
            if self._main_window is None:
                logger.warning("Main window não disponível para geração de arquivo")
                return
                
            main_window_file = self.output_dir / "rm_main_window_locators.txt"
            self._generate_control_identifiers_file(
                self._main_window, 
                main_window_file,
                "Main Window"
            )
            logger.info(f"Arquivo main_window gerado: {main_window_file}")
            
        except Exception as e:
            logger.warning(f"Erro ao gerar arquivo main_window: {e}")
    
    def _generate_ribbon_control_file(self) -> None:
        """
        Gera arquivo de mapeamento de elementos do controle ribbon.
        
        Cria arquivo de texto contendo todos os identificadores de controle
        do ribbon, incluindo abas, botões e grupos, essencial para
        desenvolvimento de navegação no sistema RM.
        
        Note:
            O arquivo é gerado apenas se generate_files=True e se o
            ribbon control estiver disponível. Falhas são logadas
            como warnings sem interromper o fluxo.
        """
        try:
            if self._ribbon_control is None:
                logger.warning("Ribbon control não disponível para geração de arquivo")
                return
                
            ribbon_file = self.output_dir / "rm_window_mdiRibbonControl_locators.txt"
            self._generate_control_identifiers_file(
                self._ribbon_control,
                ribbon_file,
                "Ribbon Control"
            )
            logger.info(f"Arquivo ribbon_control gerado: {ribbon_file}")
            
        except Exception as e:
            logger.warning(f"Erro ao gerar arquivo ribbon_control: {e}")
    
    def _generate_control_identifiers_file(
        self, 
        control, 
        file_path: Path,
        description: str
    ) -> None:
        """
        Gera arquivo de texto com identificadores de um controle específico.
        
        Utiliza o método print_control_identifiers() do pywinauto para
        capturar todos os identificadores do controle e salva em arquivo
        de texto com cabeçalho informativo.
        
        Args:
            control: Controle do pywinauto para extrair identificadores.
                Pode ser WindowSpecification ou qualquer wrapper de elemento.
            file_path (Path): Caminho completo onde salvar o arquivo gerado.
            description (str): Descrição do controle para incluir no cabeçalho
                do arquivo.
        
        Note:
            Usa redirect_stdout para capturar a saída do print_control_identifiers()
            e salva com codificação UTF-8. Erros são logados sem interromper execução.
        """
        try:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                control.print_control_identifiers()
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# {description} - Control Identifiers\n")
                f.write(f"# Generated by RMDualConnect\n\n")
                f.write(buffer.getvalue())
            
            logger.debug(f"Arquivo gerado: {file_path}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo {file_path}: {e}")
    
    def disconnect(self) -> None:
        """
        Desconecta de todas as aplicações e limpa referências.
        
        Remove todas as referências internas para aplicações e elementos
        conectados, liberando recursos e permitindo reconexão posterior
        se necessário.
        
        Note:
            Após chamar este método, is_connected retornará False e
            será necessário chamar connect_dual() novamente para
            restabelecer as conexões.
        """
        logger.info("Desconectando das aplicações")
        
        self._win32_app = None
        self._uia_app = None
        self._main_window = None
        self._ribbon_control = None
    
    @property
    def is_connected(self) -> bool:
        """
        Verifica se todas as conexões essenciais estão ativas.
        
        Checa se as conexões win32, UIA e janela principal estão
        todas estabelecidas e prontas para uso.
        
        Returns:
            bool: True se win32_app, uia_app e main_window estão
                todos conectados, False caso contrário.
        
        Example:
            >>> if connector.is_connected:
            ...     print("Pronto para usar")
            ... else:
            ...     print("Precisa conectar primeiro")
        """
        return (
            self._win32_app is not None and 
            self._uia_app is not None and 
            self._main_window is not None
        )
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Retorna informações detalhadas sobre o estado das conexões.
        
        Fornece status detalhado de cada componente da conexão dupla,
        útil para debugging e monitoramento do estado do conector.
        
        Returns:
            Dict[str, Any]: Dicionário contendo:
                - 'win32_connected': Se a conexão win32 está ativa
                - 'uia_connected': Se a conexão UIA está ativa
                - 'main_window_ready': Se a janela principal está pronta
                - 'ribbon_control_ready': Se o ribbon control está pronto
                - 'output_dir': Diretório de saída configurado
        
        Example:
            >>> info = connector.get_connection_info()
            >>> print(f"Win32: {info['win32_connected']}")
            >>> print(f"UIA: {info['uia_connected']}")
        """
        return {
            'win32_connected': self._win32_app is not None,
            'uia_connected': self._uia_app is not None,
            'main_window_ready': self._main_window is not None,
            'ribbon_control_ready': self._ribbon_control is not None,
            'output_dir': str(self.output_dir)
        }


# Exemplo de uso
if __name__ == "__main__":
    """
    Exemplo prático de uso do RMDualConnect.
    
    Este exemplo demonstra como usar o conector duplo para estabelecer
    conexão simultânea com ambos os backends do pywinauto e gerar
    arquivos de mapeamento de elementos para desenvolvimento.
    
    Mostra tanto o uso com geração de arquivos quanto sem geração,
    e como acessar as informações retornadas pela conexão.
    """
    try:
        # Criar conector (com geração de arquivos)
        connector = RMDualConnect(output_dir="locators_output", generate_files=True)
        
        # Ou sem geração de arquivos
        # connector = RMDualConnect(generate_files=False)
        
        # Realizar conexão dupla
        success, info = connector.connect_dual()
        
        if success:
            print("Conexão dupla realizada com sucesso!")
            print(f"Win32 App: {info['win32_app']}")
            print(f"UIA App: {info['uia_app']}")
            print(f"Main Window: {info['main_window']}")
            print(f"Ribbon Control: {info['ribbon_control']}")
            print(f"Arquivos gerados: {info['locator_files']}")
        else:
            print("Falha na conexão dupla")
            
    except Exception as e:
        print(f"Erro no exemplo: {e}")