"""
Utilitários para localização de elementos por reconhecimento de imagem.

Fornece funcionalidades para encontrar elementos na tela usando
template matching e reconhecimento visual.
"""

import logging
import os
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image, ImageGrab

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError, UIInteractionError
from .position_finder import ScreenRegion, PositionFinder
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


@dataclass
class ImageMatchResult:
    """
    Resultado de uma busca por imagem.
    
    Attributes:
        found: Se a imagem foi encontrada.
        confidence: Nível de confiança do match (0.0 a 1.0).
        position: Posição (x, y) onde a imagem foi encontrada.
        region: Região da tela onde a imagem foi localizada.
        template_path: Caminho do arquivo template usado na busca.
    """
    found: bool
    confidence: float
    position: Tuple[int, int]
    region: ScreenRegion
    template_path: str


class ImageFinder:
    """
    Localizador de elementos por reconhecimento de imagem.
    
    Utiliza template matching para encontrar elementos na tela
    baseado em imagens de referência.
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Inicializa o localizador de imagens.
        
        Args:
            templates_dir: Diretório onde os templates serão armazenados.
        """
        self.config = get_ui_config()
        self.position_finder = PositionFinder()
        self.templates_dir = templates_dir
        
        # Cria diretório de templates se não existir
        os.makedirs(templates_dir, exist_ok=True)
    
    def find_element_by_image(
        self,
        template_path: str,
        confidence_threshold: float = 0.8,
        search_region: Optional[ScreenRegion] = None,
        method: int = cv2.TM_CCOEFF_NORMED
    ) -> ImageMatchResult:
        """
        Encontra elemento na tela usando template matching.
        
        Args:
            template_path: Caminho para a imagem template.
            confidence_threshold: Limite mínimo de confiança (0.0 a 1.0).
            search_region: Região específica para buscar (None = tela toda).
            method: Método de template matching do OpenCV.
            
        Returns:
            ImageMatchResult: Resultado da busca.
            
        Raises:
            UIElementNotFoundError: Se o template não for encontrado.
        """
        try:
            # Carrega o template
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template não encontrado: {template_path}")
            
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError(f"Não foi possível carregar o template: {template_path}")
            
            # Captura screenshot da região de busca
            if search_region:
                screenshot = self.position_finder.capture_region_screenshot(search_region)
                offset_x, offset_y = search_region.x, search_region.y
            else:
                screenshot = ImageGrab.grab()
                offset_x, offset_y = 0, 0
            
            # Converte para OpenCV
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Executa template matching
            result = cv2.matchTemplate(screenshot_cv, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Determina a posição baseada no método
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                confidence = 1 - min_val
                match_loc = min_loc
            else:
                confidence = max_val
                match_loc = max_loc
            
            # Calcula posição absoluta
            abs_x = match_loc[0] + offset_x
            abs_y = match_loc[1] + offset_y
            
            # Cria região do match
            template_h, template_w = template.shape[:2]
            match_region = ScreenRegion(abs_x, abs_y, template_w, template_h)
            
            found = confidence >= confidence_threshold
            
            result = ImageMatchResult(
                found=found,
                confidence=confidence,
                position=(abs_x, abs_y),
                region=match_region,
                template_path=template_path
            )
            
            if found:
                logger.info(f"Template encontrado: {template_path} "
                           f"(confiança: {confidence:.3f}, posição: {abs_x}, {abs_y})")
            else:
                logger.warning(f"Template não encontrado: {template_path} "
                              f"(confiança: {confidence:.3f} < {confidence_threshold})")
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao buscar template {template_path}"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("image_search_failed")
            raise UIElementNotFoundError(error_msg, str(e))
    
    def find_all_matches(
        self,
        template_path: str,
        confidence_threshold: float = 0.8,
        search_region: Optional[ScreenRegion] = None,
        method: int = cv2.TM_CCOEFF_NORMED
    ) -> List[ImageMatchResult]:
        """
        Encontra todas as ocorrências de um template na tela.
        
        Args:
            template_path: Caminho para a imagem template.
            confidence_threshold: Limite mínimo de confiança.
            search_region: Região específica para buscar.
            method: Método de template matching.
            
        Returns:
            List[ImageMatchResult]: Lista com todos os matches encontrados.
        """
        try:
            # Carrega template
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                raise ValueError(f"Não foi possível carregar o template: {template_path}")
            
            # Captura screenshot
            if search_region:
                screenshot = self.position_finder.capture_region_screenshot(search_region)
                offset_x, offset_y = search_region.x, search_region.y
            else:
                screenshot = ImageGrab.grab()
                offset_x, offset_y = 0, 0
            
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Template matching
            result = cv2.matchTemplate(screenshot_cv, template, method)
            
            # Encontra todas as posições acima do threshold
            locations = np.where(result >= confidence_threshold)
            matches = []
            
            template_h, template_w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):  # Switch x and y
                abs_x = pt[0] + offset_x
                abs_y = pt[1] + offset_y
                confidence = result[pt[1], pt[0]]
                
                match_region = ScreenRegion(abs_x, abs_y, template_w, template_h)
                
                match_result = ImageMatchResult(
                    found=True,
                    confidence=float(confidence),
                    position=(abs_x, abs_y),
                    region=match_region,
                    template_path=template_path
                )
                
                matches.append(match_result)
            
            logger.info(f"Encontrados {len(matches)} matches para {template_path}")
            return matches
            
        except Exception as e:
            logger.error(f"Erro ao buscar múltiplos matches: {e}")
            return []
    
    def click_on_image(
        self,
        template_path: str,
        confidence_threshold: float = 0.8,
        search_region: Optional[ScreenRegion] = None,
        click_offset: Tuple[int, int] = (0, 0),
        double_click: bool = False
    ) -> bool:
        """
        Clica em uma imagem encontrada na tela.
        
        Args:
            template_path: Caminho para a imagem template.
            confidence_threshold: Limite mínimo de confiança.
            search_region: Região específica para buscar.
            click_offset: Offset do clique em relação ao centro da imagem.
            double_click: Se deve fazer duplo clique.
            
        Returns:
            bool: True se clicou com sucesso, False caso contrário.
        """
        try:
            match_result = self.find_element_by_image(
                template_path, confidence_threshold, search_region
            )
            
            if not match_result.found:
                logger.warning(f"Imagem não encontrada para clique: {template_path}")
                return False
            
            # Calcula posição do clique (centro da imagem + offset)
            center_x = match_result.region.center[0] + click_offset[0]
            center_y = match_result.region.center[1] + click_offset[1]
            
            # Executa o clique
            self.position_finder.click_at_position(
                center_x, center_y, double_click=double_click
            )
            
            logger.info(f"Clique realizado na imagem: {template_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao clicar na imagem {template_path}: {e}")
            return False
    
    def wait_for_image(
        self,
        template_path: str,
        confidence_threshold: float = 0.8,
        timeout: Optional[int] = None,
        search_region: Optional[ScreenRegion] = None,
        check_interval: float = 1.0
    ) -> ImageMatchResult:
        """
        Aguarda uma imagem aparecer na tela.
        
        Args:
            template_path: Caminho para a imagem template.
            confidence_threshold: Limite mínimo de confiança.
            timeout: Timeout em segundos.
            search_region: Região específica para buscar.
            check_interval: Intervalo entre verificações.
            
        Returns:
            ImageMatchResult: Resultado quando a imagem for encontrada.
            
        Raises:
            UIElementNotFoundError: Se a imagem não aparecer no tempo esperado.
        """
        timeout = timeout or self.config.default_timeout
        
        def image_exists():
            """Verifica se a imagem existe na tela."""
            try:
                result = self.find_element_by_image(
                    template_path, confidence_threshold, search_region
                )
                return result.found
            except:
                return False
        
        logger.info(f"Aguardando imagem: {template_path}")
        
        from .waits import UIWaits
        waits = UIWaits()
        
        if waits.wait_for_condition(
            image_exists,
            timeout,
            check_interval,
            f"imagem {os.path.basename(template_path)}"
        ):
            return self.find_element_by_image(
                template_path, confidence_threshold, search_region
            )
    
    def save_template_from_region(
        self,
        region: ScreenRegion,
        template_name: str,
        description: str = ""
    ) -> str:
        """
        Salva uma região da tela como template.
        
        Args:
            region: Região da tela para capturar.
            template_name: Nome do arquivo template.
            description: Descrição do template.
            
        Returns:
            str: Caminho do arquivo salvo.
        """
        try:
            # Garante extensão .png
            if not template_name.endswith('.png'):
                template_name += '.png'
            
            template_path = os.path.join(self.templates_dir, template_name)
            
            # Captura a região
            screenshot = self.position_finder.capture_region_screenshot(
                region, template_path
            )
            
            # Salva metadados se fornecidos
            if description:
                metadata_path = template_path.replace('.png', '_metadata.txt')
                import time
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    f.write(f"Template: {template_name}\n")
                    f.write(f"Descrição: {description}\n")
                    f.write(f"Região: {region.bounds}\n")
                    f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Template salvo: {template_path}")
            return template_path
            
        except Exception as e:
            logger.error(f"Erro ao salvar template: {e}")
            raise UIInteractionError("Erro ao salvar template", str(e))
    
    def create_template_from_element(
        self,
        element,
        template_name: str,
        expand_by: int = 5,
        description: str = ""
    ) -> str:
        """
        Cria um template a partir de um elemento.
        
        Args:
            element: Elemento para capturar.
            template_name: Nome do template.
            expand_by: Pixels para expandir a captura.
            description: Descrição do template.
            
        Returns:
            str: Caminho do template criado.
        """
        try:
            # Obtém região do elemento
            region = self.position_finder.get_screen_region_from_element(
                element, expand_by
            )
            
            # Salva como template
            return self.save_template_from_region(
                region, template_name, description
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar template do elemento: {e}")
            raise UIInteractionError("Erro ao criar template", str(e))