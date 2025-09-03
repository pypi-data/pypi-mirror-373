"""
Conector único para aplicação RM.

Fornece funcionalidades para conexão robusta com a aplicação RM,
incluindo retry automático, captura de screenshots e validação estrutural.
"""

import logging
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

import yaml
from pywinauto import Application, Desktop

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIConnectionError, UIElementNotFoundError
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


class RMSingleConnect:
    """
    Conector único para aplicação RM.
    
    Realiza conexão robusta com a aplicação RM usando backend único,
    com funcionalidades enterprise como retry automático, screenshots
    e validação estrutural opcional.
    """
    
    def __init__(
        self,
        backend: str = "uia",
        screenshot_enabled: bool = False,
        screenshot_dir: Optional[str] = None,
        retries: int = 3,
        delay: float = 2.0,
        control_retry: int = 3,
        control_delay: float = 1.0
    ):
        """
        Inicializa o conector único.
        
        Args:
            backend: Backend de automação ("win32" ou "uia").
            screenshot_enabled: Se deve capturar screenshots das janelas.
            screenshot_dir: Diretório para salvar screenshots.
            retries: Número de tentativas de conexão global.
            delay: Delay entre tentativas de conexão (segundos).
            control_retry: Tentativas por controle/janela individual.
            control_delay: Delay entre tentativas de controle (segundos).
        """
        self.config = get_ui_config()
        self.backend = backend
        self.screenshot_enabled = screenshot_enabled
        self.retries = retries
        self.delay = delay
        self.control_retry = control_retry
        self.control_delay = control_delay
        
        # Configurar diretório de screenshots
        if screenshot_dir:
            self.screenshot_dir = Path(screenshot_dir)
        else:
            self.screenshot_dir = Path("screenshots")
        
        if screenshot_enabled:
            self.screenshot_dir.mkdir(exist_ok=True)
        
        # Estado da conexão
        self._app: Optional[Application] = None
        self._connected_windows: Dict[str, Dict[str, Any]] = {}
    
    def connect_single(
        self,
        titulos: Optional[List[str]] = None,
        classe: Optional[str] = None,
        pid: Optional[int] = None,
        yaml_expected: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Conecta no TOTVS RM com funcionalidades enterprise avançadas.
        
        Args:
            titulos: Lista de títulos para buscar janelas RM.
            classe: Nome da classe da janela para conexão.
            pid: Process ID específico para conexão direta.
            yaml_expected: Arquivo YAML para validação estrutural.
        
        Returns:
            Tuple[bool, Dict[str, Any]]:
                - (True, janelas_dict) se conexão bem-sucedida
                - (False, {}) se falhar
        
        Raises:
            UIConnectionError: Se não conseguir conectar após todas as tentativas.
        """
        try:
            logger.info("Iniciando conexão única com aplicação RM")
            
            # 1. Estabelecer conexão com retry
            success = self._establish_connection(titulos, classe, pid)
            if not success:
                return False, {}
            
            # 2. Capturar janelas
            self._capture_windows()
            
            # 3. Validação estrutural (opcional)
            if yaml_expected:
                self._validate_structure(yaml_expected)
            
            logger.info(f"Conexão única estabelecida com {len(self._connected_windows)} janelas")
            return True, self._connected_windows
            
        except Exception as e:
            error_msg = f"Erro durante conexão única: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_single_connect_failed")
            return False, {}
    
    def _establish_connection(
        self,
        titulos: Optional[List[str]],
        classe: Optional[str],
        pid: Optional[int]
    ) -> bool:
        """
        Estabelece conexão com retry automático.
        
        Args:
            titulos: Lista de títulos para buscar.
            classe: Classe da janela.
            pid: Process ID.
        
        Returns:
            bool: True se conexão bem-sucedida.
        """
        for attempt in range(1, self.retries + 1):
            try:
                logger.info(f"Tentativa {attempt}/{self.retries} para conectar RM")
                
                if pid:
                    self._app = Application(backend=self.backend).connect(process=pid)
                elif classe:
                    janela = Desktop(backend=self.backend).window(class_name=classe)
                    pid_found = janela.process_id()
                    self._app = Application(backend=self.backend).connect(process=pid_found)
                elif titulos:
                    for titulo in titulos:
                        try:
                            janela = Desktop(backend=self.backend).window(title_re=f".*{titulo}.*")
                            pid_found = janela.process_id()
                            self._app = Application(backend=self.backend).connect(process=pid_found)
                            break
                        except Exception:
                            continue
                
                # Fallback: buscar qualquer janela com "RM"
                if not self._app:
                    for w in Desktop(backend=self.backend).windows():
                        if "RM" in w.window_text():
                            pid_found = w.process_id()
                            self._app = Application(backend=self.backend).connect(process=pid_found)
                            break
                
                if self._app:
                    logger.info("Conexão estabelecida com sucesso")
                    return True
                    
            except Exception as e:
                logger.warning(f"Falha na tentativa {attempt}: {e}")
                if attempt < self.retries:
                    time.sleep(self.delay)
        
        logger.error("Não foi possível estabelecer conexão com o TOTVS RM")
        return False
    
    def _capture_windows(self) -> None:
        """
        Captura informações de todas as janelas da aplicação.
        """
        if not self._app:
            return
        
        for window in self._app.windows():
            try:
                window_info = self._process_window(window)
                if window_info:
                    handle = str(window.handle)
                    self._connected_windows[handle] = window_info
                    
            except Exception as e:
                logger.error(f"Falha ao processar janela {window.window_text()}: {e}")
                continue
    
    def _process_window(self, window) -> Optional[Dict[str, Any]]:
        """
        Processa uma janela individual com retry.
        
        Args:
            window: Janela a ser processada.
        
        Returns:
            Dict com informações da janela ou None se falhar.
        """
        img_path = None
        
        # Capturar screenshot com retry
        if self.screenshot_enabled:
            for attempt in range(1, self.control_retry + 1):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_title = self._sanitize_filename(window.window_text())
                    img_path = self.screenshot_dir / f"{timestamp}_{safe_title}.png"
                    window.capture_as_image().save(str(img_path))
                    break
                except Exception as e:
                    logger.warning(f"Tentativa {attempt} falhou para screenshot: {e}")
                    if attempt < self.control_retry:
                        time.sleep(self.control_delay)
        
        # Criar wrapper híbrido compatível
        hybrid_wrapper = self._create_hybrid_wrapper(window)
        
        return {
            "title": window.window_text(),
            "pid": window.process_id(),
            "element": hybrid_wrapper,  # Wrapper híbrido para compatibilidade
            "raw_element": window,     # Elemento original
            "screenshot": str(img_path) if img_path else None
        }
    
    def _sanitize_filename(self, filename: str, max_length: int = 40) -> str:
        """
        Sanitiza nome de arquivo removendo caracteres inválidos.
        
        Args:
            filename: Nome original.
            max_length: Comprimento máximo.
        
        Returns:
            Nome sanitizado.
        """
        # Remover caracteres inválidos
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        
        # Substituir espaços e limitar comprimento
        filename = filename.replace(" ", "_")[:max_length]
        
        return filename if filename else "unnamed"
    
    def _create_hybrid_wrapper(self, window):
        """
        Cria wrapper híbrido compatível com RMNavigator e RMAdaptNavigator.
        
        Args:
            window: Janela original do pywinauto.
            
        Returns:
            Wrapper híbrido com métodos necessários.
        """
        logger.debug(f"Criando HybridWrapper para: {type(window)} - {getattr(window, 'window_text', lambda: 'N/A')()}")
        
        # Definir HybridWrapper fora para permitir referência recursiva
        class HybridWrapper:
            def __init__(self, original_window):
                self._window = original_window
                # Expor atributos essenciais para compatibilidade
                self.handle = getattr(original_window, 'handle', None)
                self.element_info = getattr(original_window, 'element_info', None)
                logger.debug(f"HybridWrapper criado para: {type(original_window)}")
            
            def child_window(self, **criteria):
                """Compatibilidade com RMNavigator e RMAdaptNavigator."""
                logger.debug(f"HybridWrapper.child_window chamado com: {criteria}")
                try:
                    # Para UIAWrapper, usar método correto baseado nos critérios
                    if 'UIAWrapper' in str(type(self._window)):
                        logger.debug("Processando UIAWrapper")
                        # UIAWrapper usa diferentes métodos dependendo dos critérios
                        if 'title' in criteria:
                            # Buscar por título usando descendants
                            for child in self._window.descendants():
                                if hasattr(child, 'window_text') and criteria['title'] in child.window_text():
                                    return HybridWrapper(child)
                        elif 'control_type' in criteria:
                            # Buscar por tipo de controle
                            for child in self._window.descendants():
                                if hasattr(child, 'element_info') and child.element_info.control_type == criteria['control_type']:
                                    return HybridWrapper(child)
                        else:
                            # Fallback: usar primeiro descendente que atenda aos critérios
                            for child in self._window.descendants():
                                match = True
                                for key, value in criteria.items():
                                    if hasattr(child, key) and getattr(child, key) != value:
                                        match = False
                                        break
                                if match:
                                    return HybridWrapper(child)
                        
                        # Se não encontrou, lançar exceção
                        raise Exception(f"Elemento não encontrado com critérios: {criteria}")
                    else:
                        logger.debug("Usando child_window() para outros tipos")
                        child = self._window.child_window(**criteria)
                        return HybridWrapper(child)
                    
                except Exception as e:
                    logger.error(f"Erro em child_window: {e}")
                    raise e
            
            def window(self, **criteria):
                """Método window para compatibilidade direta."""
                logger.debug(f"HybridWrapper.window chamado com: {criteria}")
                try:
                    child = self._window.window(**criteria)
                    return HybridWrapper(child)
                except Exception as e:
                    logger.error(f"Erro em window: {e}")
                    raise e
            
            def __getattr__(self, name):
                """Delegar todas as chamadas não implementadas para o elemento original."""
                logger.debug(f"HybridWrapper.__getattr__ chamado para: {name}")
                if not hasattr(self._window, name):
                    logger.error(f"Elemento {type(self._window)} não tem atributo: {name}")
                    raise AttributeError(f"'{type(self._window).__name__}' object has no attribute '{name}'")
                
                attr = getattr(self._window, name)
                return attr
            
            def window_text(self):
                """Texto da janela."""
                return self._window.window_text()
            
            def process_id(self):
                """ID do processo."""
                return self._window.process_id()
            
            def exists(self, timeout=None):
                """Verifica existência com timeout opcional."""
                if timeout is not None:
                    return self._window.exists(timeout=timeout)
                return self._window.exists()
            
            def wait(self, wait_for, timeout=None, retry_interval=None):
                """Espera por condições."""
                return self._window.wait(wait_for, timeout, retry_interval)
            
            def draw_outline(self):
                """Destaque visual."""
                return self._window.draw_outline()
            
            def click_input(self, **kwargs):
                """Clique com parâmetros."""
                return self._window.click_input(**kwargs)
            
            def set_focus(self):
                """Foco na janela."""
                return self._window.set_focus()
            
            def capture_as_image(self):
                """Captura de screenshot."""
                return self._window.capture_as_image()
            
            def children(self):
                """Filhos da janela."""
                return self._window.children()
            
            # Métodos adicionais para compatibilidade total
            def __str__(self):
                return f"HybridWrapper({self._window})"
            
            def __repr__(self):
                return f"HybridWrapper({repr(self._window)})"
        
        wrapper = HybridWrapper(window)
        logger.debug(f"HybridWrapper criado com sucesso: {wrapper}")
        return wrapper
    
    def _validate_structure(self, yaml_path: str) -> None:
        """
        Valida estrutura das janelas contra arquivo YAML.
        
        Args:
            yaml_path: Caminho para arquivo YAML de validação.
        """
        try:
            expected_structure = self._load_yaml_structure(yaml_path)
            
            for handle, window_info in self._connected_windows.items():
                real_tree = self._extract_window_tree(window_info["element"], depth=2)
                
                for expected_window in expected_structure.get("expected_windows", []):
                    errors = self._validate_tree(real_tree, expected_window, f"[handle {handle}]")
                    
                    if errors:
                        logger.warning(f"Divergências encontradas para handle {handle}:\n" + "\n".join(errors))
                    else:
                        logger.info(f"[handle {handle}] Estrutura validada com sucesso!")
                        
        except Exception as e:
            logger.warning(f"Erro durante validação estrutural: {e}")
    
    def _load_yaml_structure(self, yaml_path: str) -> Dict[str, Any]:
        """
        Carrega estrutura esperada do arquivo YAML.
        
        Args:
            yaml_path: Caminho para o arquivo YAML.
        
        Returns:
            Estrutura carregada do YAML.
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _extract_window_tree(self, window, depth: int = 2) -> Dict[str, Any]:
        """
        Extrai árvore de elementos da janela.
        
        Args:
            window: Janela para extrair árvore.
            depth: Profundidade da extração.
        
        Returns:
            Árvore de elementos.
        """
        # Usar elemento original para extração de árvore
        raw_window = getattr(window, '_window', window)
        
        element_info = getattr(raw_window, "element_info", None)
        control_type = getattr(element_info, "control_type", None) if element_info else None
        
        node = {
            "title": raw_window.window_text(),
            "control_type": control_type,
            "children": []
        }
        
        if depth > 0:
            try:
                for child in raw_window.children():
                    node["children"].append(self._extract_window_tree(child, depth - 1))
            except Exception as e:
                logger.debug(f"Erro ao extrair filhos: {e}")
        
        return node
    
    def _validate_tree(self, real: Dict[str, Any], expected: Dict[str, Any], path: str = "") -> List[str]:
        """
        Valida árvore real contra esperada.
        
        Args:
            real: Árvore real extraída.
            expected: Árvore esperada do YAML.
            path: Caminho atual na validação.
        
        Returns:
            Lista de erros encontrados.
        """
        errors = []
        
        # Elementos dinâmicos do RM que podem não estar presentes
        dynamic_elements = {
            'Minimize', 'Maximize', 'Close',
            'barSubItemContext', 'biWindowMDI', 'barSubItemWindows',
            'barSubItemStartup', 'bBISelfService',
            'Administração de Pessoal', 'Folha Mensal', 'Férias',
            'Rescisão', 'Encargos', 'Anuais', 'eSocial',
            'Orçamento (beta)', 'Configurações', 'Assinatura Eletrônica',
            'Customização', 'Gestão', 'Ambiente',
            'btShowDockedWindows', 'barButtonHelp', 'System'
        }
        
        # Validar título
        if "title" in expected and expected["title"] not in real.get("title", ""):
            errors.append(f"{path}: esperado título '{expected['title']}' mas obtido '{real.get('title')}'")
        
        # Validar tipo de controle
        if "control_type" in expected and expected["control_type"] != real.get("control_type"):
            errors.append(f"{path}: esperado control_type '{expected['control_type']}' mas obtido '{real.get('control_type')}'")
        
        # Validar filhos
        for idx, child_expected in enumerate(expected.get("children", [])):
            child_title = child_expected.get('title', '')
            
            # Pular validação de elementos dinâmicos
            if child_title in dynamic_elements:
                continue
            
            if idx < len(real.get("children", [])):
                errors.extend(self._validate_tree(
                    real["children"][idx], 
                    child_expected, 
                    path + f"/{child_title}"
                ))
            else:
                # Só reportar erro se não for elemento dinâmico
                if child_title not in dynamic_elements:
                    errors.append(f"{path}: filho esperado '{child_title}' não encontrado")
        
        return errors
    
    def generate_yaml_baseline(
        self,
        output_file: Optional[str] = None,
        depth: int = 3
    ) -> str:
        """
        Gera baseline YAML da estrutura atual.
        
        Args:
            output_file: Arquivo de saída. Se None, usa padrão.
            depth: Profundidade da extração.
        
        Returns:
            Caminho do arquivo gerado.
        """
        if not self._app:
            raise UIConnectionError("Aplicação não conectada", "App is None")
        
        if not output_file:
            output_path = self.screenshot_dir / "rm_baseline.yaml"
        else:
            output_path = Path(output_file)
        
        baseline = {"expected_windows": []}
        
        for window in self._app.windows():
            baseline["expected_windows"].append(self._extract_window_tree(window, depth))
        
        # Criar diretório se não existir
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(baseline, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"Baseline YAML gerado em: {output_path}")
        return str(output_path)
    
    def get_connected_windows(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna dicionário de janelas conectadas.
        
        Returns:
            Dicionário com informações das janelas.
        """
        return self._connected_windows.copy()
    
    def get_main_window(self):
        """
        Obtém a janela principal compatível com RMNavigator.
        
        Returns:
            Wrapper híbrido da janela principal ou None se não conectada.
        """
        if not self._connected_windows:
            logger.error("Nenhuma janela conectada")
            return None
        
        logger.debug(f"Janelas conectadas: {len(self._connected_windows)}")
        
        # Retorna a primeira janela (geralmente a principal)
        first_window = next(iter(self._connected_windows.values()))
        element = first_window.get('element')
        raw_element = first_window.get('raw_element')
        
        logger.debug(f"Elemento obtido: {type(element)}")
        logger.debug(f"Raw element: {type(raw_element)}")
        logger.debug(f"Element tem _window: {hasattr(element, '_window')}")
        logger.debug(f"Element tem child_window: {hasattr(element, 'child_window')}")
        
        # Verificar se já é HybridWrapper
        if hasattr(element, '_window'):
            logger.debug(f"Retornando HybridWrapper existente: {type(element)}")
            return element
        
        # Se não for HybridWrapper, criar um novo
        logger.warning(f"Elemento não é HybridWrapper ({type(element)}), criando wrapper")
        if raw_element:
            logger.debug(f"Usando raw_element para criar wrapper: {type(raw_element)}")
            return self._create_hybrid_wrapper(raw_element)
        else:
            logger.debug(f"Usando element para criar wrapper: {type(element)}")
            return self._create_hybrid_wrapper(element)
    
    def get_application(self) -> Optional[Application]:
        """
        Retorna a aplicação conectada.
        
        Returns:
            Instância da aplicação ou None se não conectada.
        """
        return self._app
    
    def disconnect(self) -> None:
        """
        Desconecta da aplicação e limpa recursos.
        """
        self._app = None
        self._connected_windows.clear()
        logger.info("Desconectado da aplicação RM")


def connect_single(
    titulos: Optional[List[str]] = None,
    classe: Optional[str] = None,
    pid: Optional[int] = None,
    backend: str = "uia",
    screenshot: bool = False,
    screenshot_dir: str = "screenshots",
    retries: int = 3,
    delay: float = 2.0,
    yaml_expected: Optional[str] = None,
    control_retry: int = 3,
    control_delay: float = 1.0
) -> Dict[str, Any]:
    """
    Função de conveniência para conexão única com RM.
    
    Args:
        titulos: Lista de títulos para buscar janelas RM.
        classe: Nome da classe da janela para conexão.
        pid: Process ID específico para conexão direta.
        backend: Backend de automação ("win32" ou "uia").
        screenshot: Se deve capturar screenshots das janelas.
        screenshot_dir: Diretório para salvar screenshots.
        retries: Número de tentativas de conexão global.
        delay: Delay entre tentativas de conexão (segundos).
        yaml_expected: Arquivo YAML para validação estrutural.
        control_retry: Tentativas por controle/janela individual.
        control_delay: Delay entre tentativas de controle (segundos).
    
    Returns:
        Dict[str, Any]: Dicionário com handles das janelas encontradas.
    
    Example:
        >>> # Conexão básica com UIA
        >>> janelas = connect_single(
        ...     titulos=["CorporeRM", "TOTVS"],
        ...     backend="uia",
        ...     screenshot=True
        ... )
        
        >>> # Conexão via PID específico
        >>> janelas = connect_single(
        ...     pid=1234,
        ...     backend="uia",
        ...     retries=5
        ... )
    """
    connector = RMSingleConnect(
        backend=backend,
        screenshot_enabled=screenshot,
        screenshot_dir=screenshot_dir,
        retries=retries,
        delay=delay,
        control_retry=control_retry,
        control_delay=control_delay
    )
    
    success, windows = connector.connect_single(
        titulos=titulos,
        classe=classe,
        pid=pid,
        yaml_expected=yaml_expected
    )
    
    return windows if success else {}


# Exemplo de uso com compatibilidade híbrida
if __name__ == "__main__":
    """
    Exemplo de uso do RMSingleConnect com compatibilidade híbrida.
    
    Demonstra como usar o conector com RMNavigator e RMAdaptNavigator.
    """
    try:
        # Conectar usando RMSingleConnect
        connector = RMSingleConnect(
            backend="uia",
            screenshot_enabled=True,
            retries=3
        )
        
        success, windows = connector.connect_single(
            titulos=["TOTVS", "CorporeRM"]
        )
        
        if success:
            print(f"Conectado a {len(windows)} janelas")
            
            # Obter janela principal compatível
            main_window = connector.get_main_window()
            app = connector.get_application()
            
            if main_window and app:
                # Usar com RMNavigator
                from .rm_navigator import RMNavigator
                navigator = RMNavigator(app, main_window)  # type: ignore[arg-type]
                
                # Usar com RMAdaptNavigator
                from .rm_adapt_navigator import RMAdaptNavigator
                adapt_navigator = RMAdaptNavigator(main_window)  # type: ignore[arg-type]
                
                print("Compatibilidade híbrida funcionando!")
            
        else:
            print("Falha na conexão")
            
    except Exception as e:
        print(f"Erro no exemplo: {e}")