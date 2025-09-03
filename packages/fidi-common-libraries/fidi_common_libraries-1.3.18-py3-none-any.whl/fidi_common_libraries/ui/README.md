# Módulo de Automação de UI

Este módulo fornece uma camada de abstração robusta sobre o Pywinauto para automação de interfaces gráficas do sistema RM, seguindo as melhores práticas de automação de UI.

## Estrutura do Módulo

```
ui/
├── config/           # Configurações para automação de UI
├── core/             # Componentes principais de automação
├── exceptions/       # Exceções específicas para operações de UI
├── locators/         # Mapeamento de elementos da interface
└── utils/            # Utilitários para automação
```

## Componentes Principais

### RMApplication

Gerencia a conexão com a aplicação RM, fornecendo métodos para conectar, reconectar e interagir com a aplicação.

```python
from fidi_common_libraries.ui import RMApplication

# Inicializar e conectar à aplicação
app = RMApplication()
app.connect()

# Obter a janela principal
main_window = app.get_main_window()
```

### ElementFinder

Localiza elementos na interface com estratégias robustas de busca e fallback.

```python
from fidi_common_libraries.ui import ElementFinder

finder = ElementFinder()

# Encontrar elemento com critérios primários e fallback
button = finder.find_element(
    parent=main_window,
    primary_criteria={"title": "Salvar", "control_type": "Button"},
    fallback_criteria=[{"auto_id": "btnSave"}, {"class_name": "Button", "title": "Salvar"}]
)

# Verificar se elemento existe
exists = finder.element_exists(main_window, {"title": "Confirmar"})

# Aguardar elemento aparecer
dialog = finder.wait_for_element_to_appear(main_window, {"title": "Configurações"})
```

### UIInteractions

Fornece métodos seguros para interagir com elementos da interface.

```python
from fidi_common_libraries.ui import UIInteractions

interactions = UIInteractions()

# Clicar em um botão com segurança
interactions.safe_click(button)

# Digitar texto em um campo
interactions.safe_type_text(text_field, "Exemplo de texto")

# Selecionar item em dropdown
interactions.select_from_dropdown(dropdown, "Opção 2")

# Marcar/desmarcar checkbox
interactions.check_checkbox(checkbox, check=True)
```

### UIWaits

Implementa mecanismos de espera para sincronização com a interface.

```python
from fidi_common_libraries.ui import UIWaits

waits = UIWaits()

# Aguardar elemento ficar pronto
waits.wait_for_element_ready(button)

# Aguardar elemento ficar visível
waits.wait_for_element_visible(dialog)

# Aguardar condição personalizada
waits.wait_for_condition(lambda: button.is_enabled(), timeout=10)
```

## Tratamento de Exceções

O módulo fornece exceções específicas para diferentes tipos de falhas:

```python
from fidi_common_libraries.ui.exceptions import UIElementNotFoundError, UITimeoutError

try:
    # Código de automação
    pass
except UIElementNotFoundError as e:
    print(f"Elemento não encontrado: {e}")
except UITimeoutError as e:
    print(f"Timeout ao aguardar elemento: {e}")
```

## Configuração

As configurações de automação podem ser personalizadas:

```python
from fidi_common_libraries.ui.config import get_ui_config

# Obter configuração padrão
config = get_ui_config()

# Configuração via variáveis de ambiente:
# UI_DEFAULT_TIMEOUT=30
# RM_WINDOW_TITLE=Sistema RM
# RM_PROCESS_NAME=rm.exe
# UI_SCREENSHOT_ON_ERROR=true
# UI_LOG_LEVEL=INFO
```

## Captura de Screenshots

```python
from fidi_common_libraries.ui.utils import capture_screenshot

# Capturar screenshot manualmente
screenshot_path = capture_screenshot("tela_login")
```

## Validação

```python
from fidi_common_libraries.ui.utils import validate_text_input, validate_numeric_input

# Validar entrada de texto
validate_text_input("Exemplo", max_length=50)

# Validar entrada numérica
valor = validate_numeric_input("123.45", min_value=0, max_value=1000)
```