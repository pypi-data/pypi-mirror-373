# Módulo de Configuração

Este módulo fornece funcionalidades para gerenciamento de configurações e parâmetros do sistema de RPA para a FIDI.

## Módulos Disponíveis

### parametros.py

Implementa uma interface centralizada para gerenciamento de parâmetros armazenados no banco de dados:

1. **Classe Parametros**: Gerenciador de parâmetros do sistema
   - `get_parametro(nome, default=None)`: Obtém o valor de um parâmetro
   - `get_parametros_por_grupo(agrupamento)`: Obtém todos os parâmetros de um agrupamento
   - `atualizar_parametro(nome, valor)`: Atualiza o valor de um parâmetro
   - `limpar_cache(parametro=None)`: Limpa o cache de parâmetros

2. **Características principais**:
   - Cache com TTL configurável para reduzir consultas ao banco
   - Conversão automática de tipos (string, int, float, bool, json, csv, date)
   - Tratamento especial para parâmetros sensíveis (não exibidos em logs)
   - Agrupamento de parâmetros para organização lógica

### ScriptsDB_Datametria_Parametros.sql

Script SQL para criação e configuração dos objetos de banco de dados necessários para o módulo de parâmetros:

1. **Objetos criados**:
   - Tabela `parametrosrpa`: Armazena os parâmetros do sistema
   - Stored procedures para gerenciamento de parâmetros:
     - `sp_obter_parametro`: Obtém um parâmetro específico
     - `sp_obter_parametros_por_grupo`: Obtém todos os parâmetros de um grupo
     - `sp_atualizar_parametro`: Atualiza o valor de um parâmetro
   - View `vw_parametros_publicos`: Exibe apenas parâmetros não sensíveis

2. **Dados iniciais**:
   - Parâmetros pré-configurados para diversos ambientes e produtos
   - Agrupamentos lógicos: TI, Negocio, Produto
   - Tipos de parâmetros: string, int, float, bool, json, csv

## Como Usar

```python
from fidi_common_libraries.config.parametros import Parametros

# Inicializar o gerenciador de parâmetros
params = Parametros(ambiente="HML", produto="FIDI-ferias")

# Obter um parâmetro
url_api = params.get_parametro("URL_API", default="https://api.exemplo.com")

# Obter parâmetros por grupo
config_email = params.get_parametros_por_grupo("Email")

# Atualizar um parâmetro
params.atualizar_parametro("TIMEOUT_API", 30)

# Limpar o cache
params.limpar_cache()
```

## Tabela de Banco de Dados

Os parâmetros são armazenados na tabela `parametrosrpa` com a seguinte estrutura:

- `id`: Identificador único do parâmetro
- `ambiente`: Ambiente (DEV, HML, PROD)
- `produto`: Nome do produto (FIDI-ferias, FIDI-pos-folha)
- `parametro`: Nome do parâmetro
- `agrupamento`: Grupo do parâmetro (opcional)
- `valor`: Valor do parâmetro
- `tipo_valor`: Tipo do valor (string, int, float, bool, json, csv, date)
- `is_sensivel`: Indica se o parâmetro é sensível (não deve ser exibido em logs)
- `ativo`: Indica se o parâmetro está ativo
- `descricao`: Descrição do parâmetro
- `criado_em`: Data de criação
- `atualizado_em`: Data da última atualização
- `versao`: Versão do parâmetro

## Categorias de Parâmetros

O script SQL pré-configura parâmetros nas seguintes categorias:

- **TI**: Configurações técnicas (caminhos, servidores, credenciais)
- **Negocio**: Configurações específicas do negócio (filiais, organizações)
- **Produto**: Configurações do produto (timeouts, retries, processamento)