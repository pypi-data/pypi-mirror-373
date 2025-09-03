"""
Utilitários avançados para localização robusta de elementos de interface gráfica.

Este módulo implementa um sistema sofisticado de localização de elementos
UI com suporte a múltiplos critérios de busca, estratégias de fallback
automáticas e tratamento de erros abrangente. É projetado para lidar com
a natureza dinâmica e instável de interfaces gráficas modernas.

O módulo oferece funcionalidades essenciais para automação UI:
- Localização com critérios primários e alternativos
- Sistema de retry automático com timeouts configuráveis
- Busca de múltiplos elementos simultaneamente
- Verificação de existência sem exceções
- Aguardar elementos aparecerem ou desaparecerem
- Captura automática de screenshots para debugging

Características principais:
- Tolerância a falhas com fallback automático
- Logging detalhado para auditoria e debugging
- Integração com sistema de esperas (UIWaits)
- Tratamento robusto de elementos instáveis

Example:
    Uso básico do localizador de elementos:
    
    >>> finder = ElementFinder()
    >>> button = finder.find_element(
    ...     parent=main_window,
    ...     primary_criteria={"title": "OK"},
    ...     fallback_criteria=[{"auto_id": "btnOK"}, {"class_name": "Button"}]
    ... )
    
    Verificação de existência:
    
    >>> if finder.element_exists(window, {"title": "Dialog"}):
    ...     print("Diálogo está presente")
    
    Aguardar elemento aparecer:
    
    >>> loading_element = finder.wait_for_element_to_appear(
    ...     parent=app_window,
    ...     criteria={"auto_id": "loadingIndicator"},
    ...     timeout=30
    ... )

Note:
    Este módulo requer pywinauto e integra-se com o sistema de
    configurações UI para timeouts e comportamentos padrão.
"""

import logging
from typing import Any, Dict, Optional, List, Union
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import ElementNotFoundError

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIElementNotFoundError
from .waits import UIWaits
from ..utils.screenshot import capture_screenshot_on_error


logger = logging.getLogger(__name__)


class ElementFinder:
    """
    Localizador avançado e robusto de elementos de interface gráfica.
    
    Esta classe implementa um sistema completo de localização de elementos
    UI com funcionalidades avançadas de tolerância a falhas, retry automático
    e estratégias de fallback. Projetada para lidar com a instabilidade
    inerente de interfaces gráficas modernas.
    
    A classe oferece múltiplas abordagens para localização:
    - Busca com critérios primários e alternativos
    - Sistema de retry com timeouts inteligentes
    - Verificação de existência não-destrutiva
    - Aguardar elementos aparecerem ou desaparecerem
    - Busca de múltiplos elementos simultaneamente
    
    Attributes:
        config: Configuração de UI carregada do sistema.
        waits: Instância de UIWaits para operações de espera.
    
    Example:
        Inicialização e uso básico:
        
        >>> finder = ElementFinder()
        >>> element = finder.find_element(
        ...     parent=window,
        ...     primary_criteria={"title": "Save"}
        ... )
        
        Busca com fallback:
        
        >>> element = finder.find_element(
        ...     parent=window,
        ...     primary_criteria={"auto_id": "btnSave"},
        ...     fallback_criteria=[
        ...         {"title": "Save"},
        ...         {"class_name": "Button", "title_re": ".*Save.*"}
        ...     ]
        ... )
    
    Note:
        A classe carrega automaticamente configurações de timeout
        e inicializa componentes de espera necessários.
    """
    
    def __init__(self):
        """
        Inicializa o localizador de elementos com configurações e componentes.
        
        Carrega as configurações de UI do sistema e inicializa os
        componentes necessários para operações de espera e localização.
        """
        self.config = get_ui_config()
        self.waits = UIWaits()
    
    def find_element(
        self,
        parent: HwndWrapper,
        primary_criteria: Dict[str, Any],
        fallback_criteria: Optional[List[Dict[str, Any]]] = None,
        wait_for_ready: bool = True,
        timeout: Optional[int] = None
    ) -> HwndWrapper:
        """
        Localiza elemento usando estratégia de critérios primários e fallback.
        
        Executa busca inteligente de elemento UI com sistema de fallback
        automático. Tenta primeiro os critérios primários e, em caso de falha,
        itera pelos critérios alternativos até encontrar o elemento ou
        esgotar todas as opções.
        
        Args:
            parent (HwndWrapper): Elemento pai onde realizar a busca.
                Deve ser um elemento válido e acessível.
            primary_criteria (Dict[str, Any]): Critérios primários para
                localização do elemento. Chaves comuns: 'title', 'auto_id',
                'class_name', 'control_type', etc.
            fallback_criteria (Optional[List[Dict[str, Any]]], optional):
                Lista de critérios alternativos a serem tentados se os
                primários falharem. Defaults to None.
            wait_for_ready (bool, optional): Se True, aguarda o elemento
                ficar pronto após ser encontrado. Defaults to True.
            timeout (Optional[int], optional): Timeout em segundos para
                a operação completa. Se None, usa timeout padrão da
                configuração. Defaults to None.
            
        Returns:
            HwndWrapper: Elemento encontrado e validado.
            
        Raises:
            UIElementNotFoundError: Se o elemento não for encontrado
                com nenhum dos critérios fornecidos.
        
        Example:
            Busca simples:
            
            >>> element = finder.find_element(
            ...     parent=window,
            ...     primary_criteria={"title": "OK"}
            ... )
            
            Busca com fallback:
            
            >>> element = finder.find_element(
            ...     parent=window,
            ...     primary_criteria={"auto_id": "btnSave"},
            ...     fallback_criteria=[
            ...         {"title": "Save"},
            ...         {"class_name": "Button", "title_re": ".*Save.*"}
            ...     ],
            ...     timeout=15
            ... )
            
            Busca sem aguardar elemento ficar pronto:
            
            >>> element = finder.find_element(
            ...     parent=dialog,
            ...     primary_criteria={"control_type": "Edit"},
            ...     wait_for_ready=False
            ... )
        
        Note:
            A função tenta cada conjunto de critérios em sequência
            até encontrar o elemento. Screenshot é capturado
            automaticamente em caso de falha.
        """
        timeout = timeout or self.config.element_timeout
        all_criteria = [primary_criteria]
        
        if fallback_criteria:
            all_criteria.extend(fallback_criteria)
        
        last_error = None
        
        for i, criteria in enumerate(all_criteria):
            try:
                logger.debug(f"Tentativa {i+1}: Buscando elemento com critérios: {criteria}")
                element = self._find_with_retry(parent, criteria, timeout)
                
                if wait_for_ready:
                    element = self.waits.wait_for_element_ready(element, timeout)
                
                logger.debug(f"Elemento encontrado com critérios: {criteria}")
                return element
                
            except Exception as e:
                last_error = e
                logger.debug(f"Critérios {criteria} falharam: {e}")
                continue
        
        # Se chegou aqui, nenhum critério funcionou
        error_msg = f"Elemento não encontrado com nenhum dos critérios fornecidos"
        logger.error(error_msg)
        capture_screenshot_on_error("element_not_found")
        raise UIElementNotFoundError(error_msg, str(last_error))
    
    def _find_with_retry(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: int
    ) -> HwndWrapper:
        """
        Localiza elemento com sistema de retry automático e validação.
        
        Método interno que implementa busca persistente com tentativas
        repetidas até o timeout. Inclui validação do elemento encontrado
        para garantir que está acessível e válido.
        
        Args:
            parent (HwndWrapper): Elemento pai onde buscar.
            criteria (Dict[str, Any]): Critérios específicos para localização.
            timeout (int): Tempo limite total em segundos para a busca.
            
        Returns:
            HwndWrapper: Elemento encontrado e validado.
        
        Raises:
            ElementNotFoundError: Se o elemento não for encontrado
                dentro do timeout especificado.
        
        Note:
            Este é um método interno que implementa retry com intervalo
            de 0.5 segundos entre tentativas. Valida o elemento
            chamando exists() antes de retornar.
        """
        import time
        
        start_time = time.time()
        last_error = None
        
        while time.time() - start_time < timeout:
            try:
                element = parent.child_window(**criteria)  # type: ignore
                # Tenta uma operação simples para verificar se o elemento é válido
                _ = element.exists()
                return element
            except Exception as e:
                last_error = e
                time.sleep(0.5)
        
        raise last_error or ElementNotFoundError(f"Elemento não encontrado: {criteria}")
    
    def find_elements(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> List[HwndWrapper]:
        """
        Localiza múltiplos elementos que atendem aos critérios especificados.
        
        Executa busca abrangente para encontrar todos os elementos filhos
        que correspondem aos critérios fornecidos. Útil para localizar
        listas de itens, botões similares ou elementos repetidos.
        
        Args:
            parent (HwndWrapper): Elemento pai onde realizar a busca.
            criteria (Dict[str, Any]): Critérios para localização dos
                elementos. Todos os elementos que atenderem aos critérios
                serão retornados.
            timeout (Optional[int], optional): Timeout em segundos para
                a operação. Se None, usa timeout padrão. Defaults to None.
            
        Returns:
            List[HwndWrapper]: Lista contendo todos os elementos encontrados
                que atendem aos critérios. Lista vazia se nenhum elemento
                for encontrado.
        
        Example:
            Encontrar todos os botões:
            
            >>> buttons = finder.find_elements(
            ...     parent=toolbar,
            ...     criteria={"control_type": "Button"}
            ... )
            >>> print(f"Encontrados {len(buttons)} botões")
            
            Encontrar itens de lista:
            
            >>> list_items = finder.find_elements(
            ...     parent=listbox,
            ...     criteria={"control_type": "ListItem"}
            ... )
            >>> for item in list_items:
            ...     print(f"Item: {item.window_text()}")
        
        Note:
            Em caso de erro, retorna lista vazia em vez de lançar
            exceção. Verifique o log para detalhes sobre erros.
        """
        timeout = timeout or self.config.element_timeout
        
        try:
            logger.debug(f"Buscando múltiplos elementos com critérios: {criteria}")
            elements = parent.children(**criteria)
            logger.debug(f"Encontrados {len(elements)} elementos")
            return elements
        except Exception as e:
            logger.error(f"Erro ao buscar múltiplos elementos: {e}")
            return []
    
    def element_exists(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: int = 5
    ) -> bool:
        """
        Verifica existência de elemento de forma não-destrutiva.
        
        Executa verificação silenciosa da existência de um elemento
        sem lançar exceções. Útil para validações condicionais e
        verificações de estado da interface.
        
        Args:
            parent (HwndWrapper): Elemento pai onde buscar.
            criteria (Dict[str, Any]): Critérios para localização do elemento.
            timeout (int, optional): Tempo limite em segundos para a
                verificação. Defaults to 5.
            
        Returns:
            bool: True se o elemento existe e é acessível,
                False caso contrário ou em caso de erro.
        
        Example:
            Verificação condicional:
            
            >>> if finder.element_exists(window, {"title": "Error Dialog"}):
            ...     print("Diálogo de erro detectado")
            ...     # Tratar erro
            ... else:
            ...     print("Nenhum erro detectado")
            
            Aguardar elemento desaparecer:
            
            >>> while finder.element_exists(window, {"auto_id": "loading"}):
            ...     time.sleep(1)
            >>> print("Carregamento concluído")
        
        Note:
            Esta função nunca lança exceções, sempre retorna
            boolean. Use para verificações que não devem interromper
            o fluxo de execução.
        """
        try:
            self._find_with_retry(parent, criteria, timeout)
            return True
        except Exception:
            return False
    
    def wait_for_element_to_appear(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> HwndWrapper:
        """
        Aguarda elemento aparecer na interface com timeout configurável.
        
        Monitora continuamente a interface aguardando que um elemento
        específico apareça. Útil para aguardar carregamentos, diálogos
        ou elementos que aparecem dinamicamente após ações do usuário.
        
        Args:
            parent (HwndWrapper): Elemento pai onde monitorar o aparecimento.
            criteria (Dict[str, Any]): Critérios para identificar o elemento
                que deve aparecer.
            timeout (Optional[int], optional): Tempo limite em segundos
                para aguardar o elemento. Se None, usa timeout padrão
                da configuração. Defaults to None.
            
        Returns:
            HwndWrapper: Elemento encontrado quando aparecer.
            
        Raises:
            UIElementNotFoundError: Se o elemento não aparecer dentro
                do tempo limite especificado.
        
        Example:
            Aguardar diálogo de confirmação:
            
            >>> dialog = finder.wait_for_element_to_appear(
            ...     parent=app_window,
            ...     criteria={"title": "Confirm Action"},
            ...     timeout=10
            ... )
            >>> print("Diálogo apareceu")
            
            Aguardar resultado de processamento:
            
            >>> result_panel = finder.wait_for_element_to_appear(
            ...     parent=main_window,
            ...     criteria={"auto_id": "resultPanel"},
            ...     timeout=30
            ... )
        
        Note:
            A função verifica a existência do elemento a cada segundo.
            Quando encontrado, retorna o elemento já pronto para uso.
        """
        timeout = timeout or self.config.default_timeout
        
        def element_appears():
            """
            Verifica se o elemento apareceu na interface.
            
            Returns:
                bool: True se o elemento existe, False caso contrário.
            """
            return self.element_exists(parent, criteria, timeout=1)
        
        logger.debug(f"Aguardando elemento aparecer: {criteria}")
        
        if self.waits.wait_for_condition(
            element_appears,
            timeout,
            condition_description=f"elemento {criteria} aparecer"
        ):
            return self.find_element(parent, criteria, wait_for_ready=True)
        
        # Se chegou aqui, elemento não apareceu no timeout
        raise UIElementNotFoundError(
            f"Elemento não apareceu após {timeout}s: {criteria}"
        )
    
    def wait_for_element_to_disappear(
        self,
        parent: HwndWrapper,
        criteria: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> bool:
        """
        Aguarda elemento desaparecer da interface com monitoramento contínuo.
        
        Monitora a interface aguardando que um elemento específico
        desapareça. Útil para aguardar fechamento de diálogos,
        conclusão de carregamentos ou elementos temporários.
        
        Args:
            parent (HwndWrapper): Elemento pai onde monitorar o desaparecimento.
            criteria (Dict[str, Any]): Critérios para identificar o elemento
                que deve desaparecer.
            timeout (Optional[int], optional): Tempo limite em segundos
                para aguardar o desaparecimento. Se None, usa timeout
                padrão da configuração. Defaults to None.
            
        Returns:
            bool: True se o elemento desapareceu dentro do tempo limite,
                False se ainda estiver presente após o timeout.
        
        Example:
            Aguardar fechamento de diálogo:
            
            >>> disappeared = finder.wait_for_element_to_disappear(
            ...     parent=app_window,
            ...     criteria={"title": "Loading..."},
            ...     timeout=30
            ... )
            >>> if disappeared:
            ...     print("Carregamento concluído")
            ... else:
            ...     print("Timeout: carregamento ainda em andamento")
            
            Aguardar elemento temporário sumir:
            
            >>> finder.wait_for_element_to_disappear(
            ...     parent=status_bar,
            ...     criteria={"auto_id": "tempMessage"},
            ...     timeout=5
            ... )
        
        Note:
            A função verifica o desaparecimento a cada segundo.
            Retorna False em caso de timeout, não lança exceção.
        """
        timeout = timeout or self.config.default_timeout
        
        def element_disappears():
            """
            Verifica se o elemento desapareceu da interface.
            
            Returns:
                bool: True se o elemento não existe mais, False se ainda existe.
            """
            return not self.element_exists(parent, criteria, timeout=1)
        
        logger.debug(f"Aguardando elemento desaparecer: {criteria}")
        
        return self.waits.wait_for_condition(
            element_disappears,
            timeout,
            condition_description=f"elemento {criteria} desaparecer"
        )