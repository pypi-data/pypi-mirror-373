"""
Configurações para operações de UI.

Centraliza todas as configurações relacionadas à automação de UI,
permitindo fácil customização e manutenção.
"""

from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class UIConfig:
    """Configurações para automação de UI."""

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
    totvs_window_pattern: str = ".*TOTVS.*"
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
    Retorna a configuração de UI, permitindo override via variáveis de ambiente.

    Variáveis suportadas:
    - UI_DEFAULT_TIMEOUT
    - RM_WINDOW_TITLE (separado por vírgula)
    - RM_PROCESS_NAME
    - UI_SCREENSHOT_ON_ERROR
    - UI_LOG_LEVEL

    Returns:
        UIConfig: Configuração de UI carregada.
    """
    config = UIConfig()

    # Override com variáveis de ambiente
    config.default_timeout = int(os.getenv("UI_DEFAULT_TIMEOUT", config.default_timeout))

    # Overrides executavel RM
    config.rm_executable_path = os.getenv("RM_EXECUTABLE_PATH", config.rm_executable_path)
    config.start_wait_time = int(os.getenv("RM_START_WAIT_TIME", config.start_wait_time))
    config.totvs_window_pattern = os.getenv("RM_TOTVS_WINDOW_PATTERN", config.totvs_window_pattern)
    config.application_ready_timeout = int(os.getenv("RM_APP_READY_TIMEOUT", config.application_ready_timeout))

    # Converte string separada por vírgulas em lista de títulos
    window_titles_str = os.getenv("RM_WINDOW_TITLE")
    if window_titles_str:
        config.window_title = [title.strip() for title in window_titles_str.split(",")]

    config.process_name = os.getenv("RM_PROCESS_NAME", config.process_name)
    config.screenshot_on_error = os.getenv("UI_SCREENSHOT_ON_ERROR", "true").lower() == "true"
    config.log_level = os.getenv("UI_LOG_LEVEL", config.log_level)

    return config
