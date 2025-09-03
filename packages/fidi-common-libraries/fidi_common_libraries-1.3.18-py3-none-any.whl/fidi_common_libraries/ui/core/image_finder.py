"""
Utilitários avançados para localização de elementos por reconhecimento de imagem.

Este módulo implementa funcionalidades sofisticadas de computer vision
para localização de elementos de interface gráfica baseado em template
matching e reconhecimento visual. Utiliza OpenCV para processamento de
imagens e oferece alta precisão na detecção de elementos visuais.

O módulo é especialmente útil para:
- Automação de interfaces sem identificadores únicos
- Detecção de elementos gráficos complexos
- Validação visual de estados da interface
- Criação de bibliotecas de templates reutilizáveis

Funcionalidades principais:
- Template matching com múltiplos algoritmos
- Busca em regiões específicas da tela
- Detecção de múltiplas ocorrências
- Cliques baseados em reconhecimento visual
- Aguardar elementos aparecerem visualmente
- Criação e gerenciamento de templates

Example:
    Uso básico do reconhecimento de imagem:
    
    >>> finder = ImageFinder("templates/")
    >>> result = finder.find_element_by_image("button_ok.png")
    >>> if result.found:
    ...     print(f"Botão encontrado com {result.confidence:.2f} de confiança")
    
    Clique baseado em imagem:
    
    >>> success = finder.click_on_image("save_button.png", confidence_threshold=0.9)
    >>> if success:
    ...     print("Clique realizado com sucesso")
    
    Aguardar elemento aparecer:
    
    >>> result = finder.wait_for_image("loading_complete.png", timeout=30)
    >>> print(f"Elemento apareceu na posição {result.position}")

Note:
    Este módulo requer OpenCV (cv2) e PIL para processamento de imagens.
    Templates devem estar em formato PNG para melhor compatibilidade.
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
    Resultado detalhado de uma operação de busca por imagem.
    
    Esta classe encapsula todas as informações sobre o resultado de uma
    operação de template matching, incluindo localização, confiança e
    metadados do template utilizado.
    
    Attributes:
        found (bool): Indica se a imagem foi encontrada com confiança
            suficiente baseada no threshold especificado.
        confidence (float): Nível de confiança do match, variando de 0.0
            (nenhuma correspondência) a 1.0 (correspondência perfeita).
        position (Tuple[int, int]): Coordenadas (x, y) do canto superior
            esquerdo onde a imagem foi encontrada na tela.
        region (ScreenRegion): Região retangular da tela que contém
            a imagem encontrada, incluindo dimensões completas.
        template_path (str): Caminho completo do arquivo template
            utilizado na busca para referência e debugging.
    
    Example:
        Analisando resultado de busca:
        
        >>> result = finder.find_element_by_image("button.png")
        >>> if result.found:
        ...     print(f"Encontrado em {result.position}")
        ...     print(f"Confiança: {result.confidence:.3f}")
        ...     print(f"Região: {result.region.bounds}")
    """
    found: bool
    confidence: float
    position: Tuple[int, int]
    region: ScreenRegion
    template_path: str


class ImageFinder:
    """
    Localizador avançado de elementos por reconhecimento de imagem e computer vision.
    
    Esta classe implementa um sistema completo de localização de elementos
    de interface gráfica baseado em template matching usando OpenCV. Oferece
    funcionalidades robustas para detecção, interação e gerenciamento de
    templates visuais.
    
    A classe suporta múltiplos algoritmos de template matching, busca em
    regiões específicas, detecção de múltiplas ocorrências e operações
    de interação baseadas em reconhecimento visual.
    
    Attributes:
        config: Configuração de UI carregada do sistema.
        position_finder: Instância de PositionFinder para operações de posição.
        templates_dir: Diretório onde os templates são armazenados.
    
    Example:
        Inicialização e uso básico:
        
        >>> finder = ImageFinder("my_templates/")
        >>> result = finder.find_element_by_image("login_button.png")
        >>> if result.found:
        ...     finder.click_on_image("login_button.png")
        
        Busca com parâmetros personalizados:
        
        >>> region = ScreenRegion(x=100, y=50, width=400, height=300)
        >>> result = finder.find_element_by_image(
        ...     "icon.png",
        ...     confidence_threshold=0.95,
        ...     search_region=region
        ... )
    
    Note:
        A classe cria automaticamente o diretório de templates se
        não existir. Templates em formato PNG são recomendados para
        melhor compatibilidade e precisão.
    """
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Inicializa o localizador de imagens com configurações e componentes.
        
        Configura o sistema de reconhecimento de imagem, carrega as
        configurações de UI e inicializa os componentes necessários para
        operações de template matching.
        
        Args:
            templates_dir (str, optional): Diretório onde os templates de
                imagem serão armazenados e carregados. O diretório será
                criado automaticamente se não existir. Defaults to "templates".
        
        Example:
            Inicialização com diretório personalizado:
            
            >>> finder = ImageFinder("assets/ui_templates/")
            
            Inicialização com diretório padrão:
            
            >>> finder = ImageFinder()
        
        Note:
            O diretório de templates é criado automaticamente se não existir.
            Recomenda-se usar caminhos relativos para portabilidade.
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
        Localiza elemento na tela usando template matching avançado.
        
        Executa busca de elemento visual na tela usando algoritmos de
        template matching do OpenCV. Suporta diferentes métodos de
        correspondência e permite busca em regiões específicas para
        otimizar performance e precisão.
        
        Args:
            template_path (str): Caminho completo para o arquivo de imagem
                template. Deve ser um arquivo válido nos formatos suportados
                pelo OpenCV (PNG, JPG, BMP, etc.).
            confidence_threshold (float, optional): Limite mínimo de confiança
                para considerar um match válido. Varia de 0.0 (qualquer
                correspondência) a 1.0 (correspondência perfeita).
                Defaults to 0.8.
            search_region (Optional[ScreenRegion], optional): Região específica
                da tela para realizar a busca. Se None, busca na tela inteira.
                Defaults to None.
            method (int, optional): Método de template matching do OpenCV.
                Opções comuns: cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED.
                Defaults to cv2.TM_CCOEFF_NORMED.
            
        Returns:
            ImageMatchResult: Objeto contendo todos os detalhes do resultado
                da busca, incluindo se foi encontrado, confiança, posição
                e região da correspondência.
            
        Raises:
            UIElementNotFoundError: Se ocorrer erro durante a busca,
                incluindo template não encontrado ou inválido.
            FileNotFoundError: Se o arquivo template não existir.
            ValueError: Se o template não puder ser carregado.
        
        Example:
            Busca básica:
            
            >>> result = finder.find_element_by_image("button_save.png")
            >>> if result.found:
            ...     print(f"Botão encontrado em {result.position}")
            
            Busca com alta precisão:
            
            >>> result = finder.find_element_by_image(
            ...     "icon_critical.png",
            ...     confidence_threshold=0.95
            ... )
            
            Busca em região específica:
            
            >>> toolbar_region = ScreenRegion(0, 0, 800, 100)
            >>> result = finder.find_element_by_image(
            ...     "toolbar_button.png",
            ...     search_region=toolbar_region
            ... )
        
        Note:
            Templates em formato PNG oferecem melhor precisão.
            Valores de confidence_threshold muito baixos podem gerar
            falsos positivos, enquanto valores muito altos podem
            perder matches válidos.
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
        Localiza todas as ocorrências de um template na tela simultaneamente.
        
        Executa busca abrangente para encontrar múltiplas instâncias do mesmo
        template visual na tela. Útil para detectar elementos repetidos como
        ícones, botões ou itens de lista.
        
        Args:
            template_path (str): Caminho para o arquivo de imagem template.
            confidence_threshold (float, optional): Limite mínimo de confiança
                para considerar matches válidos. Defaults to 0.8.
            search_region (Optional[ScreenRegion], optional): Região específica
                para busca. Se None, busca na tela inteira. Defaults to None.
            method (int, optional): Método de template matching do OpenCV.
                Defaults to cv2.TM_CCOEFF_NORMED.
            
        Returns:
            List[ImageMatchResult]: Lista contendo todos os matches encontrados
                que atendem ao critério de confiança. Lista vazia se nenhum
                match for encontrado.
        
        Example:
            Encontrar todos os ícones de arquivo:
            
            >>> matches = finder.find_all_matches("file_icon.png")
            >>> print(f"Encontrados {len(matches)} arquivos")
            >>> for match in matches:
            ...     print(f"Arquivo em {match.position}")
            
            Buscar botões em uma barra de ferramentas:
            
            >>> toolbar = ScreenRegion(0, 0, 1024, 80)
            >>> buttons = finder.find_all_matches(
            ...     "toolbar_button.png",
            ...     search_region=toolbar,
            ...     confidence_threshold=0.9
            ... )
        
        Note:
            Esta função pode retornar muitos resultados para templates
            muito genéricos. Use confidence_threshold mais alto para
            reduzir falsos positivos.
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
        Localiza e clica em elemento baseado em reconhecimento de imagem.
        
        Combina busca por template matching com execução de clique,
        oferecendo uma solução completa para interação com elementos
        visuais. Calcula automaticamente a posição de clique baseada
        no centro da imagem encontrada.
        
        Args:
            template_path (str): Caminho para o arquivo de imagem template
                do elemento a ser clicado.
            confidence_threshold (float, optional): Limite mínimo de confiança
                para considerar o elemento encontrado. Defaults to 0.8.
            search_region (Optional[ScreenRegion], optional): Região específica
                para buscar o elemento. Defaults to None.
            click_offset (Tuple[int, int], optional): Deslocamento (x, y) em
                pixels do ponto de clique em relação ao centro da imagem.
                Útil para clicar em pontos específicos do elemento.
                Defaults to (0, 0).
            double_click (bool, optional): Se True, executa duplo clique.
                Defaults to False.
            
        Returns:
            bool: True se o elemento foi encontrado e clicado com sucesso,
                False se o elemento não foi encontrado ou ocorreu erro.
        
        Example:
            Clique simples em botão:
            
            >>> success = finder.click_on_image("button_ok.png")
            >>> if success:
            ...     print("Botão OK clicado")
            
            Duplo clique com offset:
            
            >>> success = finder.click_on_image(
            ...     "file_icon.png",
            ...     click_offset=(10, -5),
            ...     double_click=True
            ... )
            
            Clique em região específica:
            
            >>> menu_area = ScreenRegion(0, 0, 200, 50)
            >>> success = finder.click_on_image(
            ...     "menu_item.png",
            ...     search_region=menu_area,
            ...     confidence_threshold=0.9
            ... )
        
        Note:
            O clique é executado no centro da imagem encontrada mais
            o offset especificado. Em caso de erro, retorna False
            em vez de lançar exceção.
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
        Aguarda elemento visual aparecer na tela com timeout configurável.
        
        Monitora continuamente a tela aguardando que um elemento visual
        específico apareça. Útil para aguardar carregamentos, transições
        de tela ou elementos que aparecem dinamicamente.
        
        Args:
            template_path (str): Caminho para o arquivo de imagem template
                do elemento a ser aguardado.
            confidence_threshold (float, optional): Limite mínimo de confiança
                para considerar o elemento encontrado. Defaults to 0.8.
            timeout (Optional[int], optional): Tempo limite em segundos para
                aguardar o elemento. Se None, usa timeout padrão da configuração.
                Defaults to None.
            search_region (Optional[ScreenRegion], optional): Região específica
                para monitorar. Se None, monitora a tela inteira.
                Defaults to None.
            check_interval (float, optional): Intervalo em segundos entre
                verificações consecutivas. Valores menores oferecem maior
                responsividade mas consomem mais recursos. Defaults to 1.0.
            
        Returns:
            ImageMatchResult: Resultado detalhado quando o elemento for
                encontrado, incluindo posição e confiança.
            
        Raises:
            UIElementNotFoundError: Se o elemento não aparecer dentro do
                tempo limite especificado.
        
        Example:
            Aguardar carregamento completar:
            
            >>> result = finder.wait_for_image(
            ...     "loading_complete.png",
            ...     timeout=30
            ... )
            >>> print(f"Carregamento completo em {result.position}")
            
            Aguardar diálogo aparecer:
            
            >>> try:
            ...     result = finder.wait_for_image(
            ...         "dialog_box.png",
            ...         confidence_threshold=0.9,
            ...         timeout=10,
            ...         check_interval=0.5
            ...     )
            ...     print("Diálogo apareceu")
            ... except UIElementNotFoundError:
            ...     print("Diálogo não apareceu no tempo esperado")
        
        Note:
            Intervalos de verificação muito baixos podem impactar performance.
            Recomenda-se usar valores entre 0.5 e 2.0 segundos dependendo
            da responsividade necessária.
        """
        timeout = timeout or self.config.default_timeout
        
        def image_exists():
            """
            Verifica se a imagem existe na tela no momento atual.
            
            Returns:
                bool: True se a imagem for encontrada com confiança suficiente,
                    False caso contrário ou em caso de erro.
            """
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
        
        # Se chegou aqui, a imagem não foi encontrada no timeout
        raise UIElementNotFoundError(
            f"Imagem não encontrada após {timeout}s: {os.path.basename(template_path)}"
        )
    
    def save_template_from_region(
        self,
        region: ScreenRegion,
        template_name: str,
        description: str = ""
    ) -> str:
        """
        Captura região da tela e salva como template reutilizável.
        
        Cria um novo template de imagem capturando uma região específica
        da tela. Útil para criar bibliotecas de templates personalizadas
        ou capturar elementos para uso posterior em automação.
        
        Args:
            region (ScreenRegion): Região retangular da tela a ser capturada
                como template.
            template_name (str): Nome do arquivo template. A extensão .png
                será adicionada automaticamente se não especificada.
            description (str, optional): Descrição textual do template
                para documentação. Será salva em arquivo de metadados
                separado. Defaults to "".
            
        Returns:
            str: Caminho completo do arquivo template salvo.
        
        Raises:
            UIInteractionError: Se ocorrer erro durante a captura ou
                salvamento do template.
        
        Example:
            Salvar botão como template:
            
            >>> button_region = ScreenRegion(100, 200, 80, 30)
            >>> template_path = finder.save_template_from_region(
            ...     button_region,
            ...     "save_button",
            ...     "Botão de salvar da barra de ferramentas"
            ... )
            >>> print(f"Template salvo em: {template_path}")
            
            Capturar ícone para reutilização:
            
            >>> icon_region = ScreenRegion(50, 50, 32, 32)
            >>> finder.save_template_from_region(
            ...     icon_region,
            ...     "warning_icon.png"
            ... )
        
        Note:
            Um arquivo de metadados (.txt) é criado automaticamente
            quando uma descrição é fornecida, contendo informações
            sobre o template para referência futura.
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
        Cria template de imagem a partir de elemento UI existente.
        
        Converte um elemento UI localizado por outros métodos em um
        template de imagem reutilizável. Útil para criar bibliotecas
        de templates baseadas em elementos já identificados.
        
        Args:
            element: Elemento UI (HwndWrapper) a ser capturado como template.
                Deve ser um elemento válido e visível na tela.
            template_name (str): Nome do arquivo template a ser criado.
                Extensão .png será adicionada se necessário.
            expand_by (int, optional): Número de pixels para expandir
                a captura além dos limites do elemento. Útil para incluir
                bordas ou sombras. Defaults to 5.
            description (str, optional): Descrição do template para
                documentação. Defaults to "".
            
        Returns:
            str: Caminho completo do arquivo template criado.
        
        Raises:
            UIInteractionError: Se ocorrer erro durante a captura do
                elemento ou criação do template.
        
        Example:
            Criar template de botão encontrado:
            
            >>> button = app.window().child_window(title="Salvar")
            >>> template_path = finder.create_template_from_element(
            ...     button,
            ...     "save_button_template",
            ...     expand_by=10,
            ...     description="Botão salvar com bordas"
            ... )
            
            Capturar elemento sem expansão:
            
            >>> icon = app.window().child_window(class_name="Icon")
            >>> finder.create_template_from_element(
            ...     icon,
            ...     "app_icon",
            ...     expand_by=0
            ... )
        
        Note:
            O elemento deve estar visível na tela no momento da captura.
            A expansão é aplicada igualmente em todas as direções.
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