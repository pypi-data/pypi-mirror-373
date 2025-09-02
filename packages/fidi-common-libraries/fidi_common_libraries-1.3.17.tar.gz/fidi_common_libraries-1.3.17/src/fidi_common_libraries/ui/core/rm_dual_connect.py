"""
Conector duplo para aplicação RM.

Fornece funcionalidades para conexão dupla (win32 + uia) com a aplicação RM,
incluindo geração de arquivos de locators para análise e desenvolvimento.
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
    Conector duplo para aplicação RM.
    
    Realiza conexão dupla (win32 + uia) com a aplicação RM e gera
    arquivos de locators para análise e desenvolvimento.
    """
    
    def __init__(self, output_dir: Optional[str] = None, generate_files: bool = True):
        """
        Inicializa o conector duplo.
        
        Args:
            output_dir: Diretório para salvar arquivos de locators.
                       Se None, usa diretório atual.
            generate_files: Se deve gerar arquivos de locators automaticamente.
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
        Realiza conexão dupla com a aplicação RM.
        
        Executa o fluxo completo: conexão win32 → conexão uia → 
        obtenção de janelas → geração de locators.
        
        Returns:
            Tuple[bool, Dict[str, Any]]:
                - (True, info_dict) se conexão bem-sucedida
                - (False, {}) se falhar
                
        Raises:
            UIConnectionError: Se não conseguir conectar.
            UIElementNotFoundError: Se elementos não forem encontrados.
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
        Realiza conexão via backend win32.
        
        Raises:
            UIConnectionError: Se não conseguir conectar.
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
        Realiza conexão via backend uia.
        
        Raises:
            UIConnectionError: Se não conseguir conectar.
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
        Obtém a janela principal da aplicação.
        
        Raises:
            UIElementNotFoundError: Se a janela não for encontrada.
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
        Obtém o controle ribbon da aplicação.
        
        Raises:
            UIElementNotFoundError: Se o controle não for encontrado.
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
        Gera arquivo de locators da main_window imediatamente após instanciação.
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
        Gera arquivo de locators do ribbon control imediatamente após instanciação.
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
        Gera arquivo com identificadores de controle.
        
        Args:
            control: Controle para gerar identificadores.
            file_path: Caminho do arquivo de saída.
            description: Descrição do controle.
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
        Desconecta das aplicações.
        
        Limpa as referências e libera recursos.
        """
        logger.info("Desconectando das aplicações")
        
        self._win32_app = None
        self._uia_app = None
        self._main_window = None
        self._ribbon_control = None
    
    @property
    def is_connected(self) -> bool:
        """
        Verifica se as conexões estão ativas.
        
        Returns:
            bool: True se ambas as conexões estão ativas.
        """
        return (
            self._win32_app is not None and 
            self._uia_app is not None and 
            self._main_window is not None
        )
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Retorna informações das conexões ativas.
        
        Returns:
            Dict[str, Any]: Informações das conexões.
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
    Exemplo de uso do RMDualConnect.
    
    Este exemplo demonstra como usar o conector duplo para
    conectar à aplicação RM e gerar arquivos de locators.
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