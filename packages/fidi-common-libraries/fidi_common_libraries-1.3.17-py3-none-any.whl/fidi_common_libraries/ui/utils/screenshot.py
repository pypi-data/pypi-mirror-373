"""
Utilitários para captura de screenshots.

Fornece funcionalidades para capturar screenshots em caso de erro
ou para documentação, auxiliando na depuração e análise.
"""

import logging
import os
from datetime import datetime
from typing import Optional
from PIL import ImageGrab

from ..config.ui_config import get_ui_config


logger = logging.getLogger(__name__)


def capture_screenshot_on_error(
    error_context: str,
    custom_filename: Optional[str] = None
) -> Optional[str]:
    """
    Captura screenshot em caso de erro.
    
    Args:
        error_context: Contexto do erro para nomear o arquivo.
        custom_filename: Nome customizado para o arquivo.
        
    Returns:
        Optional[str]: Caminho do arquivo salvo ou None se falhar.
    """
    config = get_ui_config()
    
    if not config.screenshot_on_error:
        return None
    
    try:
        # Cria diretório se não existir
        os.makedirs(config.screenshot_dir, exist_ok=True)
        
        # Gera nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_filename:
            filename = f"{custom_filename}_{timestamp}.png"
        else:
            filename = f"error_{error_context}_{timestamp}.png"
        
        filepath = os.path.join(config.screenshot_dir, filename)
        
        # Captura screenshot
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        
        logger.info(f"Screenshot capturado: {filepath}")
        return filepath
        
    except Exception as e:
        logger.warning(f"Falha ao capturar screenshot: {e}")
        return None


def capture_screenshot(
    filename: Optional[str] = None,
    directory: Optional[str] = None
) -> Optional[str]:
    """
    Captura screenshot manual.
    
    Args:
        filename: Nome do arquivo (sem extensão).
        directory: Diretório para salvar.
        
    Returns:
        Optional[str]: Caminho do arquivo salvo ou None se falhar.
    """
    config = get_ui_config()
    
    try:
        # Define diretório
        save_dir = directory or config.screenshot_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # Gera nome do arquivo
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}"
        
        filepath = os.path.join(save_dir, f"{filename}.png")
        
        # Captura screenshot
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        
        logger.info(f"Screenshot salvo: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Erro ao capturar screenshot: {e}")
        return None