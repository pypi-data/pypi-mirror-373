"""
Monitor de progresso para aplicação RM.

Fornece funcionalidades para monitoramento de timers e progresso de processos
na aplicação RM, com conversão automática para milissegundos e detecção de estabilização.
"""

import logging
import re
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UITimeoutError
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


def time_string_to_milliseconds(time_str: str) -> int:
    """
    Converte string de tempo HH:MM:SS para milissegundos.
    
    Args:
        time_str: String no formato "HH:MM:SS".
        
    Returns:
        int: Tempo em milissegundos.
        
    Raises:
        ValueError: Se formato for inválido.
    """
    try:
        parts = time_str.split(':')
        if len(parts) != 3:
            raise ValueError(f"Formato inválido: {time_str}")
        
        hours, minutes, seconds = map(int, parts)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds * 1000
        
    except Exception as e:
        raise ValueError(f"Erro ao converter tempo '{time_str}': {e}")


class RMProgressMonitor:
    """
    Monitor de progresso para aplicação RM.
    
    Monitora timers de progresso na interface RM, detectando quando processos
    são finalizados através da estabilização do texto do timer.
    """
    
    def __init__(self, parent_element: HwndWrapper, timer_auto_id: str, check_interval: float = 5.0):
        """
        Inicializa o monitor de progresso.
        
        Args:
            parent_element: Elemento pai que contém o timer.
            timer_auto_id: AutoID do elemento timer.
            check_interval: Intervalo entre verificações em segundos.
            
        Raises:
            ValueError: Se parâmetros forem inválidos.
        """
        if parent_element is None:
            raise ValueError("Parâmetro 'parent_element' não pode ser None")
        if not timer_auto_id:
            raise ValueError("Parâmetro 'timer_auto_id' não pode ser vazio")
        if check_interval <= 0:
            raise ValueError("Parâmetro 'check_interval' deve ser positivo")
            
        self.parent_element = parent_element
        self.timer_auto_id = timer_auto_id
        self.check_interval = check_interval
        self.config = get_ui_config()
        
        # Estado do monitoramento
        self.previous_text: Optional[str] = None
        self.start_time: Optional[float] = None
        self.iteration_count: int = 0
    
    def _get_timer_element_fresh(self) -> Optional[HwndWrapper]:
        """
        Re-captura o elemento timer para garantir dados atualizados.
        
        Returns:
            Optional[HwndWrapper]: Elemento timer ou None se não encontrado.
            
        Raises:
            UIElementNotFoundError: Se elemento não for encontrado.
        """
        try:
            timer_element = self.parent_element.child_window(   # type: ignore[attr-defined]
                auto_id=self.timer_auto_id, 
                control_type="Text"
            )
            return timer_element
            
        except ElementNotFoundError as e:
            logger.warning(f"Elemento timer não encontrado: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao capturar elemento timer: {e}")
            return None
    
    def _get_current_timer_text(self) -> Optional[str]:
        """
        Obtém texto atual do timer re-capturando o elemento.
        
        Returns:
            Optional[str]: Texto do timer ou None se não conseguir ler.
        """
        timer_element = self._get_timer_element_fresh()
        if timer_element:
            try:
                return timer_element.window_text()
            except Exception as e:
                logger.warning(f"Erro ao ler texto do timer: {e}")
                return None
        return None
    
    def _extract_time_from_text(self, text: str) -> Optional[str]:
        """
        Extrai tempo do formato 'Tempo Total Decorrido = 00:02:21'.
        
        Args:
            text: Texto completo do timer.
            
        Returns:
            Optional[str]: Tempo no formato HH:MM:SS ou None se não encontrado.
        """
        try:
            match = re.search(r'(\d{2}:\d{2}:\d{2})', text)
            return match.group(1) if match else None
        except Exception as e:
            logger.warning(f"Erro ao extrair tempo do texto '{text}': {e}")
            return None
    
    def _time_to_milliseconds(self, time_str: str) -> int:
        """
        Converte tempo HH:MM:SS para milissegundos.
        
        Args:
            time_str: String no formato HH:MM:SS.
            
        Returns:
            int: Tempo em milissegundos.
        """
        return time_string_to_milliseconds(time_str)
    
    def monitor_until_stable(
        self, 
        max_timeout: Optional[float] = None, 
        max_failures: int = 3
    ) -> Dict[str, Any]:
        """
        Monitora timer até o texto estabilizar e retorna resultado completo.
        
        Executa monitoramento contínuo do timer, detectando quando o processo
        é finalizado através da estabilização do texto (sem mudanças).
        
        Args:
            max_timeout: Timeout máximo em segundos. Se None, sem limite.
            max_failures: Máximo de falhas consecutivas antes de desistir.
        
        Returns:
            Dict[str, Any]: Resultado do monitoramento com as seguintes chaves:
                - success (bool): Se monitoramento foi bem-sucedido
                - final_time_milliseconds (int): Tempo final em ms
                - final_time_string (str): Tempo final como string
                - iterations (int): Número de iterações realizadas
                - error (str): Mensagem de erro se success=False
                
        Raises:
            UITimeoutError: Se timeout for atingido.
            UIElementNotFoundError: Se elemento não for encontrado.
        """
        try:
            return self._execute_monitoring(max_timeout, max_failures)
        except Exception as e:
            error_msg = f"Erro durante monitoramento: {e}"
            logger.error(error_msg)
            capture_screenshot_on_error("rm_progress_monitor_failed")
            return {"success": False, "error": error_msg}
    
    def _execute_monitoring(self, max_timeout: Optional[float], max_failures: int) -> Dict[str, Any]:
        """
        Executa o loop principal de monitoramento.
        
        Args:
            max_timeout: Timeout máximo em segundos.
            max_failures: Máximo de falhas consecutivas.
            
        Returns:
            Dict[str, Any]: Resultado do monitoramento.
        """
        
        self.start_time = time.time()
        logger.info("Iniciando monitoramento do timer RM")
        
        # Leitura inicial
        initial_text = self._get_current_timer_text()
        if initial_text is None:
            raise UIElementNotFoundError("Falha ao ler texto inicial do timer")
        
        self.previous_text = self._extract_time_from_text(initial_text)
        if self.previous_text is None:
            raise UIElementNotFoundError("Não foi possível extrair tempo do texto inicial")
            
        initial_ms = self._time_to_milliseconds(self.previous_text)
        logger.info(f"Tempo inicial: {self.previous_text} ({initial_ms:,} ms)")
        
        consecutive_failures = 0
        
        # Loop de monitoramento
        while True:
            self.iteration_count += 1
            
            # Aguarda intervalo
            logger.debug(f"Verificação #{self.iteration_count} - Aguardando {self.check_interval}s")
            time.sleep(self.check_interval)
            
            # RE-CAPTURA o elemento e lê texto atual
            current_full_text = self._get_current_timer_text()
            
            if current_full_text is None:
                consecutive_failures += 1
                logger.warning(f"Falha na leitura #{consecutive_failures}")
                
                if consecutive_failures >= max_failures:
                    raise UIElementNotFoundError(
                        f"Muitas falhas consecutivas na leitura do timer ({consecutive_failures})"
                    )
                continue
            
            # Reset contador de falhas
            consecutive_failures = 0
            
            current_text = self._extract_time_from_text(current_full_text)
            current_ms = self._time_to_milliseconds(current_text) if current_text else 0
            
            logger.debug(f"Tempo atual: {current_text} ({current_ms:,} ms)")
            
            # Verifica se mudou
            if current_text == self.previous_text:
                # Texto estabilizou!
                elapsed_time = time.time() - self.start_time
                
                logger.info("✅ PROCESSO FINALIZADO - Texto estabilizou!")
                logger.info(f"⏱️ Tempo final: {current_text} = {current_ms:,} milissegundos")
                
                return {
                    "success": True,
                    "final_text": current_full_text,
                    "final_time_string": current_text,
                    "final_time_milliseconds": current_ms,
                    "initial_time_milliseconds": initial_ms,
                    "time_difference_ms": current_ms - initial_ms,
                    "iterations": self.iteration_count,
                    "monitoring_elapsed": round(elapsed_time, 2),
                    "monitoring_duration": f"{int(elapsed_time//60)}m {int(elapsed_time%60)}s"
                }
            
            else:
                # Texto mudou
                prev_ms = self._time_to_milliseconds(self.previous_text) if self.previous_text else 0
                diff_ms = current_ms - prev_ms
                
                logger.info(f"🔄 Mudança detectada:")
                logger.info(f"   De: {self.previous_text} ({prev_ms:,} ms)")
                logger.info(f"   Para: {current_text} ({current_ms:,} ms)")
                logger.info(f"   Diferença: +{diff_ms:,} ms")
                
                self.previous_text = current_text
            
            # Verifica timeout
            if max_timeout:
                elapsed = time.time() - self.start_time
                if elapsed > max_timeout:
                    logger.warning(f"⏰ Timeout atingido ({max_timeout}s)")
                    raise UITimeoutError(
                        f"Timeout de {max_timeout}s atingido durante monitoramento"
                    )