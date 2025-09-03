"""
Inspetor de elementos de UI com navegação assistida.

Fornece funcionalidades para inspeção interativa de elementos de interface gráfica,
incluindo overlay visual, captura de caminho de navegação e assistente de navegação
em tempo real para automação de UI.
"""

import os
import sys
import time
import argparse
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, Union, Callable
from pathlib import Path

try:
    import pywinauto
    from pywinauto import Application, Desktop
    from pywinauto.controls.hwndwrapper import HwndWrapper
    import pygetwindow as gw
except ImportError:
    print("❌ PyWinAuto não encontrado. Instale com: pip install pywinauto pygetwindow")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    import win32gui
    import win32con
    import win32api
    PIL_AVAILABLE = True
except ImportError:
    print("⚠️ PIL/win32 não disponível. Overlay visual não estará disponível.")
    PIL_AVAILABLE = False

try:
    import pynput
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    print("⚠️ Pynput não disponível. Navegação por mouse não estará disponível.")
    PYNPUT_AVAILABLE = False


class NavigationPath:
    """
    Gerenciador de caminho de navegação para elementos UI.
    
    Armazena e gerencia a sequência de passos de navegação durante
    a inspeção de elementos, permitindo exportação e análise posterior.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de caminho de navegação.
        
        Configura estruturas para armazenar passos de navegação,
        elemento atual e timestamp de início.
        """
        self.steps: List[Dict[str, Any]] = []
        self.current_element = None
        self.start_time = datetime.now()
    
    def add_step(self, element: Any, action: str = "navigate", coordinates: Optional[Tuple[int, int]] = None):
        """
        Adiciona um passo ao caminho de navegação.
        
        Args:
            element: Elemento UI que foi navegado.
            action: Tipo de ação realizada (navigate, click, etc.).
            coordinates: Coordenadas do clique/interação (opcional).
            
        Raises:
            Exception: Se houver erro ao extrair informações do elemento.
        """
        try:
            step = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "element_info": {
                    "name": element.window_text() or "[No Name]",
                    "class_name": element.class_name() or "[No Class]",
                    "control_type": getattr(element.element_info, 'control_type', 'Unknown'),
                    "automation_id": getattr(element.element_info, 'automation_id', '') or "[No AutoID]",
                    "handle": f"0x{element.handle:08X}",
                    "rectangle": {
                        "left": element.rectangle().left,
                        "top": element.rectangle().top,
                        "width": element.rectangle().width(),
                        "height": element.rectangle().height()
                    },
                    "is_visible": element.is_visible(),
                    "is_enabled": element.is_enabled()
                },
                "coordinates": coordinates,
                "step_number": len(self.steps) + 1
            }
            self.steps.append(step)
            self.current_element = element
            
        except Exception as e:
            print(f"❌ Erro ao adicionar passo: {e}")
    
    def get_path_summary(self) -> str:
        """
        Retorna resumo formatado do caminho de navegação.
        
        Returns:
            str: Resumo textual com todos os passos de navegação.
        """
        if not self.steps:
            return "Nenhum passo registrado"
        
        summary = f"📍 Caminho de Navegação ({len(self.steps)} passos):\n"
        summary += "=" * 60 + "\n"
        
        for step in self.steps:
            info = step["element_info"]
            summary += f"{step['step_number']:2d}. {step['action'].upper()}: {info['name']}\n"
            summary += f"    Type: {info['control_type']}\n"
            summary += f"    AutoID: {info['automation_id']}\n"
            if step['coordinates']:
                summary += f"    Coords: {step['coordinates']}\n"
            summary += "\n"
        
        return summary
    
    def export_to_file(self, filepath: str) -> bool:
        """
        Exporta caminho de navegação para arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo para exportação.
            
        Returns:
            bool: True se exportação bem-sucedida, False caso contrário.
            
        Raises:
            Exception: Se houver erro na escrita do arquivo.
        """
        try:
            export_data = {
                "metadata": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "total_steps": len(self.steps),
                    "generator": "UI Element Inspector v2.0.0"
                },
                "navigation_path": self.steps
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Erro ao exportar caminho: {e}")
            return False


class OverlayWindow:
    """
    Sistema de overlay visual para destacar elementos UI.
    
    Cria janelas transparentes sobrepostas para destacar elementos
    da interface com retângulos coloridos durante a inspeção.
    """
    
    def __init__(self):
        """
        Inicializa o sistema de overlay.
        
        Configura estruturas para gerenciar janelas de overlay
        e estado do sistema de destaque visual.
        """
        self.overlay_windows: List[tk.Toplevel] = []
        self.root = None
        self.is_active = False
    
    def initialize(self) -> bool:
        """
        Inicializa o sistema de overlay Tkinter.
        
        Returns:
            bool: True se inicialização bem-sucedida, False caso contrário.
            
        Raises:
            Exception: Se houver erro na inicialização do Tkinter.
        """
        if not PIL_AVAILABLE:
            return False
        
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Esconde a janela principal
            self.is_active = True
            return True
        except Exception as e:
            print(f"❌ Erro ao inicializar overlay: {e}")
            return False
    
    def highlight_element(self, element: Any, color: str = "red", width: int = 3, 
                         duration: float = 2.0) -> bool:
        """
        Destaca um elemento com retângulo colorido sobreposto.
        
        Args:
            element: Elemento UI a ser destacado.
            color: Cor do retângulo de destaque.
            width: Largura da borda do retângulo.
            duration: Duração do destaque em segundos (0 = permanente).
            
        Returns:
            bool: True se destaque criado com sucesso, False caso contrário.
            
        Raises:
            Exception: Se houver erro na criação do overlay.
        """
        if not self.is_active or not self.root:
            return False
        
        try:
            # Limpa overlays anteriores
            self.clear_overlays()
            
            # Obtém retângulo do elemento
            rect = element.rectangle()
            
            # Cria janela de overlay
            overlay = tk.Toplevel(self.root)
            overlay.overrideredirect(True)  # Remove decorações
            overlay.attributes('-topmost', True)  # Sempre no topo
            overlay.attributes('-transparentcolor', 'white')  # Fundo transparente
            
            # Posiciona e dimensiona
            overlay.geometry(f"{rect.width() + width*2}x{rect.height() + width*2}+{rect.left - width}+{rect.top - width}")
            
            # Cria canvas para desenhar retângulo
            canvas = tk.Canvas(overlay, highlightthickness=0, bg='white')
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Desenha retângulo
            canvas.create_rectangle(
                width, width, 
                rect.width() + width, rect.height() + width,
                outline=color, width=width, fill=''
            )
            
            # Adiciona à lista
            self.overlay_windows.append(overlay)
            
            # Remove automaticamente após duração
            if duration > 0:
                self.root.after(int(duration * 1000), lambda: self.remove_overlay(overlay))
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao destacar elemento: {e}")
            return False
    
    def remove_overlay(self, overlay: tk.Toplevel):
        """
        Remove um overlay específico da tela.
        
        Args:
            overlay: Janela de overlay a ser removida.
        """
        try:
            if overlay in self.overlay_windows:
                self.overlay_windows.remove(overlay)
            overlay.destroy()
        except Exception:
            pass
    
    def clear_overlays(self):
        """
        Remove todos os overlays ativos da tela.
        
        Limpa a lista de overlays e destroi todas as janelas.
        """
        for overlay in self.overlay_windows.copy():
            self.remove_overlay(overlay)
    
    def destroy(self):
        """
        Destroi completamente o sistema de overlay.
        
        Remove todos os overlays e finaliza o sistema Tkinter.
        """
        try:
            self.clear_overlays()
            if self.root:
                self.root.destroy()
            self.is_active = False
        except Exception:
            pass


class NavigationAssistant:
    """
    Assistente para navegação interativa em elementos UI.
    
    Fornece funcionalidades de navegação assistida com destaque visual,
    captura de eventos de mouse/teclado e gravação de caminhos de navegação.
    """
    
    def __init__(self, inspector):
        """
        Inicializa o assistente de navegação.
        
        Args:
            inspector: Instância do inspetor principal.
            
        Raises:
            ValueError: Se inspector for None.
        """
        if inspector is None:
            raise ValueError("Inspector não pode ser None")
            
        self.inspector = inspector
        self.overlay = OverlayWindow()
        self.navigation_path = NavigationPath()
        self.mouse_listener = None
        self.keyboard_listener = None
        self.is_recording = False
        self.current_highlighted_element = None
        
        # Configurações de destaque
        self.highlight_color = "red"
        self.highlight_width = 3
        self.highlight_duration = 0  # 0 = permanente até próximo highlight
        
        # Callbacks para eventos
        self.on_element_selected: Optional[Callable] = None
        self.on_navigation_step: Optional[Callable] = None
    
    def start(self) -> bool:
        """
        Inicia o assistente de navegação interativa.
        
        Inicializa o sistema de overlay, listeners de mouse/teclado
        e começa a gravação do caminho de navegação.
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário.
            
        Raises:
            Exception: Se houver erro na inicialização dos componentes.
        """
        try:
            print("🚀 Iniciando Assistente de Navegação...")
            
            # Inicializa overlay
            if not self.overlay.initialize():
                print("⚠️ Overlay não disponível, continuando sem destaque visual")
            
            # Inicia listeners se disponível
            if PYNPUT_AVAILABLE:
                self.start_mouse_listener()
                self.start_keyboard_listener()
            
            self.is_recording = True
            print("✅ Assistente iniciado!")
            print("💡 Dicas:")
            print("   - Clique em elementos para navegar")
            print("   - Pressione 'h' para destacar elemento sob o mouse")
            print("   - Pressione 'p' para imprimir caminho atual")
            print("   - Pressione 'ESC' para parar")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar assistente: {e}")
            return False
    
    def stop(self):
        """Para o assistente de navegação."""
        try:
            print("🛑 Parando Assistente de Navegação...")
            
            self.is_recording = False
            
            # Para listeners
            if self.mouse_listener:
                self.mouse_listener.stop()
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            
            # Destroi overlay
            self.overlay.destroy()
            
            print("✅ Assistente parado!")
            
        except Exception as e:
            print(f"❌ Erro ao parar assistente: {e}")
    
    def start_mouse_listener(self):
        """Inicia listener do mouse."""
        if not PYNPUT_AVAILABLE:
            return
        
        def on_click(x, y, button, pressed):
            if not self.is_recording or not pressed:
                return
            
            try:
                # Encontra elemento na posição do clique
                element = self.find_element_at_position(x, y)
                if element:
                    self.on_element_clicked(element, (x, y))
            except Exception as e:
                print(f"❌ Erro no clique: {e}")
        
        def on_move(x, y):
            if not self.is_recording:
                return
            
            # Implementar highlight on hover se necessário
            pass
        
        self.mouse_listener = mouse.Listener(
            on_click=on_click,
            on_move=on_move
        )
        self.mouse_listener.start()
    
    def start_keyboard_listener(self):
        """Inicia listener do teclado."""
        if not PYNPUT_AVAILABLE:
            return
        
        def on_press(key):
            if not self.is_recording:
                return
            
            try:
                if key == keyboard.Key.esc:
                    self.stop()
                elif hasattr(key, 'char'):
                    if key.char == 'h':
                        self.highlight_element_under_mouse()
                    elif key.char == 'p':
                        print(self.navigation_path.get_path_summary())
                    elif key.char == 'c':
                        self.overlay.clear_overlays()
                    elif key.char == 's':
                        self.save_navigation_path()
            except Exception as e:
                print(f"❌ Erro no teclado: {e}")
        
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()
    
    def find_element_at_position(self, x: int, y: int) -> Optional[Any]:
        """Encontra elemento na posição especificada."""
        try:
            if not self.inspector.current_window:
                return None
            
            # Usa PyWinAuto para encontrar elemento na posição
            from pywinauto import findwindows
            
            # Encontra janela na posição
            hwnd = win32gui.WindowFromPoint((x, y))
            if not hwnd:
                return None
            
            # Tenta conectar ao elemento
            try:
                app = Application().connect(handle=hwnd)
                element = app.window(handle=hwnd)
                return element if element.exists() else None
            except:
                # Fallback: busca na árvore atual
                return self.find_element_in_tree_at_position(self.inspector.current_window, x, y)
                
        except Exception as e:
            print(f"❌ Erro ao encontrar elemento: {e}")
            return None
    
    def find_element_in_tree_at_position(self, parent: Any, x: int, y: int, 
                                       depth: int = 0, max_depth: int = 5) -> Optional[Any]:
        """Busca elemento na árvore que contém a posição especificada."""
        try:
            if depth > max_depth:
                return None
            
            # Verifica se a posição está dentro do elemento atual
            rect = parent.rectangle()
            if not (rect.left <= x <= rect.right and rect.top <= y <= rect.bottom):
                return None
            
            # Busca nos filhos (do mais específico para o mais geral)
            try:
                children = parent.children()
                for child in children:
                    result = self.find_element_in_tree_at_position(child, x, y, depth + 1, max_depth)
                    if result:
                        return result
            except:
                pass
            
            # Se nenhum filho contém a posição, retorna o elemento atual
            return parent
            
        except Exception:
            return None
    
    def on_element_clicked(self, element: Any, coordinates: Tuple[int, int]):
        """Callback quando um elemento é clicado."""
        try:
            # Adiciona ao caminho de navegação
            self.navigation_path.add_step(element, "click", coordinates)
            
            # Destaca o elemento
            self.highlight_element(element)
            
            # Imprime informações do elemento
            self.print_element_info(element)
            
            # Atualiza árvore se necessário
            if self.on_navigation_step:
                self.on_navigation_step(element)
            
            # Callback personalizado
            if self.on_element_selected:
                self.on_element_selected(element, coordinates)
                
        except Exception as e:
            print(f"❌ Erro ao processar clique: {e}")
    
    def highlight_element(self, element: Any, color: Optional[str] = None) -> bool:
        """Destaca um elemento."""
        try:
            color = color or self.highlight_color
            success = self.overlay.highlight_element(
                element, 
                color=color, 
                width=self.highlight_width,
                duration=self.highlight_duration
            )
            
            if success:
                self.current_highlighted_element = element
            
            return success
            
        except Exception as e:
            print(f"❌ Erro ao destacar elemento: {e}")
            return False
    
    def highlight_element_under_mouse(self):
        """Destaca elemento sob o cursor do mouse."""
        try:
            if not PYNPUT_AVAILABLE:
                print("⚠️ Pynput não disponível")
                return
            
            # Obtém posição do mouse
            x, y = win32gui.GetCursorPos()
            
            # Encontra elemento
            element = self.find_element_at_position(x, y)
            if element:
                self.highlight_element(element, color="blue")
                self.print_element_info(element, prefix="🔍 Elemento sob o mouse:")
            else:
                print("❌ Nenhum elemento encontrado sob o mouse")
                
        except Exception as e:
            print(f"❌ Erro ao destacar elemento sob mouse: {e}")
    
    def print_element_info(self, element: Any, prefix: str = "🎯 Elemento selecionado:"):
        """Imprime informações detalhadas do elemento."""
        try:
            print(f"\n{prefix}")
            print("-" * 50)
            
            name = element.window_text() or "[No Name]"
            class_name = element.class_name() or "[No Class]"
            control_type = getattr(element.element_info, 'control_type', 'Unknown')
            auto_id = getattr(element.element_info, 'automation_id', '') or "[No AutoID]"
            rect = element.rectangle()
            
            print(f"📝 Name: {name}")
            print(f"🏗️ Class: {class_name}")
            print(f"🎯 Type: {control_type}")
            print(f"🆔 AutoID: {auto_id}")
            print(f"📐 Rectangle: ({rect.left}, {rect.top}, {rect.width()}, {rect.height()})")
            print(f"👁️ Visible: {element.is_visible()}")
            print(f"✋ Enabled: {element.is_enabled()}")
            print(f"🔗 Handle: 0x{element.handle:08X}")
            
            # Mostra caminho na árvore
            path = self.get_element_path(element)
            if path:
                print(f"📍 Caminho: {' → '.join(path)}")
            
        except Exception as e:
            print(f"❌ Erro ao imprimir info: {e}")
    
    def get_element_path(self, element: Any) -> List[str]:
        """Obtém caminho do elemento na árvore."""
        try:
            path = []
            current = element
            
            # Sobe na hierarquia até a janela principal
            while current and hasattr(current, 'parent'):
                try:
                    name = current.window_text() or current.class_name() or "Unknown"
                    control_type = getattr(current.element_info, 'control_type', '')
                    
                    if control_type:
                        path.insert(0, f"{name} ({control_type})")
                    else:
                        path.insert(0, name)
                    
                    # Tenta obter pai
                    try:
                        current = current.parent()
                    except:
                        break
                        
                except:
                    break
            
            return path
            
        except Exception as e:
            print(f"❌ Erro ao obter caminho: {e}")
            return []
    
    def save_navigation_path(self):
        """Salva o caminho de navegação atual."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"navigation_path_{timestamp}.json"
            filepath = self.inspector.output_dir / filename
            
            if self.navigation_path.export_to_file(str(filepath)):
                print(f"✅ Caminho salvo em: {filepath}")
            else:
                print("❌ Erro ao salvar caminho")
                
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")


class UIElementInspectorAdvanced:
    """Versão avançada do inspetor com navegação assistida."""
    
    def __init__(self):
        """Inicializa o inspetor avançado."""
        self.current_app: Optional[Application] = None
        self.current_window: Optional[Any] = None
        self.output_dir = Path("ui_inspector_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configurações
        self.max_depth = 5
        self.export_format = "txt"
        
        # Assistente de navegação
        self.navigation_assistant = NavigationAssistant(self)
        
        # Configurar callbacks
        self.navigation_assistant.on_navigation_step = self.on_navigation_step
        self.navigation_assistant.on_element_selected = self.on_element_selected
        
        print("🔍 UI Element Inspector Advanced inicializado")
        print(f"📁 Diretório de saída: {self.output_dir.absolute()}")
    
    def connect_to_application(self, process_name: Optional[str] = None, 
                             window_title: Optional[str] = None, 
                             handle: Optional[int] = None) -> bool:
        """Conecta a uma aplicação."""
        try:
            if handle is not None:
                print(f"🔗 Conectando via handle: 0x{handle:08X}")
                self.current_app = Application().connect(handle=handle)
                self.current_window = self.current_app.window(handle=handle)
                
            elif process_name is not None:
                print(f"🔗 Conectando ao processo: {process_name}")
                self.current_app = Application().connect(process=process_name)
                self.current_window = self.current_app.top_window()
                
            elif window_title is not None:
                print(f"🔗 Conectando à janela: {window_title}")
                self.current_app = Application().connect(title=window_title)
                self.current_window = self.current_app.window(title=window_title)
                
            else:
                print("❌ Especifique process_name, window_title ou handle")
                return False
            
            if self.current_window and self.current_window.exists():
                window_text = self.current_window.window_text() or "[No Title]"
                class_name = self.current_window.class_name() or "[No Class]"
                
                print(f"✅ Conectado com sucesso!")
                print(f"📋 Janela: {window_text}")
                print(f"🏗️ Classe: {class_name}")
                print(f"🔗 Handle: 0x{self.current_window.handle:08X}")
                return True
            else:
                print("❌ Falha ao conectar")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    def start_assisted_navigation(self) -> bool:
        """Inicia navegação assistida."""
        if not self.current_window:
            print("❌ Conecte a uma aplicação primeiro")
            return False
        
        return self.navigation_assistant.start()
    
    def stop_assisted_navigation(self):
        """Para navegação assistida."""
        self.navigation_assistant.stop()
    
    def on_navigation_step(self, element: Any):
        """Callback chamado a cada passo da navegação."""
        try:
            # Atualiza árvore em tempo real (opcional)
            print(f"\n🔄 Atualizando árvore para elemento: {element.window_text() or '[No Name]'}")
            
            # Você pode implementar atualização da árvore aqui
            # self.print_element_tree_around(element)
            
        except Exception as e:
            print(f"❌ Erro no callback de navegação: {e}")
    
    def on_element_selected(self, element: Any, coordinates: Tuple[int, int]):
        """Callback chamado quando um elemento é selecionado."""
        try:
            # Implementar ações personalizadas aqui
            pass
        except Exception as e:
            print(f"❌ Erro no callback de seleção: {e}")
    
    def print_element_tree_around(self, element: Any, levels_up: int = 2, levels_down: int = 2):
        """Imprime árvore ao redor de um elemento específico."""
        try:
            print(f"\n🌳 ÁRVORE AO REDOR DO ELEMENTO")
            print("=" * 60)
            
            # Encontra elemento pai alguns níveis acima
            current = element
            for _ in range(levels_up):
                try:
                    parent = current.parent()
                    if parent:
                        current = parent
                    else:
                        break
                except:
                    break
            
            # Imprime árvore a partir do pai
            self._print_element_recursive_highlight(current, target_element=element, 
                                                  depth=0, max_depth=levels_up + levels_down)
            
        except Exception as e:
            print(f"❌ Erro ao imprimir árvore ao redor: {e}")
    
    def _print_element_recursive_highlight(self, element: Any, target_element: Any,
                                         depth: int = 0, max_depth: int = 5) -> None:
        """Imprime elemento recursivamente destacando o alvo."""
        try:
            if depth > max_depth:
                return
            
            indent = "  " * depth
            
            # Verifica se é o elemento alvo
            is_target = (element.handle == target_element.handle)
            prefix = "🎯 " if is_target else ("├── " if depth > 0 else "🏠 ")
            
            # Informações básicas
            try:
                window_text = element.window_text() or "[No Text]"
                class_name = element.class_name() or "[No Class]"
                control_type = getattr(element.element_info, 'control_type', 'Unknown')
                auto_id = getattr(element.element_info, 'automation_id', '') or "[No AutoID]"
                
                if is_target:
                    print(f"{indent}{prefix}>>> {window_text} <<<")
                else:
                    print(f"{indent}{prefix}{window_text}")
                
                print(f"{indent}    📝 Class: {class_name}")
                print(f"{indent}    🎯 Type: {control_type}")
                print(f"{indent}    🆔 AutoID: {auto_id}")
                
                if is_target:
                    rect = element.rectangle()
                    print(f"{indent}    📐 Rect: ({rect.left}, {rect.top}, {rect.width()}, {rect.height()})")
                    print(f"{indent}    👁️ Visible: {element.is_visible()}")
                    print(f"{indent}    ✋ Enabled: {element.is_enabled()}")
                
                print()
                
            except Exception as e:
                print(f"{indent}{prefix}[Erro ao obter info: {e}]")
            
            # Processa filhos
            try:
                children = element.children()
                for child in children:
                    self._print_element_recursive_highlight(child, target_element, depth + 1, max_depth)
            except Exception:
                pass
                
        except Exception as e:
            print(f"Erro no elemento (depth {depth}): {e}")
    
    def list_available_windows(self) -> List[Dict[str, Any]]:
        """Lista janelas disponíveis."""
        try:
            print("🔍 Listando janelas disponíveis...")
            
            windows = []
            desktop = Desktop(backend="win32")
            
            for window in desktop.windows():
                try:
                    window_text = window.window_text() or ""
                    if window.is_visible() and window_text.strip():
                        rect = window.rectangle()
                        window_info = {
                            'title': window_text,
                            'class_name': window.class_name() or "[No Class]",
                            'handle': f"0x{window.handle:08X}",
                            'process_id': window.process_id(),
                            'rectangle': {
                                'left': rect.left,
                                'top': rect.top,
                                'width': rect.width(),
                                'height': rect.height()
                            },
                            'is_enabled': window.is_enabled(),
                            'is_visible': window.is_visible()
                        }
                        windows.append(window_info)
                except Exception:
                    continue
            
            windows.sort(key=lambda x: x['title'].lower())
            
            print(f"📋 Encontradas {len(windows)} janelas:")
            for i, win in enumerate(windows):
                title = win['title'][:50] if len(win['title']) > 50 else win['title']
                class_name = win['class_name'][:30] if len(win['class_name']) > 30 else win['class_name']
                print(f"  {i+1:2d}. {title:<50} | {class_name:<30} | {win['handle']}")
            
            return windows
            
        except Exception as e:
            print(f"❌ Erro ao listar janelas: {e}")
            return []
    
    def interactive_mode_advanced(self) -> None:
        """Modo interativo avançado com navegação assistida."""
        print("🎮 MODO INTERATIVO AVANÇADO - Navegação Assistida")
        print("=" * 70)
        print("Comandos disponíveis:")
        print("  list         - Lista janelas disponíveis")
        print("  connect <n>  - Conecta à janela número n da lista")
        print("  start        - Inicia navegação assistida")
        print("  stop         - Para navegação assistida")
        print("  highlight <name> - Destaca elemento por nome")
        print("  path         - Mostra caminho atual")
        print("  save         - Salva caminho de navegação")
        print("  clear        - Limpa overlays")
        print("  info         - Mostra informações da janela atual")
        print("  help         - Mostra esta ajuda")
        print("  quit         - Sai do programa")
        print("-" * 70)
        
        windows_list: List[Dict[str, Any]] = []
        
        while True:
            try:
                command = input("\n🔍 Inspector Advanced> ").strip().lower()
                
                if command in ["quit", "exit"]:
                    self.stop_assisted_navigation()
                    print("👋 Saindo...")
                    break
                
                elif command == "help":
                    print("📚 Comandos disponíveis:")
                    print("  list, connect <n>, start, stop")
                    print("  highlight <name>, path, save, clear")
                    print("  info, help, quit")
                
                elif command == "list":
                    windows_list = self.list_available_windows()
                
                elif command.startswith("connect "):
                    try:
                        parts = command.split()
                        if len(parts) >= 2:
                            index = int(parts[1]) - 1
                            if 0 <= index < len(windows_list):
                                window_info = windows_list[index]
                                handle = int(window_info['handle'], 16)
                                self.connect_to_application(handle=handle)
                            else:
                                print("❌ Índice inválido")
                        else:
                            print("❌ Uso: connect <número>")
                    except (ValueError, IndexError):
                        print("❌ Uso: connect <número>")
                
                elif command == "start":
                    if self.start_assisted_navigation():
                        print("🚀 Navegação assistida iniciada!")
                        print("💡 Clique em elementos para navegar")
                        print("💡 Pressione 'h' para destacar elemento sob mouse")
                        print("💡 Pressione 'ESC' para parar")
                    else:
                        print("❌ Falha ao iniciar navegação assistida")
                
                elif command == "stop":
                    self.stop_assisted_navigation()
                    print("🛑 Navegação assistida parada")
                
                elif command.startswith("highlight "):
                    try:
                        parts = command.split(maxsplit=1)
                        if len(parts) >= 2:
                            element_name = parts[1]
                            # Implementar busca e highlight por nome
                            print(f"🔍 Buscando elemento: {element_name}")
                            # self.highlight_element_by_name(element_name)
                        else:
                            print("❌ Uso: highlight <nome_do_elemento>")
                    except IndexError:
                        print("❌ Uso: highlight <nome_do_elemento>")
                
                elif command == "path":
                    print(self.navigation_assistant.navigation_path.get_path_summary())
                
                elif command == "save":
                    self.navigation_assistant.save_navigation_path()
                
                elif command == "clear":
                    self.navigation_assistant.overlay.clear_overlays()
                    print("✅ Overlays limpos")
                
                elif command == "info":
                    if self.current_window:
                        window_text = self.current_window.window_text() or "[No Title]"
                        class_name = self.current_window.class_name() or "[No Class]"
                        rect = self.current_window.rectangle()
                        
                        print(f"📋 Janela atual: {window_text}")
                        print(f"🏗️ Classe: {class_name}")
                        print(f"🔗 Handle: 0x{self.current_window.handle:08X}")
                        print(f"📐 Rectangle: {rect}")
                        print(f"🎯 Navegação ativa: {self.navigation_assistant.is_recording}")
                        print(f"📍 Passos registrados: {len(self.navigation_assistant.navigation_path.steps)}")
                    else:
                        print("❌ Nenhuma janela conectada")
                
                elif command == "":
                    continue
                
                else:
                    print(f"❌ Comando desconhecido: {command}")
                    print("💡 Digite 'help' para ver os comandos disponíveis")
                
            except KeyboardInterrupt:
                self.stop_assisted_navigation()
                print("\n👋 Saindo...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="UI Element Inspector Advanced - Navegação Assistida",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python ui_inspector_advanced.py --interactive
  python ui_inspector_advanced.py --assisted --title Calculator
  python ui_inspector_advanced.py --list
        """
    )
    
    # Argumentos de conexão
    parser.add_argument("--process", help="Nome do processo")
    parser.add_argument("--title", help="Título da janela")
    parser.add_argument("--handle", help="Handle da janela")
    
    # Argumentos de modo
    parser.add_argument("--interactive", action="store_true", help="Modo interativo avançado")
    parser.add_argument("--assisted", action="store_true", help="Inicia navegação assistida")
    parser.add_argument("--list", action="store_true", help="Lista janelas disponíveis")
    
    args = parser.parse_args()
    
    # Cria inspetor avançado
    inspector = UIElementInspectorAdvanced()
    
    try:
        # Lista janelas
        if args.list:
            inspector.list_available_windows()
            return
        
        # Conecta à aplicação se especificado
        if args.handle or args.process or args.title:
            connected = False
            if args.handle:
                handle_value = int(args.handle, 16) if args.handle.startswith("0x") else int(args.handle)
                connected = inspector.connect_to_application(handle=handle_value)
            elif args.process:
                connected = inspector.connect_to_application(process_name=args.process)
            elif args.title:
                connected = inspector.connect_to_application(window_title=args.title)
            
            if not connected:
                print("❌ Falha ao conectar à aplicação")
                return
        
        # Modo interativo
        if args.interactive:
            inspector.interactive_mode_advanced()
            return
        
        # Navegação assistida
        if args.assisted:
            if not inspector.current_window:
                print("❌ Especifique uma aplicação para conectar")
                return
            
            if inspector.start_assisted_navigation():
                print("🚀 Navegação assistida iniciada!")
                print("💡 Pressione ESC para parar")
                
                # Mantém o programa rodando
                try:
                    while inspector.navigation_assistant.is_recording:
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    pass
                
                inspector.stop_assisted_navigation()
            return
        
        # Se nenhum modo específico, inicia interativo
        inspector.interactive_mode_advanced()
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()