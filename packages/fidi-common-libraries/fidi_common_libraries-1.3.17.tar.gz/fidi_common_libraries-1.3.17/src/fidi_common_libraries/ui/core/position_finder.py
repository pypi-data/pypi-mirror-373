"""
Utilitários para localização de elementos por posição na tela.

Fornece funcionalidades para encontrar elementos baseado em coordenadas,
regiões da tela, posição relativa e reconhecimento visual.
"""

import logging
import time
from typing import Tuple, Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from PIL import Image, ImageGrab
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto import mouse, keyboard
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UIInteractionError
from .waits import UIWaits
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


class PositionReference(Enum):
    """
    Referências para posicionamento de elementos.
    
    Attributes:
        ABSOLUTE: Coordenadas absolutas da tela.
        RELATIVE_TO_WINDOW: Coordenadas relativas à janela.
        RELATIVE_TO_ELEMENT: Coordenadas relativas a outro elemento.
    """
    ABSOLUTE = "absolute"
    RELATIVE_TO_WINDOW = "relative_to_window"
    RELATIVE_TO_ELEMENT = "relative_to_element"


@dataclass
class ScreenRegion:
    """
    Define uma região retangular da tela.
    
    Attributes:
        x: Coordenada X do canto superior esquerdo.
        y: Coordenada Y do canto superior esquerdo.
        width: Largura da região em pixels.
        height: Altura da região em pixels.
    """
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> Tuple[int, int]:
        """Retorna o centro da região."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """Retorna os limites da região (x1, y1, x2, y2)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


@dataclass
class PositionCriteria:
    """
    Critérios para localização de elementos por posição.
    
    Attributes:
        x: Coordenada X.
        y: Coordenada Y.
        reference: Tipo de referência para as coordenadas.
        tolerance: Tolerância em pixels para a busca.
        reference_element: Elemento de referência (se aplicável).
        region: Região específica para buscar.
        description: Descrição dos critérios.
    """
    x: int
    y: int
    reference: PositionReference = PositionReference.ABSOLUTE
    tolerance: int = 5
    reference_element: Optional[HwndWrapper] = None
    region: Optional[ScreenRegion] = None
    description: str = ""


class PositionFinder:
    """
    Localizador de elementos por posição na tela.
    
    Fornece métodos para encontrar elementos usando coordenadas,
    regiões da tela e posicionamento relativo.
    """
    
    def __init__(self):
        """
        Inicializa o localizador de posições.
        
        Configura os componentes necessários para localização de elementos
        por coordenadas e regiões da tela.
        """
        self.config = get_ui_config()
        self.waits = UIWaits()
        self._last_screenshot = None
        self._last_screenshot_time = 0
    
    def find_element_at_position(
        self,
        x: int,
        y: int,
        reference: PositionReference = PositionReference.ABSOLUTE,
        reference_element: Optional[HwndWrapper] = None,
        tolerance: int = 5
    ) -> Optional[HwndWrapper]:
        """
        Encontra elemento em uma posição específica.
        
        Args:
            x: Coordenada X.
            y: Coordenada Y.
            reference: Tipo de referência para as coordenadas.
            reference_element: Elemento de referência (se aplicável).
            tolerance: Tolerância em pixels para a busca.
            
        Returns:
            Optional[HwndWrapper]: Elemento encontrado ou None.
        """
        try:
            # Converte coordenadas se necessário
            abs_x, abs_y = self._convert_to_absolute_coords(
                x, y, reference, reference_element
            )
            
            logger.debug(f"Buscando elemento na posição ({abs_x}, {abs_y})")
            
            # Busca elemento na posição
            element = self._find_element_at_absolute_position(abs_x, abs_y, tolerance)
            
            if element:
                logger.info(f"Elemento encontrado na posição ({abs_x}, {abs_y})")
                return element
            else:
                logger.warning(f"Nenhum elemento encontrado na posição ({abs_x}, {abs_y})")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar elemento por posição: {e}")
            return None
    
    def _convert_to_absolute_coords(
        self,
        x: int,
        y: int,
        reference: PositionReference,
        reference_element: Optional[HwndWrapper] = None
    ) -> Tuple[int, int]:
        """
        Converte coordenadas relativas para coordenadas absolutas da tela.
        
        Args:
            x: Coordenada X.
            y: Coordenada Y.
            reference: Tipo de referência das coordenadas.
            reference_element: Elemento de referência (se necessário).
            
        Returns:
            Tuple[int, int]: Coordenadas absolutas (x, y).
            
        Raises:
            ValueError: Se parâmetros obrigatórios estiverem ausentes.
        """
        
        if reference == PositionReference.ABSOLUTE:
            return x, y
        
        elif reference == PositionReference.RELATIVE_TO_WINDOW:
            if not reference_element:
                raise ValueError("reference_element é obrigatório para RELATIVE_TO_WINDOW")
            
            rect = reference_element.rectangle()
            return rect.left + x, rect.top + y
        
        elif reference == PositionReference.RELATIVE_TO_ELEMENT:
            if not reference_element:
                raise ValueError("reference_element é obrigatório para RELATIVE_TO_ELEMENT")
            
            rect = reference_element.rectangle()
            center_x = rect.left + rect.width() // 2
            center_y = rect.top + rect.height() // 2
            return center_x + x, center_y + y
        
        else:
            raise ValueError(f"Referência inválida: {reference}")
    
    def _find_element_at_absolute_position(
        self,
        x: int,
        y: int,
        tolerance: int
    ) -> Optional[HwndWrapper]:
        """
        Encontra elemento em posição absoluta da tela.
        
        Realiza busca em uma região ao redor da posição especificada,
        considerando a tolerância definida.
        
        Args:
            x: Coordenada X absoluta.
            y: Coordenada Y absoluta.
            tolerance: Tolerância em pixels para a busca.
            
        Returns:
            Optional[HwndWrapper]: Elemento encontrado ou None.
        """
        try:
            from pywinauto import Desktop
            
            # Busca em uma região ao redor da posição
            for offset_x in range(-tolerance, tolerance + 1):
                for offset_y in range(-tolerance, tolerance + 1):
                    try:
                        test_x = x + offset_x
                        test_y = y + offset_y
                        
                        # Tenta encontrar elemento na posição
                        element = Desktop().from_point(test_x, test_y)
                        if element and element.exists():
                            return element
                    except:
                        continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Erro ao buscar elemento em posição absoluta: {e}")
            return None
    
    def find_elements_in_region(
        self,
        region: ScreenRegion,
        element_filter: Optional[Dict[str, Any]] = None
    ) -> List[HwndWrapper]:
        """
        Encontra todos os elementos em uma região da tela.
        
        Args:
            region: Região da tela para buscar.
            element_filter: Filtros opcionais para os elementos.
            
        Returns:
            List[HwndWrapper]: Lista de elementos encontrados.
        """
        try:
            from pywinauto import Desktop
            
            elements = []
            step = 10  # Passo para varredura da região
            
            logger.debug(f"Buscando elementos na região: {region.bounds}")
            
            for x in range(region.x, region.x + region.width, step):
                for y in range(region.y, region.y + region.height, step):
                    try:
                        element = Desktop().from_point(x, y)
                        if element and element.exists():
                            # Verifica se já foi adicionado
                            if not any(e.handle == element.handle for e in elements):
                                # Aplica filtros se especificados
                                if self._matches_filter(element, element_filter):
                                    elements.append(element)
                    except:
                        continue
            
            logger.info(f"Encontrados {len(elements)} elementos na região")
            return elements
            
        except Exception as e:
            logger.error(f"Erro ao buscar elementos na região: {e}")
            return []
    
    def _matches_filter(
        self,
        element: HwndWrapper,
        element_filter: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Verifica se um elemento corresponde aos filtros especificados.
        
        Args:
            element: Elemento a ser verificado.
            element_filter: Dicionário com critérios de filtragem.
            
        Returns:
            bool: True se o elemento corresponde aos filtros.
        """
        if not element_filter:
            return True
        
        try:
            for key, value in element_filter.items():
                if key == "class_name":
                    if element.class_name() != value:
                        return False
                elif key == "control_type":
                    if element.control_type() != value:
                        return False
                elif key == "title":
                    if element.window_text() != value:
                        return False
                # Adicione mais filtros conforme necessário
            
            return True
            
        except:
            return False
    
    def click_at_position(
        self,
        x: int,
        y: int,
        reference: PositionReference = PositionReference.ABSOLUTE,
        reference_element: Optional[HwndWrapper] = None,
        button: str = "left",
        double_click: bool = False
    ) -> None:
        """
        Clica em uma posição específica da tela.
        
        Args:
            x: Coordenada X.
            y: Coordenada Y.
            reference: Tipo de referência para as coordenadas.
            reference_element: Elemento de referência (se aplicável).
            button: Botão do mouse ("left", "right", "middle").
            double_click: Se deve fazer duplo clique.
            
        Raises:
            UIInteractionError: Se o clique falhar.
        """
        try:
            # Converte coordenadas
            abs_x, abs_y = self._convert_to_absolute_coords(
                x, y, reference, reference_element
            )
            
            logger.debug(f"Clicando na posição ({abs_x}, {abs_y})")
            
            # Executa o clique
            if double_click:
                mouse.double_click(coords=(abs_x, abs_y), button=button)
            else:
                mouse.click(coords=(abs_x, abs_y), button=button)
            
            logger.info(f"Clique realizado na posição ({abs_x}, {abs_y})")
            
        except Exception as e:
            error_msg = f"Erro ao clicar na posição ({x}, {y})"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("position_click_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def get_element_center_position(
        self,
        element: HwndWrapper,
        reference: PositionReference = PositionReference.ABSOLUTE
    ) -> Tuple[int, int]:
        """
        Obtém a posição central de um elemento.
        
        Args:
            element: Elemento para obter a posição.
            reference: Tipo de referência para retorno.
            
        Returns:
            Tuple[int, int]: Coordenadas (x, y) do centro do elemento.
        """
        try:
            rect = element.rectangle()
            center_x = rect.left + rect.width() // 2
            center_y = rect.top + rect.height() // 2
            
            if reference == PositionReference.ABSOLUTE:
                return center_x, center_y
            else:
                # Para outras referências, retorna relativo à tela por enquanto
                # Pode ser expandido conforme necessário
                return center_x, center_y
                
        except Exception as e:
            logger.error(f"Erro ao obter posição do elemento: {e}")
            raise UIInteractionError("Erro ao obter posição do elemento", str(e))
    
    def wait_for_element_at_position(
        self,
        x: int,
        y: int,
        reference: PositionReference = PositionReference.ABSOLUTE,
        reference_element: Optional[HwndWrapper] = None,
        timeout: Optional[int] = None,
        tolerance: int = 5
    ) -> HwndWrapper:
        """
        Aguarda um elemento aparecer em uma posição específica.
        
        Args:
            x: Coordenada X.
            y: Coordenada Y.
            reference: Tipo de referência para as coordenadas.
            reference_element: Elemento de referência (se aplicável).
            timeout: Timeout em segundos.
            tolerance: Tolerância em pixels.
            
        Returns:
            HwndWrapper: Elemento encontrado.
            
        Raises:
            UIElementNotFoundError: Se o elemento não aparecer no tempo esperado.
        """
        timeout = timeout or self.config.default_timeout
        
        def element_at_position_exists():
            """Verifica se existe elemento na posição especificada."""
            element = self.find_element_at_position(
                x, y, reference, reference_element, tolerance
            )
            return element is not None
        
        logger.debug(f"Aguardando elemento na posição ({x}, {y})")
        
        if self.waits.wait_for_condition(
            element_at_position_exists,
            timeout,
            condition_description=f"elemento na posição ({x}, {y})"
        ):
            return self.find_element_at_position(
                x, y, reference, reference_element, tolerance
            )
    
    def capture_region_screenshot(
        self,
        region: ScreenRegion,
        save_path: Optional[str] = None
    ) -> Image.Image:
        """
        Captura screenshot de uma região específica.
        
        Args:
            region: Região para capturar.
            save_path: Caminho para salvar (opcional).
            
        Returns:
            Image.Image: Imagem capturada.
        """
        try:
            # Captura a região específica
            screenshot = ImageGrab.grab(bbox=region.bounds)
            
            if save_path:
                screenshot.save(save_path)
                logger.info(f"Screenshot da região salvo em: {save_path}")
            
            return screenshot
            
        except Exception as e:
            logger.error(f"Erro ao capturar screenshot da região: {e}")
            raise UIInteractionError("Erro ao capturar screenshot", str(e))
    
    def get_screen_region_from_element(
        self,
        element: HwndWrapper,
        expand_by: int = 0
    ) -> ScreenRegion:
        """
        Cria uma região da tela baseada em um elemento.
        
        Args:
            element: Elemento de referência.
            expand_by: Pixels para expandir a região.
            
        Returns:
            ScreenRegion: Região criada.
        """
        try:
            rect = element.rectangle()
            
            return ScreenRegion(
                x=rect.left - expand_by,
                y=rect.top - expand_by,
                width=rect.width() + (2 * expand_by),
                height=rect.height() + (2 * expand_by)
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar região do elemento: {e}")
            raise UIInteractionError("Erro ao criar região", str(e))