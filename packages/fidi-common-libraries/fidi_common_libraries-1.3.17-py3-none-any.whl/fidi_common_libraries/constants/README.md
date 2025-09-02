# Módulo de Constantes

Este módulo centraliza as constantes utilizadas em todo o projeto de RPA para a FIDI., facilitando a manutenção e garantindo consistência.

## Módulos Disponíveis

### status.py

Contém constantes e funções relacionadas aos status de execução utilizados no projeto:

1. **DBStatus**: Status para o banco de dados (tabela processosrpa)
   - `NOVO`, `AGRUPADO`, `PROCESSADO`, `VALIDADO`, `INTEGRADO`, `BAIXADO`, `FINALIZADO`

2. **LogStatus**: Status para logs (tabela logexecucaorpa)
   - `SUCESSO`, `ERRO`, `PENDENTE`, `CANCELADO`

3. **HubStatus**: Status para comunicação com o Hub AWS
   - `Sucesso`, `Sem_Itens`, `Pendente`, `Erro`

4. **Mapeamentos entre status**:
   - `HUB_TO_LOG_MAP`: Mapeamento de status do Hub para status de log
   - `LOG_TO_HUB_MAP`: Mapeamento de status de log para status do Hub
   - `DB_TO_LOG_MAP`: Mapeamento de status do banco para status de log

5. **Função de conversão**:
   - `convert_status(status, source_type, target_type)`: Converte um status de um tipo para outro

## Como Usar

```python
from fidi_common_libraries.constants.status import DBStatus, LogStatus, HubStatus, convert_status

# Usar constantes diretamente
db_status = DBStatus.AGRUPADO
log_status = LogStatus.SUCESSO
hub_status = HubStatus.PENDENTE

# Verificar se um status é válido
if status in DBStatus.values():
    print("Status de banco válido")

# Converter entre tipos de status
log_status = convert_status(hub_status, 'hub', 'log')
```