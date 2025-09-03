# Módulo de Logging

Este módulo fornece funcionalidades para registro de logs em diferentes bancos de dados, permitindo o acompanhamento centralizado das operações do sistema de RPA para a FIDI.

> **Nota**: A partir da versão 1.2.0, este módulo utiliza apenas a biblioteca `oracledb` para conexões Oracle, removendo a dependência do `cx_Oracle`.

## Módulos Disponíveis

### logger.py

Implementa funções para registro de logs em diferentes bancos de dados:

1. **registrar_log_banco**: Wrapper genérico para registrar log no banco, detectando o tipo de conexão
   - Detecta automaticamente o tipo de conexão (Oracle via oracledb, PostgreSQL, SQL Server)
   - Encaminha para a função específica de registro de log

2. **registrar_log_rpa_oracle**: Registra log no banco de dados Oracle
   - Utiliza procedure FIDI.inserir_log_execucao
   - Usa oracledb para manipulação de tipos CLOB

3. **registrar_log_rpa_postgres**: Registra log no banco de dados PostgreSQL
   - Insere diretamente na tabela logexecucaorpa

4. **registrar_log_rpa_sqlserver**: Registra log no banco de dados SQL Server
   - Tenta usar procedure inserir_log_execucao se existir
   - Caso contrário, faz inserção direta na tabela logexecucaorpa

## Como Usar

```python
import pyodbc
from fidi_common_libraries.utils.logger import registrar_log_banco
from fidi_common_libraries.data.db_data import DatabaseConfig

# Configuração do banco de dados
db_config = DatabaseConfig.from_env('RPA_')
conn = pyodbc.connect(db_config.connection_string)

# Registrar log
registrar_log_banco(
    conn=conn,
    ambiente="HML",
    produto="FIDI-ferias",
    versao="1.0.0",
    nivel="INFO",
    modulo="hub_aws",
    processo="SQS_Message_Processing",
    acao="processar_mensagem",
    lote="LOTE_20230715",
    mensagem="Mensagem processada com sucesso",
    usuario="sistema",
    status_execucao="SUCESSO",
    hostname="servidor01",
    ip_origem="192.168.1.100",
    detalhes={"id_mensagem": "123456", "tipo": "monitor_RM"},
    correlation_id="abc-123-xyz",
    duracao_ms=1500
)
```

## Tabela de Banco de Dados

Os logs são armazenados na tabela `logexecucaorpa` com a seguinte estrutura:

- `id`: Identificador único do log
- `datahora`: Data e hora do log
- `ambiente`: Ambiente (DEV, HML, PROD)
- `produto`: Nome do produto (FIDI-ferias, FIDI-pos-folha)
- `versao`: Versão do produto
- `nivel`: Nível do log (INFO, ERROR, WARNING, DEBUG)
- `modulo`: Módulo que gerou o log
- `processo`: Processo que gerou o log
- `acao`: Ação executada
- `lote`: Identificador de lote
- `mensagem`: Mensagem do log
- `usuario`: Usuário que executou a ação
- `statusexecucao`: Status da execução (SUCESSO, ERRO, PENDENTE, CANCELADO)
- `detalhes`: Detalhes adicionais em formato JSON
- `hostname`: Nome da máquina
- `iporigem`: IP da máquina
- `correlationid`: ID de correlação para rastreamento
- `duracao_ms`: Duração em milissegundos
- `categoria`: Categoria do log (opcional)