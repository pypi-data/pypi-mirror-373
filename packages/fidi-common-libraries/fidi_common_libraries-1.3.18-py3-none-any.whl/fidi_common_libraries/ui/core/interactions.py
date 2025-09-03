"""
Utilitários avançados para interações com elementos da interface gráfica.

Este módulo fornece uma camada de abstração robusta para interações com
elementos de interface gráfica, oferecendo métodos seguros e confiáveis
para operações comuns como cliques, digitação de texto, seleção de opções
e manipulação de controles.

O módulo implementa tratamento de erros abrangente, logging detalhado,
validações de estado e captura automática de screenshots para debugging.
Todas as operações incluem timeouts configuráveis e retry automático
para garantir máxima confiabilidade em ambientes de automação.

Funcionalidades principais:
- Cliques seguros com validação de estado
- Digitação de texto com limpeza automática
- Seleção em dropdowns e listas
- Manipulação de checkboxes e radio buttons
- Operações de scroll e drag-and-drop
- Extração de texto de elementos

Example:
    Uso básico das interações:
    
    >>> interactions = UIInteractions()
    >>> button = app.window().child_window(title="OK")
    >>> interactions.safe_click(button)
    
    Digitação de texto com validação:
    
    >>> text_field = app.window().child_window(auto_id="txtName")
    >>> interactions.safe_type_text(text_field, "João Silva")
    
    Seleção em dropdown:
    
    >>> dropdown = app.window().child_window(class_name="ComboBox")
    >>> interactions.select_from_dropdown(dropdown, "Opção 1")

Note:
    Este módulo requer configuração adequada através do ui_config
    e depende dos módulos de validação e captura de screenshots.
"""

import logging
import time
from typing import Optional, Union, List, Any
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.keyboard import send_keys

from ..config.ui_config import get_ui_config
from ..exceptions.ui_exceptions import UIInteractionError
from .waits import UIWaits
from ..utils.screenshot import capture_screenshot_on_error
from ..utils.validation import validate_text_input, validate_element_state


logger = logging.getLogger(__name__)


class UIInteractions:
    """
    Classe principal para interações seguras e robustas com elementos UI.
    
    Esta classe encapsula todas as operações comuns de interação com
    elementos de interface gráfica, fornecendo uma API consistente e
    confiável para automação. Cada método implementa validações de estado,
    tratamento de erros abrangente e logging detalhado.
    
    A classe utiliza configurações centralizadas para timeouts, delays
    e comportamentos de retry, permitindo ajuste fino do comportamento
    de automação conforme necessário.
    
    Attributes:
        config: Configuração de UI carregada do sistema.
        waits: Instância de UIWaits para operações de espera.
    
    Example:
        Inicialização e uso básico:
        
        >>> interactions = UIInteractions()
        >>> element = app.window().child_window(title="Botão")
        >>> interactions.safe_click(element)
        
        Configuração de delays personalizados:
        
        >>> interactions.safe_click(
        ...     element,
        ...     wait_before=1.0,
        ...     wait_after=0.5
        ... )
    
    Note:
        A classe carrega automaticamente as configurações de UI
        e inicializa os componentes de espera necessários.
    """
    
    def __init__(self):
        """
        Inicializa a classe de interações UI com configurações e componentes.
        
        Carrega as configurações de UI do sistema e inicializa os
        componentes necessários para operações de espera e validação.
        """
        self.config = get_ui_config()
        self.waits = UIWaits()
    
    def safe_click(
        self,
        element: HwndWrapper,
        wait_before: Optional[float] = None,
        wait_after: Optional[float] = None,
        double_click: bool = False,
        right_click: bool = False,
        verify_enabled: bool = True
    ) -> None:
        """
        Executa clique seguro em elemento com validações e tratamento de erros.
        
        Realiza clique em elemento UI com validações de estado, timeouts
        configuráveis e captura automática de screenshot em caso de erro.
        Suporta diferentes tipos de clique e verificações de habilitação.
        
        Args:
            element (HwndWrapper): Elemento UI a ser clicado.
            wait_before (Optional[float], optional): Tempo de espera em segundos
                antes de executar o clique. Se None, usa configuração padrão.
                Defaults to None.
            wait_after (Optional[float], optional): Tempo de espera em segundos
                após executar o clique. Se None, usa configuração padrão.
                Defaults to None.
            double_click (bool, optional): Se True, executa duplo clique.
                Defaults to False.
            right_click (bool, optional): Se True, executa clique com botão
                direito do mouse. Defaults to False.
            verify_enabled (bool, optional): Se True, verifica se o elemento
                está habilitado antes do clique. Defaults to True.
            
        Raises:
            UIInteractionError: Se o clique falhar por qualquer motivo,
                incluindo elemento não encontrado, não habilitado ou
                erro durante a execução.
        
        Example:
            Clique simples:
            
            >>> button = app.window().child_window(title="OK")
            >>> interactions.safe_click(button)
            
            Duplo clique com delays personalizados:
            
            >>> interactions.safe_click(
            ...     element=button,
            ...     double_click=True,
            ...     wait_before=1.0,
            ...     wait_after=0.5
            ... )
            
            Clique direito sem verificação de habilitação:
            
            >>> interactions.safe_click(
            ...     element=menu_item,
            ...     right_click=True,
            ...     verify_enabled=False
            ... )
        
        Note:
            Em caso de erro, um screenshot é automaticamente capturado
            para auxiliar no debugging. O erro é registrado no log
            antes de lançar a exceção.
        """
        wait_before = wait_before or self.config.wait_before_click
        wait_after = wait_after or self.config.wait_after_click
        
        try:
            # Validações pré-clique
            if verify_enabled:
                validate_element_state(element, enabled=True)
            
            self.waits.wait_for_element_ready(element)
            
            if wait_before > 0:
                time.sleep(wait_before)
            
            # Executa o clique apropriado
            if double_click:
                logger.debug("Executando duplo clique")
                element.double_click()
            elif right_click:
                logger.debug("Executando clique direito")
                element.right_click()
            else:
                logger.debug("Executando clique simples")
                element.click()
            
            if self.config.log_interactions:
                logger.info(f"Clique realizado com sucesso no elemento")
            
            if wait_after > 0:
                time.sleep(wait_after)
                
        except Exception as e:
            error_msg = f"Erro ao clicar no elemento"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("click_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def safe_type_text(
        self,
        element: HwndWrapper,
        text: str,
        clear_first: bool = True,
        with_spaces: bool = True,
        use_send_keys: bool = False,
        validate_input: bool = True
    ) -> None:
        """
        Digita texto em elemento de forma segura com validações e limpeza.
        
        Executa digitação de texto em campo de entrada com foco automático,
        limpeza opcional do conteúdo existente e validação de entrada.
        Suporta diferentes métodos de digitação para máxima compatibilidade.
        
        Args:
            element (HwndWrapper): Elemento de entrada de texto onde digitar.
            text (str): Texto a ser digitado no elemento.
            clear_first (bool, optional): Se True, limpa o conteúdo existente
                antes de digitar. Defaults to True.
            with_spaces (bool, optional): Se True, preserva espaços no texto.
                Se False, remove todos os espaços. Defaults to True.
            use_send_keys (bool, optional): Se True, usa send_keys global
                em vez do type_keys do elemento. Útil para casos especiais.
                Defaults to False.
            validate_input (bool, optional): Se True, valida o texto de entrada
                e o estado do elemento antes de digitar. Defaults to True.
            
        Raises:
            UIInteractionError: Se a digitação falhar por qualquer motivo,
                incluindo elemento não encontrado, não habilitado, texto
                inválido ou erro durante a digitação.
        
        Example:
            Digitação básica:
            
            >>> text_field = app.window().child_window(auto_id="txtName")
            >>> interactions.safe_type_text(text_field, "João Silva")
            
            Digitação sem limpar campo existente:
            
            >>> interactions.safe_type_text(
            ...     element=text_field,
            ...     text=" - Complemento",
            ...     clear_first=False
            ... )
            
            Digitação usando send_keys global:
            
            >>> interactions.safe_type_text(
            ...     element=text_field,
            ...     text="Texto especial",
            ...     use_send_keys=True
            ... )
        
        Note:
            O método tenta diferentes estratégias de limpeza de campo
            e registra o texto digitado (truncado) no log para auditoria.
        """
        try:
            if validate_input:
                validate_text_input(text)
                validate_element_state(element, enabled=True)
            
            self.waits.wait_for_element_ready(element)
            
            # Foca no elemento
            element.set_focus()
            
            if clear_first:
                self._clear_field(element)
            
            if not with_spaces:
                text = text.replace(" ", "")
            
            # Escolhe o método de digitação
            if use_send_keys:
                send_keys(text)
            else:
                element.type_keys(text, with_spaces=with_spaces)
            
            if self.config.log_interactions:
                logger.info(f"Texto digitado com sucesso: '{text[:20]}{'...' if len(text) > 20 else ''}'")
                
        except Exception as e:
            error_msg = f"Erro ao digitar texto"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("type_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def _clear_field(self, element: HwndWrapper) -> None:
        """
        Limpa o conteúdo de um campo de texto usando múltiplas estratégias.
        
        Método interno que tenta diferentes abordagens para limpar um campo
        de texto, desde métodos específicos do elemento até comandos de
        teclado globais.
        
        Args:
            element (HwndWrapper): Elemento de texto a ser limpo.
        
        Note:
            Este é um método interno que implementa fallback automático
            entre diferentes estratégias de limpeza para máxima compatibilidade.
        """
        try:
            # Tenta diferentes métodos de limpeza
            element.set_text("")  # type: ignore
        except:
            try:
                element.select()  # type: ignore
                send_keys("{DELETE}")
            except:
                send_keys("^a{DELETE}")
    
    def select_from_dropdown(
        self,
        dropdown_element: HwndWrapper,
        option_text: str,
        by_index: bool = False
    ) -> None:
        """
        Seleciona opção em dropdown ou lista suspensa de forma segura.
        
        Executa seleção de item em controle dropdown com suporte a seleção
        por texto ou índice numérico. Inclui validações de estado e
        tratamento de erros robusto.
        
        Args:
            dropdown_element (HwndWrapper): Elemento dropdown ou ComboBox
                onde realizar a seleção.
            option_text (str): Texto da opção a ser selecionada ou índice
                numérico como string se by_index=True.
            by_index (bool, optional): Se True, interpreta option_text como
                índice numérico (base 0). Se False, busca por texto exato.
                Defaults to False.
            
        Raises:
            UIInteractionError: Se a seleção falhar por qualquer motivo,
                incluindo opção não encontrada, dropdown não disponível
                ou erro durante a seleção.
        
        Example:
            Seleção por texto:
            
            >>> dropdown = app.window().child_window(class_name="ComboBox")
            >>> interactions.select_from_dropdown(dropdown, "Opção 1")
            
            Seleção por índice:
            
            >>> interactions.select_from_dropdown(
            ...     dropdown_element=dropdown,
            ...     option_text="2",
            ...     by_index=True
            ... )
            
            Seleção em lista de países:
            
            >>> country_dropdown = app.window().child_window(auto_id="cmbCountry")
            >>> interactions.select_from_dropdown(country_dropdown, "Brasil")
        
        Note:
            Para seleção por índice, o primeiro item tem índice 0.
            Em caso de erro, um screenshot é capturado automaticamente.
        """
        try:
            self.waits.wait_for_element_ready(dropdown_element)
            
            if by_index:
                index = int(option_text)
                dropdown_element.select(index)  # type: ignore
                logger.info(f"Opção selecionada por índice: {index}")
            else:
                dropdown_element.select(option_text)  # type: ignore
                logger.info(f"Opção selecionada: '{option_text}'")
                
        except Exception as e:
            error_msg = f"Erro ao selecionar opção do dropdown"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("dropdown_selection_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def check_checkbox(
        self,
        checkbox_element: HwndWrapper,
        check: bool = True
    ) -> None:
        """
        Marca ou desmarca checkbox com verificação de estado atual.
        
        Executa operação de marcação/desmarcação em checkbox apenas se
        necessário, verificando o estado atual antes de realizar a ação.
        Evita cliques desnecessários quando o checkbox já está no estado desejado.
        
        Args:
            checkbox_element (HwndWrapper): Elemento checkbox ou radio button
                a ser manipulado.
            check (bool, optional): Se True, marca o checkbox. Se False,
                desmarca o checkbox. Defaults to True.
            
        Raises:
            UIInteractionError: Se a operação falhar por qualquer motivo,
                incluindo elemento não encontrado, não acessível ou
                erro durante a manipulação.
        
        Example:
            Marcar checkbox:
            
            >>> checkbox = app.window().child_window(auto_id="chkAgree")
            >>> interactions.check_checkbox(checkbox, check=True)
            
            Desmarcar checkbox:
            
            >>> interactions.check_checkbox(
            ...     checkbox_element=checkbox,
            ...     check=False
            ... )
            
            Marcar múltiplos checkboxes:
            
            >>> checkboxes = app.window().children(class_name="CheckBox")
            >>> for cb in checkboxes:
            ...     interactions.check_checkbox(cb, check=True)
        
        Note:
            O método verifica o estado atual do checkbox antes de clicar,
            evitando ações desnecessárias e registrando o resultado no log.
        """
        try:
            self.waits.wait_for_element_ready(checkbox_element)
            
            current_state = checkbox_element.get_check_state()  # type: ignore
            target_state = 1 if check else 0
            
            if current_state != target_state:
                checkbox_element.click()
                action = "marcado" if check else "desmarcado"
                logger.info(f"Checkbox {action} com sucesso")
            else:
                action = "já estava marcado" if check else "já estava desmarcado"
                logger.debug(f"Checkbox {action}")
                
        except Exception as e:
            error_msg = f"Erro ao {'marcar' if check else 'desmarcar'} checkbox"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("checkbox_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def scroll_element(
        self,
        element: HwndWrapper,
        direction: str = "down",
        clicks: int = 3
    ) -> None:
        """
        Executa operação de scroll em elemento com direção e intensidade configuráveis.
        
        Realiza scroll em elemento scrollável (lista, área de texto, etc.)
        usando roda do mouse virtual. Suporta todas as direções e permite
        controle da intensidade através do número de cliques.
        
        Args:
            element (HwndWrapper): Elemento scrollável onde executar o scroll.
            direction (str, optional): Direção do scroll. Opções válidas:
                - "up": Scroll para cima
                - "down": Scroll para baixo
                - "left": Scroll para esquerda
                - "right": Scroll para direita
                Defaults to "down".
            clicks (int, optional): Número de cliques da roda do mouse.
                Valores maiores resultam em scroll mais intenso.
                Defaults to 3.
            
        Raises:
            UIInteractionError: Se o scroll falhar por qualquer motivo,
                incluindo elemento não scrollável ou direção inválida.
            ValueError: Se a direção especificada não for válida.
        
        Example:
            Scroll básico para baixo:
            
            >>> list_element = app.window().child_window(class_name="ListBox")
            >>> interactions.scroll_element(list_element)
            
            Scroll intenso para cima:
            
            >>> interactions.scroll_element(
            ...     element=list_element,
            ...     direction="up",
            ...     clicks=10
            ... )
            
            Scroll horizontal:
            
            >>> text_area = app.window().child_window(class_name="Edit")
            >>> interactions.scroll_element(text_area, direction="right", clicks=5)
        
        Note:
            Nem todos os elementos suportam scroll em todas as direções.
            O método valida a direção antes de executar a operação.
        """
        try:
            self.waits.wait_for_element_ready(element)
            
            direction_map = {
                "up": "up",
                "down": "down", 
                "left": "left",
                "right": "right"
            }
            
            if direction not in direction_map:
                raise ValueError(f"Direção inválida: {direction}")
            
            element.scroll(direction_map[direction], "wheel", clicks)
            logger.debug(f"Scroll {direction} realizado com {clicks} cliques")
            
        except Exception as e:
            error_msg = f"Erro ao fazer scroll"
            logger.error(f"{error_msg}: {e}")
            raise UIInteractionError(error_msg, str(e))
    
    def drag_and_drop(
        self,
        source_element: HwndWrapper,
        target_element: HwndWrapper
    ) -> None:
        """
        Executa operação de arrastar e soltar entre dois elementos.
        
        Realiza drag-and-drop calculando automaticamente as posições
        centrais dos elementos origem e destino. Inclui validações
        de estado para ambos os elementos antes da operação.
        
        Args:
            source_element (HwndWrapper): Elemento origem a ser arrastado.
                Deve ser um elemento que suporte operações de drag.
            target_element (HwndWrapper): Elemento destino onde soltar.
                Deve ser um elemento que aceite drops.
            
        Raises:
            UIInteractionError: Se a operação falhar por qualquer motivo,
                incluindo elementos não encontrados, não acessíveis ou
                erro durante a execução do drag-and-drop.
        
        Example:
            Arrastar arquivo para pasta:
            
            >>> file_item = app.window().child_window(title="documento.txt")
            >>> folder_item = app.window().child_window(title="Pasta Destino")
            >>> interactions.drag_and_drop(file_item, folder_item)
            
            Arrastar item de lista:
            
            >>> source_item = list1.child_window(title="Item A")
            >>> target_list = app.window().child_window(auto_id="list2")
            >>> interactions.drag_and_drop(source_item, target_list)
        
        Note:
            A operação calcula automaticamente os pontos centrais dos
            elementos para máxima precisão. Screenshot é capturado
            automaticamente em caso de erro.
        """
        try:
            self.waits.wait_for_element_ready(source_element)
            self.waits.wait_for_element_ready(target_element)
            
            source_rect = source_element.rectangle()
            target_rect = target_element.rectangle()
            
            source_element.drag_mouse_input(
                dst=(target_rect.mid_point().x, target_rect.mid_point().y)
            )
            
            logger.info("Drag and drop realizado com sucesso")
            
        except Exception as e:
            error_msg = f"Erro ao realizar drag and drop"
            logger.error(f"{error_msg}: {e}")
            capture_screenshot_on_error("drag_drop_failed")
            raise UIInteractionError(error_msg, str(e))
    
    def get_element_text(self, element: HwndWrapper) -> str:
        """
        Extrai texto de elemento usando múltiplas estratégias de leitura.
        
        Obtém o texto de um elemento UI tentando diferentes métodos
        de extração para máxima compatibilidade com diferentes tipos
        de controles e estados de elemento.
        
        Args:
            element (HwndWrapper): Elemento UI do qual extrair o texto.
            
        Returns:
            str: Texto extraído do elemento. Retorna string vazia se
                o elemento não contiver texto visível.
            
        Raises:
            UIInteractionError: Se não conseguir acessar o elemento ou
                extrair texto por qualquer método disponível.
        
        Example:
            Obter texto de label:
            
            >>> label = app.window().child_window(auto_id="lblStatus")
            >>> status_text = interactions.get_element_text(label)
            >>> print(f"Status: {status_text}")
            
            Obter valor de campo de texto:
            
            >>> text_field = app.window().child_window(auto_id="txtName")
            >>> current_value = interactions.get_element_text(text_field)
            
            Verificar texto de botão:
            
            >>> button = app.window().child_window(class_name="Button")
            >>> button_text = interactions.get_element_text(button)
            >>> assert button_text == "Salvar"
        
        Note:
            O método tenta window_text(), texts()[0] e get_value()
            em sequência para máxima compatibilidade com diferentes
            tipos de elementos.
        """
        try:
            self.waits.wait_for_element_ready(element)
            
            # Tenta diferentes métodos para obter o texto
            try:
                return element.window_text()
            except:
                try:
                    return element.texts()[0] if element.texts() else ""
                except:
                    return element.get_value()  # type: ignore
                    
        except Exception as e:
            error_msg = f"Erro ao obter texto do elemento"
            logger.error(f"{error_msg}: {e}")
            raise UIInteractionError(error_msg, str(e))