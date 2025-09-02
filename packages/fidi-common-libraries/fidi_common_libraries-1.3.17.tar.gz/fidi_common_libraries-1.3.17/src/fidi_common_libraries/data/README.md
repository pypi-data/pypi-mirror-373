# Módulo de Dados

Este módulo fornece funcionalidades para acesso a dados e operações de banco de dados para o sistema de RPA da FIDI.

## Módulos Disponíveis

### db_data.py

Implementa classes para operações de banco de dados multi-SGBD:

1. **DatabaseConfig**: Configuração de conexão com banco de dados
   - `connection_string`: Retorna string de conexão para pyodbc
   - `sqlalchemy_connection_string`: Retorna string de conexão para SQLAlchemy
   - `from_env(prefix)`: Cria configuração a partir de variáveis de ambiente

2. **DatabaseOperations**: Classe base para operações de banco de dados
   - `get_connection()`: Obtém conexão pyodbc
   - `get_sqlalchemy_engine()`: Obtém engine SQLAlchemy

3. **ProcessosRpaInserter**: Inserção de registros na tabela processosrpa
   - `insert(...)`: Insere um registro via procedure
   - `insert_batch(records)`: Insere múltiplos registros

4. **ProcessosRpaUpdater**: Atualização de registros na tabela processosrpa
   - `update(...)`: Atualiza um registro via procedure
   - `update_batch(records)`: Atualiza múltiplos registros

5. **DatabaseQuery**: Execução de consultas SQL com proteção contra SQL injection
   - `execute_query(query, params, result_type)`: Executa consulta e retorna resultados
   - `execute_query_single_value(query, params)`: Retorna um único valor
   - `execute_query_with_callback(query, params, callback)`: Processa resultados com callback

## Como Usar

```python
from fidi_common_libraries.data.db_data import DatabaseConfig, DatabaseQuery

# Configurar conexão com o banco de dados
db_config = DatabaseConfig.from_env('RPA_')

# Executar consulta SQL segura
query = DatabaseQuery(db_config)
results = query.execute_query(
    "SELECT * FROM processosrpa WHERE statusexecucao = :status",
    {"status": "NOVO"}
)

# Obter um único valor
count = query.execute_query_single_value(
    "SELECT COUNT(*) FROM processosrpa WHERE statusexecucao = :status",
    {"status": "NOVO"}
)
```

## Nota Importante

O módulo `parametros.py` foi movido para o pacote `config`. Para gerenciamento de parâmetros, utilize:

```python
from fidi_common_libraries.config.parametros import Parametros
```