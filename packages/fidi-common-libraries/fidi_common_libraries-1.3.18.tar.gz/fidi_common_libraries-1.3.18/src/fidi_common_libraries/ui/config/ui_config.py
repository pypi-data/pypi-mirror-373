"""
Módulo de configurações para automação de UI no projeto FIDI.

Este módulo centraliza todas as configurações relacionadas à automação de interfaces
gráficas, especialmente para o sistema TOTVS RM. Fornece uma classe de configuração
com valores padrão sensatos e suporte a override via variáveis de ambiente.

Classes:
    UIConfig: Classe de configuração principal com todos os parâmetros de UI

Funções:
    get_ui_config: Factory function para obter configuração com overrides de ambiente

Exemplo:
    >>> config = get_ui_config()
    >>> print(config.default_timeout)
    30
    >>> # Com variável de ambiente UI_DEFAULT_TIMEOUT=60
    >>> config = get_ui_config()
    >>> print(config.default_timeout)
    60
"""

from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class UIConfig:
    """
    Classe de configuração para automação de UI.
    
    Esta classe centraliza todas as configurações necessárias para automação
    de interfaces gráficas, incluindo timeouts, tentativas, configurações do
    sistema RM e opções de logging e screenshots.
    
    Attributes:
        default_timeout (int): Timeout padrão para operações gerais em segundos.
        element_timeout (int): Timeout para encontrar elementos em segundos.
        click_timeout (int): Timeout para operações de clique em segundos.
        type_timeout (int): Timeout para operações de digitação em segundos.
        wait_before_click (float): Espera antes de clicar em segundos.
        wait_after_click (float): Espera após clicar em segundos.
        wait_between_retries (float): Espera entre tentativas em segundos.
        wait_before_next_window (float): Espera antes da próxima janela em segundos.
        max_retry_attempts (int): Número máximo de tentativas para operações.
        max_connection_attempts (int): Número máximo de tentativas de conexão.
        backend (str): Backend do pywinauto a ser usado ('win32' ou 'uia').
        window_title (List[str]): Lista de títulos de janela para busca.
        process_name (str): Nome do processo da aplicação RM.
        rm_executable_path (str): Caminho completo para o executável do RM.
        start_wait_time (int): Tempo de espera após iniciar aplicação em segundos.
        totvs_window_pattern (str): Padrão para identificar janelas TOTVS.
        application_ready_timeout (int): Timeout para aplicação ficar pronta em segundos.
        window_class (str): Classe da janela principal do RM.
        screenshot_on_error (bool): Se deve capturar screenshots em caso de erro.
        screenshot_dir (str): Diretório para salvar screenshots.
        log_level (str): Nível de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR').
        log_interactions (bool): Se deve logar interações com elementos.
    
    Example:
        Uso básico:
        
        >>> config = UIConfig()
        >>> print(config.default_timeout)
        30
        
        Customização:
        
        >>> config = UIConfig(
        ...     default_timeout=60,
        ...     backend='uia',
        ...     screenshot_on_error=False
        ... )
        >>> print(config.backend)
        'uia'
    """

    # Timeouts
    default_timeout: int = 30
    element_timeout: int = 10
    click_timeout: int = 5
    type_timeout: int = 3

    # Esperas
    wait_before_click: float = 0.5
    wait_after_click: float = 0.5
    wait_between_retries: float = 2.0
    wait_before_next_window: float = 10.0

    # Tentativas
    max_retry_attempts: int = 3
    max_connection_attempts: int = 5

    # Backend
    backend: str = "win32"

    # Sistema RM
    window_title: List[str] = field(default_factory=lambda: ["RM"])
    process_name: str = "RM"
    rm_executable_path: str = r"C:\totvs\CorporeRM\RM.Net\RM.exe"
    start_wait_time: int = 5
    totvs_window_pattern: str = "MainForm"
    application_ready_timeout: int = 60
    window_class: str = "WindowsForms10.Window.8.app.0.31d2b0c_r9_ad1"

    # Screenshots
    screenshot_on_error: bool = True
    screenshot_dir: str = "screenshots"

    # Logging
    log_level: str = "INFO"
    log_interactions: bool = True


def get_ui_config() -> UIConfig:
    """
    Factory function para obter configuração de UI com overrides de ambiente.
    
    Esta função cria uma instância de UIConfig com valores padrão e aplica
    overrides baseados em variáveis de ambiente, permitindo customização
    sem modificar código.
    
    Variáveis de ambiente suportadas:
        UI_DEFAULT_TIMEOUT (int): Timeout padrão em segundos
        RM_EXECUTABLE_PATH (str): Caminho para executável do RM
        RM_START_WAIT_TIME (int): Tempo de espera após iniciar RM
        RM_TOTVS_WINDOW_PATTERN (str): Padrão para janelas TOTVS
        RM_APP_READY_TIMEOUT (int): Timeout para aplicação ficar pronta
        RM_WINDOW_TITLE (str): Títulos de janela separados por vírgula
        RM_PROCESS_NAME (str): Nome do processo RM
        UI_SCREENSHOT_ON_ERROR (bool): 'true'/'false' para screenshots
        UI_LOG_LEVEL (str): Nível de logging
    
    Returns:
        UIConfig: Instância configurada com valores padrão e overrides de ambiente.
    
    Example:
        Uso básico:
        
        >>> config = get_ui_config()
        >>> print(config.default_timeout)
        30
        
        Com variáveis de ambiente:
        
        >>> import os
        >>> os.environ['UI_DEFAULT_TIMEOUT'] = '60'
        >>> os.environ['RM_WINDOW_TITLE'] = 'RM,TOTVS RM'
        >>> config = get_ui_config()
        >>> print(config.default_timeout)
        60
        >>> print(config.window_title)
        ['RM', 'TOTVS RM']
    
    Note:
        As variáveis de ambiente têm precedência sobre os valores padrão.
        Para RM_WINDOW_TITLE, use vírgulas para separar múltiplos títulos.
    """
    config = UIConfig()

    # Aplicar overrides com variáveis de ambiente
    config.default_timeout = int(os.getenv("UI_DEFAULT_TIMEOUT", config.default_timeout))

    # Overrides específicos do sistema RM
    config.rm_executable_path = os.getenv("RM_EXECUTABLE_PATH", config.rm_executable_path)
    config.start_wait_time = int(os.getenv("RM_START_WAIT_TIME", config.start_wait_time))
    config.totvs_window_pattern = os.getenv("RM_TOTVS_WINDOW_PATTERN", config.totvs_window_pattern)
    config.application_ready_timeout = int(os.getenv("RM_APP_READY_TIMEOUT", config.application_ready_timeout))

    # Processar títulos de janela (string CSV para lista)
    window_titles_str = os.getenv("RM_WINDOW_TITLE")
    if window_titles_str:
        config.window_title = [title.strip() for title in window_titles_str.split(",")]

    config.process_name = os.getenv("RM_PROCESS_NAME", config.process_name)
    config.screenshot_on_error = os.getenv("UI_SCREENSHOT_ON_ERROR", "true").lower() == "true"
    config.log_level = os.getenv("UI_LOG_LEVEL", config.log_level)

    return config
