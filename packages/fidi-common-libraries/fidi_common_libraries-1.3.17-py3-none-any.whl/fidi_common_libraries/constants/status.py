"""
Módulo de constantes para status de execução utilizados no projeto de RPA para a FIDI..

Este módulo centraliza todos os status de execução utilizados em diferentes
contextos do projeto, facilitando a manutenção e garantindo consistência.
Implementa classes para os diferentes tipos de status (banco de dados, logs, hub)
e mapeamentos entre eles, permitindo conversões consistentes.

Classes principais:
- DBStatus: Status para operações no banco de dados (tabela processosrpa)
- LogStatus: Status para logs de execução (tabela logexecucaorpa)
- HubStatus: Status para comunicação com o Hub AWS

Mapeamentos:
- HUB_TO_LOG_MAP: Mapeamento de status do Hub para status de log
- LOG_TO_HUB_MAP: Mapeamento de status de log para status do Hub
- DB_TO_LOG_MAP: Mapeamento de status do banco para status de log

Funções:
- convert_status: Converte um status de um tipo para outro
"""

from typing import List, Dict, Optional

# Status para banco de dados (processosrpa.statusexecucao)
class DBStatus:
    """
    Status para operações no banco de dados (tabela processosrpa).
    
    Esta classe define as constantes para os possíveis status de um registro
    na tabela processosrpa, representando o ciclo de vida de um processo RPA:
    
    - NOVO: Registro recém-criado, ainda não processado
    - AGRUPADO: Registro agrupado com outros para processamento em lote
    - PROCESSADO: Processamento inicial concluído
    - VALIDADO: Dados validados e prontos para integração
    - INTEGRADO: Integrado com sistema externo
    - BAIXADO: Arquivos ou documentos relacionados foram baixados
    - FINALIZADO: Processo completamente concluído
    """
    NOVO = "NOVO"
    AGRUPADO = "AGRUPADO"
    PROCESSADO = "PROCESSADO"
    VALIDADO = "VALIDADO"
    INTEGRADO = "INTEGRADO"
    BAIXADO = "BAIXADO"
    FINALIZADO = "FINALIZADO"
    
    @classmethod
    def values(cls) -> List[str]:
        """
        Retorna todos os valores de status válidos.
        
        Returns:
            Lista de strings com todos os status válidos para o banco de dados
        """
        return [cls.NOVO, cls.AGRUPADO, cls.PROCESSADO, cls.VALIDADO, 
                cls.INTEGRADO, cls.BAIXADO, cls.FINALIZADO]


# Status para logs (logexecucaorpa.statusexecucao)
class LogStatus:
    """
    Status para logs de execução (tabela logexecucaorpa).
    
    Esta classe define as constantes para os possíveis status de um registro
    de log na tabela logexecucaorpa, representando o resultado de uma operação:
    
    - SUCESSO: Operação concluída com sucesso
    - ERRO: Operação falhou devido a um erro
    - PENDENTE: Operação ainda está em andamento
    - CANCELADO: Operação foi cancelada manualmente ou por um processo
    """
    SUCESSO = "SUCESSO"
    ERRO = "ERRO"
    PENDENTE = "PENDENTE"
    CANCELADO = "CANCELADO"
    
    @classmethod
    def values(cls) -> List[str]:
        """
        Retorna todos os valores de status válidos para logs.
        
        Returns:
            Lista de strings com todos os status válidos para logs
        """
        return [cls.SUCESSO, cls.ERRO, cls.PENDENTE, cls.CANCELADO]


# Status para AWS Hub (STATUS_EXECUCAO)
class HubStatus:
    """
    Status para comunicação com o Hub AWS.
    
    Esta classe define as constantes para os possíveis status retornados
    pelos workers do Hub AWS, representando o resultado de uma tarefa:
    
    - SUCESSO: Tarefa concluída com sucesso
    - SEM_ITENS: Tarefa executada com sucesso, mas não encontrou itens para processar
    - PENDENTE: Tarefa ainda está em andamento ou aguardando processamento
    - ERRO: Tarefa falhou devido a um erro
    
    Nota: Estes status são utilizados na comunicação entre o Hub AWS e os
    serviços que o consomem, como Step Functions e Lambda.
    """
    SUCESSO = "Sucesso"
    SEM_ITENS = "Sem_Itens"
    PENDENTE = "Pendente"
    ERRO = "Erro"
    
    @classmethod
    def values(cls) -> List[str]:
        """
        Retorna todos os valores de status válidos para o Hub AWS.
        
        Returns:
            Lista de strings com todos os status válidos para o Hub AWS
        """
        return [cls.SUCESSO, cls.SEM_ITENS, cls.PENDENTE, cls.ERRO]


# Mapeamento entre status do Hub AWS e status de log
HUB_TO_LOG_MAP: Dict[str, str] = {
    HubStatus.SUCESSO: LogStatus.SUCESSO,
    HubStatus.SEM_ITENS: LogStatus.SUCESSO,  # Mapeado para SUCESSO para evitar problemas com constraint
    HubStatus.PENDENTE: LogStatus.PENDENTE,
    HubStatus.ERRO: LogStatus.ERRO
}
"""
Mapeamento de status do Hub AWS para status de log.

Este dicionário mapeia cada status do Hub AWS para seu equivalente no sistema de logs.
Nota: HubStatus.SEM_ITENS é mapeado para LogStatus.SUCESSO, pois a ausência de itens
não é considerada um erro, mas sim uma execução bem-sucedida sem resultados.
"""

# Mapeamento entre status de log e status do Hub AWS
LOG_TO_HUB_MAP: Dict[str, str] = {
    LogStatus.SUCESSO: HubStatus.SUCESSO,
    LogStatus.ERRO: HubStatus.ERRO,
    LogStatus.PENDENTE: HubStatus.PENDENTE,
    LogStatus.CANCELADO: HubStatus.ERRO  # Mapeado para Erro pois não há equivalente direto
}
"""
Mapeamento de status de log para status do Hub AWS.

Este dicionário mapeia cada status de log para seu equivalente no Hub AWS.
Nota: LogStatus.CANCELADO é mapeado para HubStatus.ERRO, pois não existe
um status equivalente no Hub AWS para operações canceladas.
"""

# Mapeamento entre status do banco e status de log
DB_TO_LOG_MAP: Dict[str, str] = {
    DBStatus.NOVO: LogStatus.PENDENTE,
    DBStatus.AGRUPADO: LogStatus.PENDENTE,
    DBStatus.PROCESSADO: LogStatus.SUCESSO,
    DBStatus.VALIDADO: LogStatus.SUCESSO,
    DBStatus.INTEGRADO: LogStatus.SUCESSO,
    DBStatus.BAIXADO: LogStatus.SUCESSO,
    DBStatus.FINALIZADO: LogStatus.SUCESSO
}
"""
Mapeamento de status do banco de dados para status de log.

Este dicionário mapeia cada status do banco de dados para seu equivalente no sistema de logs.
Os status iniciais (NOVO, AGRUPADO) são mapeados para PENDENTE, enquanto os demais
são mapeados para SUCESSO, indicando que o processo avançou com sucesso para aquela etapa.
"""

# Função auxiliar para converter entre diferentes tipos de status
def convert_status(status: str, source_type: str, target_type: str) -> str:
    """
    Converte um status de um tipo para outro utilizando os mapeamentos definidos.
    
    Esta função permite converter status entre os diferentes sistemas (banco de dados,
    logs, hub AWS), garantindo consistência nas conversões. Utiliza os mapeamentos
    HUB_TO_LOG_MAP, LOG_TO_HUB_MAP e DB_TO_LOG_MAP para realizar as conversões.
    
    Exemplos:
        >>> convert_status(HubStatus.SUCESSO, 'hub', 'log')
        'SUCESSO'
        >>> convert_status(DBStatus.NOVO, 'db', 'log')
        'PENDENTE'
    
    Args:
        status: O status a ser convertido
        source_type: O tipo de origem ('db', 'log', 'hub')
        target_type: O tipo de destino ('db', 'log', 'hub')
        
    Returns:
        O status convertido para o tipo de destino
        
    Raises:
        ValueError: Se o status não for válido ou se os tipos não forem válidos
    """
    if source_type == target_type:
        return status
        
    if source_type == 'hub' and target_type == 'log':
        if status not in HubStatus.values():
            raise ValueError(f"Status de hub inválido: {status}")
        return HUB_TO_LOG_MAP.get(status, LogStatus.ERRO)
        
    elif source_type == 'log' and target_type == 'hub':
        if status not in LogStatus.values():
            raise ValueError(f"Status de log inválido: {status}")
        return LOG_TO_HUB_MAP.get(status, HubStatus.ERRO)
        
    elif source_type == 'db' and target_type == 'log':
        if status not in DBStatus.values():
            raise ValueError(f"Status de banco inválido: {status}")
        return DB_TO_LOG_MAP.get(status, LogStatus.PENDENTE)
        
    else:
        raise ValueError(f"Conversão de {source_type} para {target_type} não suportada")