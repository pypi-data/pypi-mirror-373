"""
Utilitários para localização de elementos por posição na tela.

Este módulo fornece funcionalidades avançadas para localização de elementos
de interface gráfica baseado em coordenadas absolutas e relativas, regiões
da tela e reconhecimento visual. É especialmente útil para automação de
interfaces que não possuem identificadores únicos ou quando é necessário
interagir com elementos baseado em sua posição visual.

O módulo suporta diferentes tipos de referência de coordenadas:
- Coordenadas absolutas da tela
- Coordenadas relativas a janelas
- Coordenadas relativas a outros elementos

Também oferece funcionalidades para:
- Busca de elementos em regiões específicas
- Captura de screenshots de regiões
- Cliques em posições específicas
- Aguardar elementos aparecerem em posições

Example:
    Uso básico do localizador de posições:
    
    >>> finder = PositionFinder()
    >>> element = finder.find_element_at_position(100, 200)
    >>> if element:
    ...     finder.click_at_position(100, 200)
    
    Busca em região específica:
    
    >>> region = ScreenRegion(x=50, y=50, width=200, height=100)
    >>> elements = finder.find_elements_in_region(region)
    >>> print(f"Encontrados {len(elements)} elementos")

Note:
    Este módulo requer o pywinauto e PIL para funcionar corretamente.
    É recomendado usar em conjunto com outros módulos de UI para
    máxima eficiência.
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
    Enumeração de tipos de referência para posicionamento de elementos.
    
    Define os diferentes sistemas de coordenadas que podem ser utilizados
    para especificar posições de elementos na tela.
    
    Attributes:
        ABSOLUTE: Coordenadas absolutas da tela (0,0 = canto superior esquerdo).
        RELATIVE_TO_WINDOW: Coordenadas relativas ao canto superior esquerdo da janela.
        RELATIVE_TO_ELEMENT: Coordenadas relativas ao centro de outro elemento.
    
    Example:
        >>> ref = PositionReference.ABSOLUTE
        >>> finder.find_element_at_position(100, 200, reference=ref)
    """
    ABSOLUTE = "absolute"
    RELATIVE_TO_WINDOW = "relative_to_window"
    RELATIVE_TO_ELEMENT = "relative_to_element"


@dataclass
class ScreenRegion:
    """
    Define uma região retangular da tela para operações de busca e captura.
    
    Esta classe representa uma área retangular da tela definida por coordenadas
    e dimensões. É utilizada para delimitar áreas de busca de elementos,
    captura de screenshots e outras operações regionais.
    
    Attributes:
        x (int): Coordenada X do canto superior esquerdo da região.
        y (int): Coordenada Y do canto superior esquerdo da região.
        width (int): Largura da região em pixels.
        height (int): Altura da região em pixels.
    
    Example:
        Criar uma região e usar suas propriedades:
        
        >>> region = ScreenRegion(x=100, y=50, width=200, height=150)
        >>> center_x, center_y = region.center
        >>> bounds = region.bounds  # (100, 50, 300, 200)
    """
    x: int
    y: int
    width: int
    height: int
    
    @property
    def center(self) -> Tuple[int, int]:
        """
        Calcula e retorna as coordenadas do centro da região.
        
        Returns:
            Tuple[int, int]: Coordenadas (x, y) do centro da região.
        
        Example:
            >>> region = ScreenRegion(x=100, y=50, width=200, height=150)
            >>> center_x, center_y = region.center
            >>> print(f"Centro: ({center_x}, {center_y})")
            Centro: (200, 125)
        """
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        """
        Retorna os limites da região no formato (x1, y1, x2, y2).
        
        Returns:
            Tuple[int, int, int, int]: Coordenadas dos cantos superior esquerdo
                e inferior direito da região (x1, y1, x2, y2).
        
        Example:
            >>> region = ScreenRegion(x=100, y=50, width=200, height=150)
            >>> x1, y1, x2, y2 = region.bounds
            >>> print(f"Região: ({x1}, {y1}) até ({x2}, {y2})")
            Região: (100, 50) até (300, 200)
        """
        return (self.x, self.y, self.x + self.width, self.y + self.height)


@dataclass
class PositionCriteria:
    """
    Critérios completos para localização de elementos por posição.
    
    Esta classe encapsula todos os parâmetros necessários para realizar
    uma busca de elemento baseada em posição, incluindo coordenadas,
    tipo de referência, tolerância e filtros adicionais.
    
    Attributes:
        x (int): Coordenada X da posição de busca.
        y (int): Coordenada Y da posição de busca.
        reference (PositionReference): Tipo de referência para as coordenadas.
            Defaults to PositionReference.ABSOLUTE.
        tolerance (int): Tolerância em pixels para a busca. Defaults to 5.
        reference_element (Optional[HwndWrapper]): Elemento de referência
            para coordenadas relativas. Defaults to None.
        region (Optional[ScreenRegion]): Região específica para limitar a busca.
            Defaults to None.
        description (str): Descrição textual dos critérios. Defaults to "".
    
    Example:
        Criar critérios de busca:
        
        >>> criteria = PositionCriteria(
        ...     x=100, y=200,
        ...     reference=PositionReference.ABSOLUTE,
        ...     tolerance=10,
        ...     description="Botão OK"
        ... )
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
    Localizador avançado de elementos por posição na tela.
    
    Esta classe fornece um conjunto completo de métodos para localização
    de elementos de interface gráfica baseado em coordenadas, regiões da tela
    e posicionamento relativo. É especialmente útil para automação de
    aplicações que não possuem identificadores únicos ou quando é necessário
    interagir com elementos baseado em sua posição visual.
    
    A classe suporta diferentes estratégias de localização:
    - Busca por coordenadas absolutas
    - Busca por coordenadas relativas a janelas ou elementos
    - Busca em regiões específicas da tela
    - Aguardar elementos aparecerem em posições
    - Captura de screenshots de regiões
    
    Attributes:
        config: Configuração de UI carregada do sistema.
        waits: Instância de UIWaits para operações de espera.
    
    Example:
        Uso básico do localizador:
        
        >>> finder = PositionFinder()
        >>> element = finder.find_element_at_position(100, 200)
        >>> if element:
        ...     print(f"Elemento encontrado: {element.window_text()}")
        
        Busca com tolerância:
        
        >>> element = finder.find_element_at_position(
        ...     x=100, y=200, tolerance=15
        ... )
        
        Aguardar elemento aparecer:
        
        >>> element = finder.wait_for_element_at_position(
        ...     x=100, y=200, timeout=30
        ... )
    
    Note:
        Esta classe utiliza o pywinauto para interação com elementos
        e PIL para captura de screenshots. Certifique-se de que as
        dependências estão instaladas.
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
        Encontra elemento em uma posição específica da tela.
        
        Realiza busca de elemento UI em uma posição específica, com suporte
        a diferentes tipos de referência de coordenadas e tolerância para
        compensar pequenas variações de posição.
        
        Args:
            x (int): Coordenada X da posição de busca.
            y (int): Coordenada Y da posição de busca.
            reference (PositionReference, optional): Tipo de referência para
                as coordenadas. Defaults to PositionReference.ABSOLUTE.
            reference_element (Optional[HwndWrapper], optional): Elemento de
                referência para coordenadas relativas. Obrigatório para
                referências RELATIVE_TO_WINDOW e RELATIVE_TO_ELEMENT.
                Defaults to None.
            tolerance (int, optional): Tolerância em pixels para a busca.
                A busca será realizada em uma área de (2*tolerance+1)²
                pixels ao redor da posição especificada. Defaults to 5.
            
        Returns:
            Optional[HwndWrapper]: Elemento encontrado na posição ou None
                se nenhum elemento for encontrado.
        
        Example:
            Busca por coordenadas absolutas:
            
            >>> element = finder.find_element_at_position(100, 200)
            >>> if element:
            ...     print(f"Encontrado: {element.window_text()}")
            
            Busca relativa a uma janela:
            
            >>> window = app.window(title="Minha Janela")
            >>> element = finder.find_element_at_position(
            ...     x=50, y=30,
            ...     reference=PositionReference.RELATIVE_TO_WINDOW,
            ...     reference_element=window
            ... )
            
            Busca com tolerância maior:
            
            >>> element = finder.find_element_at_position(
            ...     x=100, y=200, tolerance=15
            ... )
        
        Note:
            A função utiliza Desktop().from_point() do pywinauto para
            localizar elementos. Em caso de erro, retorna None e registra
            o erro no log.
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
        
        Método interno que transforma coordenadas de diferentes sistemas
        de referência para coordenadas absolutas da tela, necessárias
        para operações de clique e busca.
        
        Args:
            x (int): Coordenada X no sistema de referência especificado.
            y (int): Coordenada Y no sistema de referência especificado.
            reference (PositionReference): Tipo de referência das coordenadas:
                - ABSOLUTE: Coordenadas já são absolutas
                - RELATIVE_TO_WINDOW: Relativas ao canto da janela
                - RELATIVE_TO_ELEMENT: Relativas ao centro do elemento
            reference_element (Optional[HwndWrapper], optional): Elemento
                de referência obrigatório para referências relativas.
                Defaults to None.
            
        Returns:
            Tuple[int, int]: Coordenadas absolutas (x, y) da tela.
            
        Raises:
            ValueError: Se reference_element for None quando obrigatório
                para o tipo de referência especificado, ou se o tipo
                de referência for inválido.
        
        Note:
            Para RELATIVE_TO_ELEMENT, as coordenadas são somadas ao
            centro do elemento. Para RELATIVE_TO_WINDOW, são somadas
            ao canto superior esquerdo da janela.
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
        Encontra elemento em posição absoluta da tela com tolerância.
        
        Método interno que realiza busca sistemática em uma área
        quadrada ao redor da posição especificada, considerando a
        tolerância definida para compensar pequenas variações.
        
        Args:
            x (int): Coordenada X absoluta da tela.
            y (int): Coordenada Y absoluta da tela.
            tolerance (int): Tolerância em pixels. A busca será realizada
                em uma área de (2*tolerance+1)² pixels centrada na posição.
            
        Returns:
            Optional[HwndWrapper]: Primeiro elemento encontrado na área
                de busca, ou None se nenhum elemento for encontrado.
        
        Note:
            Utiliza Desktop().from_point() do pywinauto para localizar
            elementos. A busca é feita pixel por pixel na área de tolerância.
            Em caso de erro, registra debug e retorna None.
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
        Encontra todos os elementos em uma região específica da tela.
        
        Realiza varredura sistemática de uma região da tela para localizar
        todos os elementos UI presentes, com opção de aplicar filtros para
        refinar os resultados.
        
        Args:
            region (ScreenRegion): Região da tela para realizar a busca.
                Define os limites da área de varredura.
            element_filter (Optional[Dict[str, Any]], optional): Dicionário
                com critérios de filtragem dos elementos encontrados.
                Chaves suportadas:
                - 'class_name': Nome da classe do elemento
                - 'control_type': Tipo de controle do elemento
                - 'title': Texto do elemento
                Defaults to None (sem filtros).
            
        Returns:
            List[HwndWrapper]: Lista de elementos encontrados na região
                que atendem aos critérios de filtro especificados.
        
        Example:
            Buscar todos os elementos em uma região:
            
            >>> region = ScreenRegion(x=100, y=50, width=300, height=200)
            >>> elements = finder.find_elements_in_region(region)
            >>> print(f"Encontrados {len(elements)} elementos")
            
            Buscar apenas botões na região:
            
            >>> filter_buttons = {'control_type': 'Button'}
            >>> buttons = finder.find_elements_in_region(region, filter_buttons)
            >>> for button in buttons:
            ...     print(f"Botão: {button.window_text()}")
            
            Buscar elementos com classe específica:
            
            >>> filter_class = {'class_name': 'TButton'}
            >>> elements = finder.find_elements_in_region(region, filter_class)
        
        Note:
            A varredura é realizada com passo de 10 pixels para otimizar
            performance. Elementos duplicados são automaticamente removidos
            baseado no handle do elemento.
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
        
        Método interno para aplicar critérios de filtragem em elementos
        encontrados durante buscas em regiões.
        
        Args:
            element (HwndWrapper): Elemento UI a ser verificado.
            element_filter (Optional[Dict[str, Any]]): Dicionário com
                critérios de filtragem. Se None, retorna True.
                Chaves suportadas:
                - 'class_name': Nome da classe do elemento
                - 'control_type': Tipo de controle do elemento  
                - 'title': Texto/título do elemento
            
        Returns:
            bool: True se o elemento atende a todos os critérios
                especificados, False caso contrário.
        
        Note:
            Este é um método interno. Em caso de erro ao acessar
            propriedades do elemento, retorna False.
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
        Executa clique do mouse em uma posição específica da tela.
        
        Realiza clique simples ou duplo em coordenadas especificadas,
        com suporte a diferentes tipos de referência e botões do mouse.
        Inclui captura de screenshot em caso de erro para debugging.
        
        Args:
            x (int): Coordenada X da posição para clicar.
            y (int): Coordenada Y da posição para clicar.
            reference (PositionReference, optional): Tipo de referência para
                as coordenadas. Defaults to PositionReference.ABSOLUTE.
            reference_element (Optional[HwndWrapper], optional): Elemento de
                referência para coordenadas relativas. Defaults to None.
            button (str, optional): Botão do mouse a ser usado.
                Opções: 'left', 'right', 'middle'. Defaults to 'left'.
            double_click (bool, optional): Se True, executa duplo clique.
                Defaults to False.
            
        Raises:
            UIInteractionError: Se o clique falhar por qualquer motivo,
                incluindo coordenadas inválidas ou problemas de sistema.
        
        Example:
            Clique simples em coordenadas absolutas:
            
            >>> finder.click_at_position(100, 200)
            
            Duplo clique com botão direito:
            
            >>> finder.click_at_position(
            ...     x=150, y=250,
            ...     button='right',
            ...     double_click=True
            ... )
            
            Clique relativo a uma janela:
            
            >>> window = app.window(title="Minha Janela")
            >>> finder.click_at_position(
            ...     x=50, y=30,
            ...     reference=PositionReference.RELATIVE_TO_WINDOW,
            ...     reference_element=window
            ... )
        
        Note:
            Em caso de erro, um screenshot é automaticamente capturado
            para auxiliar no debugging. O erro é registrado no log
            antes de lançar a exceção.
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
        Calcula e retorna a posição central de um elemento UI.
        
        Obtém as dimensões do elemento e calcula as coordenadas do seu
        centro geométrico, útil para cliques precisos e posicionamento.
        
        Args:
            element (HwndWrapper): Elemento UI para calcular o centro.
            reference (PositionReference, optional): Tipo de referência
                para o retorno das coordenadas. Atualmente apenas
                ABSOLUTE é suportado. Defaults to PositionReference.ABSOLUTE.
            
        Returns:
            Tuple[int, int]: Coordenadas (x, y) do centro do elemento
                em pixels da tela.
        
        Raises:
            UIInteractionError: Se não for possível obter as dimensões
                do elemento ou calcular sua posição.
        
        Example:
            Obter centro de um botão:
            
            >>> button = app.window().child_window(title="OK")
            >>> center_x, center_y = finder.get_element_center_position(button)
            >>> print(f"Centro do botão: ({center_x}, {center_y})")
            
            Usar centro para clique:
            
            >>> center = finder.get_element_center_position(element)
            >>> finder.click_at_position(center[0], center[1])
        
        Note:
            O cálculo é baseado no retângulo delimitador do elemento
            obtido através do método rectangle() do pywinauto.
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
            """
            Verifica se existe elemento na posição especificada.
            
            Returns:
                bool: True se elemento existe na posição, False caso contrário.
            """
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
            element = self.find_element_at_position(
                x, y, reference, reference_element, tolerance
            )
            if element is not None:
                return element
        
        # Se chegou aqui, elemento não foi encontrado
        raise UIElementNotFoundError(
            f"Elemento não encontrado na posição ({x}, {y}) após {timeout}s"
        )
    
    def capture_region_screenshot(
        self,
        region: ScreenRegion,
        save_path: Optional[str] = None
    ) -> Image.Image:
        """
        Captura screenshot de uma região específica da tela.
        
        Realiza captura de tela de uma área delimitada, útil para
        documentação, debugging e análise visual de elementos.
        
        Args:
            region (ScreenRegion): Região da tela para capturar.
                Define os limites da área de screenshot.
            save_path (Optional[str], optional): Caminho completo do arquivo
                para salvar a imagem. Se fornecido, a imagem será salva
                automaticamente. Defaults to None.
            
        Returns:
            Image.Image: Objeto PIL Image com a imagem capturada.
                Pode ser manipulada ou salva posteriormente.
        
        Raises:
            UIInteractionError: Se a captura falhar por problemas de
                sistema ou região inválida.
        
        Example:
            Capturar região e retornar imagem:
            
            >>> region = ScreenRegion(x=100, y=50, width=300, height=200)
            >>> image = finder.capture_region_screenshot(region)
            >>> image.show()  # Exibe a imagem
            
            Capturar e salvar automaticamente:
            
            >>> screenshot = finder.capture_region_screenshot(
            ...     region=region,
            ...     save_path="/path/to/screenshot.png"
            ... )
            
            Capturar região de um elemento:
            
            >>> element_region = finder.get_screen_region_from_element(button)
            >>> screenshot = finder.capture_region_screenshot(element_region)
        
        Note:
            Utiliza PIL.ImageGrab para captura. A região deve estar
            dentro dos limites da tela para evitar erros.
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
        Cria uma região da tela baseada nas dimensões de um elemento.
        
        Converte as dimensões de um elemento UI em uma ScreenRegion,
        com opção de expandir a área para incluir elementos adjacentes
        ou criar margem de segurança.
        
        Args:
            element (HwndWrapper): Elemento UI de referência para
                definir a região.
            expand_by (int, optional): Número de pixels para expandir
                a região em todas as direções. Valores positivos
                aumentam a região, valores negativos a reduzem.
                Defaults to 0.
            
        Returns:
            ScreenRegion: Objeto ScreenRegion correspondente à área
                do elemento, opcionalmente expandida.
        
        Raises:
            UIInteractionError: Se não for possível obter as dimensões
                do elemento ou criar a região.
        
        Example:
            Criar região exata do elemento:
            
            >>> button = app.window().child_window(title="OK")
            >>> region = finder.get_screen_region_from_element(button)
            >>> print(f"Região: {region.bounds}")
            
            Criar região expandida:
            
            >>> expanded_region = finder.get_screen_region_from_element(
            ...     element=button,
            ...     expand_by=20
            ... )
            
            Usar região para captura:
            
            >>> region = finder.get_screen_region_from_element(element)
            >>> screenshot = finder.capture_region_screenshot(region)
        
        Note:
            A expansão é aplicada igualmente em todas as direções.
            Para expansão assimétrica, modifique a ScreenRegion retornada.
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