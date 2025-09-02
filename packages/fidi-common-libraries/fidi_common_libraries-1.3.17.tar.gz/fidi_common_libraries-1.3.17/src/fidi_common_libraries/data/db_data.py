"""
Módulo de acesso a dados para o sistema de RPA para a FIDI.

Este módulo implementa classes e funções para acesso a bancos de dados,
incluindo configuração de conexão, operações CRUD e consultas com proteção
contra SQL injection.

Classes principais:
- DatabaseConfig: Configuração de conexão com banco de dados
- DatabaseOperations: Classe base para operações de banco de dados
- ProcessosRpaInserter: Inserção de registros na tabela processosrpa
- ProcessosRpaUpdater: Atualização de registros na tabela processosrpa
- DatabaseQuery: Execução de consultas SQL com proteção contra SQL injection
- ProcedureExecutor: Execução de procedures com diferentes tipos de retorno
- ProcedureHelpers: Métodos auxiliares para cenários específicos de procedures
"""


import os
import pyodbc
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Union, TypeVar, Generic, Callable
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import SQLAlchemyError


class DatabaseConfig:
    """
    Configuração de conexão com banco de dados.
    
    Esta classe encapsula os parâmetros de conexão com um banco de dados SQL Server
    e fornece métodos para gerar strings de conexão para diferentes bibliotecas.
    Também suporta carregamento de configuração a partir de variáveis de ambiente.
    
    Attributes:
        server: Nome ou endereço do servidor de banco de dados
        database: Nome do banco de dados
        username: Nome de usuário para autenticação
        password: Senha para autenticação
    """
    
    def __init__(self, server: str, database: str, username: str, password: str):
        """
        Inicializa uma nova instância de DatabaseConfig.
        
        Args:
            server: Nome ou endereço do servidor de banco de dados
            database: Nome do banco de dados
            username: Nome de usuário para autenticação
            password: Senha para autenticação
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
    
    @property
    def connection_string(self) -> str:
        """
        Retorna a string de conexão ODBC para uso com pyodbc.
        
        Returns:
            String de conexão no formato ODBC para SQL Server
        """
        return (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={self.server};DATABASE={self.database};'
            f'UID={self.username};PWD={self.password};TrustServerCertificate=yes'
        )
    
    @property
    def sqlalchemy_connection_string(self) -> str:
        """
        Retorna a string de conexão para SQLAlchemy.
        
        Returns:
            String de conexão no formato SQLAlchemy para SQL Server
        """
        return (
            f'mssql+pyodbc://{self.username}:{self.password}@{self.server}'
            f'/{self.database}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
        )
    
    @classmethod
    def from_env(cls, prefix: str = '') -> 'DatabaseConfig':
        """
        Cria uma configuração a partir de variáveis de ambiente.
        
        Carrega os parâmetros de conexão a partir de variáveis de ambiente
        com o prefixo especificado. As variáveis esperadas são:
        - {prefix}DB_SERVER: Nome ou endereço do servidor
        - {prefix}DB_DATABASE: Nome do banco de dados
        - {prefix}DB_USERNAME: Nome de usuário
        - {prefix}DB_PASSWORD: Senha
        
        Args:
            prefix: Prefixo para as variáveis de ambiente (ex: 'RPA_')
            
        Returns:
            Instância de DatabaseConfig com os valores das variáveis de ambiente
        """
        load_dotenv()
        return cls(
            server=os.getenv(f'{prefix}DB_SERVER') or "",
            database=os.getenv(f'{prefix}DB_DATABASE') or "",
            username=os.getenv(f'{prefix}DB_USERNAME') or "",
            password=os.getenv(f'{prefix}DB_PASSWORD') or ""
        )


# Tipo genérico para o retorno das consultas
T = TypeVar('T')

class DatabaseOperations:
    """
    Classe base para operações de banco de dados.
    
    Esta classe fornece métodos básicos para obter conexões com o banco de dados
    usando diferentes bibliotecas (pyodbc e SQLAlchemy). Serve como base para
    classes mais específicas que implementam operações CRUD.
    
    Attributes:
        db_config: Configuração de conexão com o banco de dados
    """
    
    def __init__(self, db_config: DatabaseConfig):
        """
        Inicializa uma nova instância de DatabaseOperations.
        
        Args:
            db_config: Configuração de conexão com o banco de dados
        """
        self.db_config = db_config
    
    def get_connection(self) -> pyodbc.Connection:
        """
        Obtém uma conexão com o banco de dados via pyodbc.
        
        Returns:
            Objeto de conexão pyodbc
            
        Raises:
            pyodbc.Error: Se ocorrer um erro ao conectar ao banco de dados
        """
        return pyodbc.connect(self.db_config.connection_string)
    
    def get_sqlalchemy_engine(self):
        """
        Obtém um engine SQLAlchemy para o banco de dados.
        
        Returns:
            Engine SQLAlchemy para o banco de dados
            
        Raises:
            SQLAlchemyError: Se ocorrer um erro ao criar o engine
        """
        return create_engine(self.db_config.sqlalchemy_connection_string)


class ProcessosRpaInserter(DatabaseOperations):
    """
    Classe para inserir registros na tabela processosrpa via procedure.
    
    Esta classe especializa DatabaseOperations para fornecer métodos de inserção
    de registros na tabela processosrpa, utilizando a procedure inserir_processosrpa.
    Suporta inserção individual e em lote.
    
    Attributes:
        db_config: Configuração de conexão com o banco de dados
    """
    
    def insert(self, 
            ambiente: str,
            produto: str,
            versao: str,
            datahora: Optional[datetime] = None,
            coligada: Optional[str] = None,
            cod_filial: Optional[str] = None,
            nome_filial: Optional[str] = None,
            agrupamento: Optional[str] = None,
            cod_secao: Optional[str] = None,
            chapa: Optional[str] = None,
            data_geracao: Optional[datetime] = None,
            mes_gozo: Optional[datetime] = None,
            valor_liquido: Optional[float] = None,
            data_pagamento: Optional[datetime] = None,
            lote: Optional[str] = None,
            historico: Optional[str] = None,
            id_financeiro: Optional[str] = None,
            data_validacao: Optional[datetime] = None,
            data_integracao: Optional[datetime] = None,
            data_download_pdf: Optional[datetime] = None,
            data_finalizado: Optional[datetime] = None,
            statusexecucao: Optional[str] = None,
            ano_competencia: Optional[int] = None,
            mes_competencia: Optional[int] = None) -> Optional[int]:
        """
        Insere um registro na tabela processosrpa via procedure.
        
        Esta função chama a procedure inserir_processosrpa para inserir um novo registro
        na tabela processosrpa. A procedure retorna o ID do registro inserido.
        
        Args:
            ambiente: Ambiente (DEV, HML, PRD)
            produto: Nome do produto (ex: FIDI-ferias, FIDI-pos-folha)
            versao: Versão do produto
            datahora: Data e hora do registro (default: None)
            coligada: Código da coligada (default: None)
            cod_filial: Código da filial (default: None)
            nome_filial: Nome da filial (default: None)
            agrupamento: Agrupamento (default: None)
            cod_secao: Código da seção (default: None)
            chapa: Chapa do funcionário (default: None)
            data_geracao: Data de geração (default: None)
            mes_gozo: Mês de gozo (default: None)
            valor_liquido: Valor líquido (default: None)
            data_pagamento: Data de pagamento (default: None)
            lote: Lote (default: None)
            historico: Histórico (default: None)
            id_financeiro: ID financeiro (default: None)
            data_validacao: Data de validação (default: None)
            data_integracao: Data de integração (default: None)
            data_download_pdf: Data de download do PDF (default: None)
            data_finalizado: Data de finalização (default: None)
            statusexecucao: Status de execução (default: None)
            ano_competencia: Ano de competência (default: None)
            mes_competencia: Mês de competência (default: None)
            
        Returns:
            ID do registro inserido ou None se a inserção falhar
            
        Raises:
            Exception: Se ocorrer um erro durante a inserção
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            params = (
                datahora,
                ambiente,
                produto,
                versao,
                coligada,
                cod_filial,
                nome_filial,
                agrupamento,
                cod_secao,
                chapa,
                data_geracao,
                mes_gozo,
                valor_liquido,
                data_pagamento,
                lote,
                historico,
                id_financeiro,
                data_validacao,
                data_integracao,
                data_download_pdf,
                data_finalizado,
                statusexecucao,
                ano_competencia,
                mes_competencia
            )
            
            sql = "{CALL inserir_processosrpa (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}"
            cursor.execute(sql, params)
            
            result = cursor.fetchone()
            registro_id = result[0] if result else None
            
            conn.commit()
            return registro_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    
    def insert_batch(self, records: List[Dict[str, Any]]) -> Tuple[List[int], int]:
        """
        Insere múltiplos registros na tabela processosrpa via procedure.

        Esta função itera sobre uma lista de registros e chama o método insert
        para cada um deles. Registros com campos obrigatórios ausentes são ignorados.

        Args:
            records: Lista de dicionários, cada um representando um registro a ser inserido

        Returns:
            Tupla contendo a lista de IDs inseridos e o número de registros com erro
        """
        ids_inseridos = []
        registros_com_erro = 0

        for record in records:
            try:
                # Garantir que os campos obrigatórios não sejam None
                ambiente = record.get('ambiente')
                produto = record.get('produto')
                versao = record.get('versao')

                # Pular registro se campos obrigatórios estiverem ausentes
                if not ambiente or not produto or not versao:
                    print(f"Erro: Campos obrigatórios ausentes no registro: {record}")
                    registros_com_erro += 1
                    continue

                registro_id = self.insert(
                    ambiente=ambiente,
                    produto=produto,
                    versao=versao,
                    datahora=record.get('datahora'),
                    coligada=record.get('coligada'),
                    cod_filial=record.get('cod_filial'),
                    nome_filial=record.get('nome_filial'),
                    agrupamento=record.get('agrupamento'),
                    cod_secao=record.get('cod_secao'),
                    chapa=record.get('chapa'),
                    data_geracao=record.get('data_geracao'),
                    mes_gozo=record.get('mes_gozo'),
                    valor_liquido=record.get('valor_liquido'),
                    data_pagamento=record.get('data_pagamento'),
                    lote=record.get('lote'),
                    historico=record.get('historico'),
                    id_financeiro=record.get('id_financeiro'),
                    data_validacao=record.get('data_validacao'),
                    data_integracao=record.get('data_integracao'),
                    data_download_pdf=record.get('data_download_pdf'),
                    data_finalizado=record.get('data_finalizado'),
                    statusexecucao=record.get('statusexecucao'),
                    ano_competencia=record.get('ano_competencia'),
                    mes_competencia=record.get('mes_competencia')
                )

                if registro_id:
                    ids_inseridos.append(registro_id)
                    # Atualiza o ID no dicionário original para uso posterior
                    record['id'] = registro_id

            except Exception as e:
                print(f"Erro ao inserir registro: {e} | Registro: {record}")
                registros_com_erro += 1

        return ids_inseridos, registros_com_erro



class ProcessosRpaUpdater(DatabaseOperations):
    """
    Classe para atualizar registros na tabela processosrpa via procedure.
    
    Esta classe especializa DatabaseOperations para fornecer métodos de atualização
    de registros na tabela processosrpa, utilizando a procedure atualizar_processosrpa.
    Suporta atualização individual e em lote.
    
    Attributes:
        db_config: Configuração de conexão com o banco de dados
    """
    
    def update(self, 
            id: int,
            datahora: Optional[datetime] = None,
            ambiente: Optional[str] = None,
            produto: Optional[str] = None,
            versao: Optional[str] = None,
            coligada: Optional[str] = None,
            cod_filial: Optional[str] = None,
            nome_filial: Optional[str] = None,
            agrupamento: Optional[str] = None,
            cod_secao: Optional[str] = None,
            chapa: Optional[str] = None,
            data_geracao: Optional[datetime] = None,
            mes_gozo: Optional[datetime] = None,
            valor_liquido: Optional[float] = None,
            data_pagamento: Optional[datetime] = None,
            lote: Optional[str] = None,
            historico: Optional[str] = None,
            id_financeiro: Optional[str] = None,
            data_validacao: Optional[datetime] = None,
            data_integracao: Optional[datetime] = None,
            data_download_pdf: Optional[datetime] = None,
            data_finalizado: Optional[datetime] = None,
            statusexecucao: Optional[str] = None,
            ano_competencia: Optional[int] = None,
            mes_competencia: Optional[int] = None) -> bool:
        """
        Atualiza um registro na tabela processosrpa via procedure.
        
        Esta função chama a procedure atualizar_processosrpa para atualizar um registro
        existente na tabela processosrpa. Apenas os campos não-None serão atualizados.
        
        Args:
            id: ID do registro a ser atualizado
            (... demais args ...)
            ano_competencia: Ano de competência (default: None)
            mes_competencia: Mês de competência (default: None)
            
        Returns:
            True se a atualização foi bem-sucedida, False caso contrário
            
        Raises:
            Exception: Se ocorrer um erro durante a atualização
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            params = (
                id,
                datahora,
                ambiente,
                produto,
                versao,
                coligada,
                cod_filial,
                nome_filial,
                agrupamento,
                cod_secao,
                chapa,
                data_geracao,
                mes_gozo,
                valor_liquido,
                data_pagamento,
                lote,
                historico,
                id_financeiro,
                data_validacao,
                data_integracao,
                data_download_pdf,
                data_finalizado,
                statusexecucao,
                ano_competencia,
                mes_competencia
            )
            
            sql = "{CALL atualizar_processosrpa (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}"
            cursor.execute(sql, params)
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def update_batch(self, records: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Atualiza múltiplos registros na tabela processosrpa via procedure.
        
        Itera sobre a lista de registros e chama o método update para cada um deles.
        Registros sem ID ou com ID inválido são ignorados.
        
        Args:
            records: Lista de dicionários, cada um representando um registro a ser atualizado.
            
        Returns:
            Tupla contendo:
                - número de registros atualizados com sucesso
                - número de registros que falharam
        """
        registros_atualizados = 0
        registros_com_erro = 0

        for record in records:
            try:
                id_value = record.get('id')
                if not id_value:
                    print("Registro sem ID, não é possível atualizar")
                    registros_com_erro += 1
                    continue

                # Garantir que o ID seja inteiro
                try:
                    id_int = int(id_value)
                except (ValueError, TypeError):
                    print(f"ID inválido: {id_value}, não é possível converter para inteiro")
                    registros_com_erro += 1
                    continue

                # Chama a procedure atualizar_processosrpa para este registro
                success = self.update(
                    id=id_int,
                    datahora=record.get('datahora'),
                    ambiente=record.get('ambiente'),
                    produto=record.get('produto'),
                    versao=record.get('versao'),
                    coligada=record.get('coligada'),
                    cod_filial=record.get('cod_filial'),
                    nome_filial=record.get('nome_filial'),
                    agrupamento=record.get('agrupamento'),
                    cod_secao=record.get('cod_secao'),
                    chapa=record.get('chapa'),
                    data_geracao=record.get('data_geracao'),
                    mes_gozo=record.get('mes_gozo'),
                    valor_liquido=record.get('valor_liquido'),
                    data_pagamento=record.get('data_pagamento'),
                    lote=record.get('lote'),
                    historico=record.get('historico'),
                    id_financeiro=record.get('id_financeiro'),
                    data_validacao=record.get('data_validacao'),
                    data_integracao=record.get('data_integracao'),
                    data_download_pdf=record.get('data_download_pdf'),
                    data_finalizado=record.get('data_finalizado'),
                    statusexecucao=record.get('statusexecucao'),
                    ano_competencia=record.get('ano_competencia'),
                    mes_competencia=record.get('mes_competencia')
                )

                if success:
                    registros_atualizados += 1

            except Exception as e:
                error_id = record.get('id', 'desconhecido')
                print(f"Erro ao atualizar registro ID {error_id}: {e}")
                registros_com_erro += 1

        return registros_atualizados, registros_com_erro



class ProcedureExecutor(DatabaseOperations):
    """
    Classe especializada para execução de procedures com diferentes tipos de retorno.
    
    Esta classe fornece métodos para executar procedures que retornam diferentes
    tipos de dados: sem retorno, valor único, linha única, múltiplas linhas,
    valores booleanos e contagens.
    
    Attributes:
        db_config: Configuração de conexão com o banco de dados
    """
    
    def execute_procedure_no_result(self, procedure_name: str, params: Optional[List[Any]] = None) -> bool:
        """
        Executa procedure que não retorna dados (INSERT, UPDATE, DELETE).
        
        Args:
            procedure_name: Nome da procedure
            params: Lista de parâmetros
            
        Returns:
            bool: True se executada com sucesso
            
        Raises:
            Exception: Se ocorrer erro na execução
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = f"{{CALL {procedure_name} ({', '.join(['?' for _ in (params or [])])})}}"
            cursor.execute(sql, params or [])
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_procedure_single_value(self, procedure_name: str, params: Optional[List[Any]] = None) -> Any:
        """
        Executa procedure que retorna um único valor.
        
        Args:
            procedure_name: Nome da procedure
            params: Lista de parâmetros
            
        Returns:
            Any: Valor retornado pela procedure ou None
            
        Raises:
            Exception: Se ocorrer erro na execução
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = f"{{CALL {procedure_name} ({', '.join(['?' for _ in (params or [])])})}}"
            cursor.execute(sql, params or [])
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_procedure_single_row(self, procedure_name: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Executa procedure que retorna uma única linha.
        
        Args:
            procedure_name: Nome da procedure
            params: Lista de parâmetros
            
        Returns:
            Optional[Dict[str, Any]]: Dicionário com os dados ou None
            
        Raises:
            Exception: Se ocorrer erro na execução
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = f"{{CALL {procedure_name} ({', '.join(['?' for _ in (params or [])])})}}"
            cursor.execute(sql, params or [])
            result = cursor.fetchone()
            conn.commit()
            
            if result:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
            return None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_procedure_multiple_rows(self, procedure_name: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Executa procedure que retorna múltiplas linhas.
        
        Args:
            procedure_name: Nome da procedure
            params: Lista de parâmetros
            
        Returns:
            List[Dict[str, Any]]: Lista de dicionários com os dados
            
        Raises:
            Exception: Se ocorrer erro na execução
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = f"{{CALL {procedure_name} ({', '.join(['?' for _ in (params or [])])})}}"
            cursor.execute(sql, params or [])
            results = cursor.fetchall()
            conn.commit()
            
            if results:
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in results]
            return []
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_procedure_boolean_result(self, procedure_name: str, params: Optional[List[Any]] = None) -> bool:
        """
        Executa procedure que retorna resultado booleano (0/1, True/False).
        
        Args:
            procedure_name: Nome da procedure
            params: Lista de parâmetros
            
        Returns:
            bool: Resultado da procedure convertido para boolean
            
        Raises:
            Exception: Se ocorrer erro na execução
        """
        result = self.execute_procedure_single_value(procedure_name, params)
        
        # Conversões comuns para boolean
        if result is None:
            return False
        if isinstance(result, bool):
            return result
        if isinstance(result, (int, float)):
            return result != 0
        if isinstance(result, str):
            return result.lower() in ('true', '1', 'yes', 'sim', 's')
        
        return bool(result)
    
    def execute_procedure_count_result(self, procedure_name: str, params: Optional[List[Any]] = None) -> int:
        """
        Executa procedure que retorna contagem (COUNT, affected rows).
        
        Args:
            procedure_name: Nome da procedure
            params: Lista de parâmetros
            
        Returns:
            int: Número retornado pela procedure
            
        Raises:
            Exception: Se ocorrer erro na execução
        """
        result = self.execute_procedure_single_value(procedure_name, params)
        return int(result) if result is not None else 0


class ProcedureHelpers(DatabaseOperations):
    """
    Métodos auxiliares para cenários específicos de procedures.
    
    Esta classe fornece métodos de alto nível para operações comuns
    usando procedures, como validação, limpeza de dados, obtenção
    de permissões e status do sistema.
    
    Attributes:
        db_config: Configuração de conexão com o banco de dados
    """
    
    def __init__(self, db_config: DatabaseConfig):
        super().__init__(db_config)
        self.executor = ProcedureExecutor(db_config)
    
    def validate_data_procedure(self, table: str, record_id: int) -> bool:
        """
        Executa procedure de validação que retorna True/False.
        
        Args:
            table: Nome da tabela
            record_id: ID do registro a validar
            
        Returns:
            bool: True se dados são válidos
        """
        return self.executor.execute_procedure_boolean_result("sp_validate_data", [table, record_id])
    
    def get_next_sequence_value(self, sequence_name: str) -> int:
        """
        Obtém próximo valor de sequência.
        
        Args:
            sequence_name: Nome da sequência
            
        Returns:
            int: Próximo valor da sequência
        """
        return self.executor.execute_procedure_count_result("sp_get_next_sequence", [sequence_name])
    
    def cleanup_old_data(self, table: str, days_old: int) -> int:
        """
        Limpa dados antigos e retorna quantidade removida.
        
        Args:
            table: Nome da tabela
            days_old: Idade em dias dos registros a remover
            
        Returns:
            int: Quantidade de registros removidos
        """
        return self.executor.execute_procedure_count_result("sp_cleanup_old_data", [table, days_old])
    
    def get_user_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Obtém permissões do usuário via procedure.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            List[Dict[str, Any]]: Lista de permissões do usuário
        """
        return self.executor.execute_procedure_multiple_rows("sp_get_user_permissions", [user_id])
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtém status do sistema via procedure.
        
        Returns:
            Dict[str, Any]: Informações de status do sistema
        """
        return self.executor.execute_procedure_single_row("sp_get_system_status") or {}
    
    def process_batch_data(self, batch_id: str) -> Tuple[bool, int, str]:
        """
        Processa lote de dados e retorna status, quantidade e mensagem.
        
        Args:
            batch_id: ID do lote a processar
            
        Returns:
            Tuple[bool, int, str]: (sucesso, quantidade_processada, mensagem)
        """
        result = self.executor.execute_procedure_single_row("sp_process_batch", [batch_id])
        
        if result:
            return (
                bool(result.get('success', False)),
                int(result.get('processed_count', 0)),
                str(result.get('message', ''))
            )
        # Garantir retorno em todos os caminhos
        return (False, 0, "")


class DatabaseQuery(DatabaseOperations, Generic[T]):
    """
    Classe para executar consultas SQL com proteção contra SQL injection.
    
    Esta classe especializa DatabaseOperations para fornecer métodos de consulta
    ao banco de dados com proteção contra SQL injection usando SQLAlchemy.
    Suporta diferentes formatos de retorno (dicionário, DataFrame, valor único)
    e processamento personalizado via callbacks.
    
    Attributes:
        db_config: Configuração de conexão com o banco de dados
    """
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, 
                      result_type: str = 'dict') -> Union[List[Dict[str, Any]], pd.DataFrame, List[Any]]:
        """
        Executa uma consulta SQL com parâmetros sanitizados e retorna os resultados no formato especificado.
        
        Args:
            query: A consulta SQL a ser executada
            params: Dicionário de parâmetros para a consulta
            result_type: Tipo de retorno ('dict', 'dataframe' ou 'raw')
            
        Returns:
            Lista de dicionários, DataFrame do pandas ou None, dependendo do result_type
            
        Raises:
            SQLAlchemyError: Se ocorrer um erro na execução da consulta
        """
        try:
            # Usar SQLAlchemy para sanitização de parâmetros
            engine = self.get_sqlalchemy_engine()
            with engine.connect() as connection:
                # Criar consulta parametrizada
                sql_query = text(query)
                
                # Executar consulta com parâmetros
                result = connection.execute(sql_query, params or {})
                
                # Processar resultados conforme o tipo solicitado
                if result_type == 'dataframe':
                    # Converter as chaves para lista para evitar problemas de tipo com RMKeyView
                    columns = list(result.keys())
                    return pd.DataFrame(result.fetchall(), columns=columns)
                elif result_type == 'dict':
                    columns = list(result.keys())
                    return [dict(zip(columns, row)) for row in result.fetchall()]
                else:  # 'raw'
                    # Converter para lista para garantir o tipo de retorno correto
                    return list(result.fetchall())
                    
        except SQLAlchemyError as e:
            print(f"Erro ao executar consulta: {e}")
            raise
    
    def execute_query_single_value(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Executa uma consulta SQL e retorna um único valor.
        
        Args:
            query: A consulta SQL a ser executada
            params: Dicionário de parâmetros para a consulta
            
        Returns:
            O primeiro valor da primeira linha do resultado ou None
        """
        try:
            engine = self.get_sqlalchemy_engine()
            with engine.connect() as connection:
                sql_query = text(query)
                result = connection.execute(sql_query, params or {})
                row = result.fetchone()
                return row[0] if row else None
                
        except SQLAlchemyError as e:
            print(f"Erro ao executar consulta para valor único: {e}")
            raise
    
    def execute_query_with_callback(self, query: str, params: Optional[Dict[str, Any]] = None, 
                                   callback: Optional[Callable[[Any], T]] = None) -> Optional[T]:
        """
        Executa uma consulta SQL e processa os resultados com uma função de callback.
        
        Args:
            query: A consulta SQL a ser executada
            params: Dicionário de parâmetros para a consulta
            callback: Função para processar os resultados
            
        Returns:
            O resultado do processamento da função de callback ou None se nenhum callback for fornecido
        """
        try:
            engine = self.get_sqlalchemy_engine()
            with engine.connect() as connection:
                sql_query = text(query)
                result = connection.execute(sql_query, params or {})
                
                if callback:
                    return callback(result)
                return None
                
        except SQLAlchemyError as e:
            print(f"Erro ao executar consulta com callback: {e}")
            raise


# Exemplo de uso:
if __name__ == "__main__":
    # Configuração do banco de dados
    db_config = DatabaseConfig.from_env('RPA_')
    
    # Exemplo de consulta
    try:
        # Consulta como lista de dicionários
        query = DatabaseQuery(db_config)
        results = query.execute_query(
            "SELECT TOP 5 * FROM processosrpa WHERE statusexecucao = :status",
            {"status": "NOVO"}
        )
        print(f"Resultados como dicionários: {results}")
        
        # Consulta como DataFrame
        df_results = query.execute_query(
            "SELECT TOP 5 * FROM processosrpa WHERE statusexecucao = :status",
            {"status": "NOVO"},
            result_type='dataframe'
        )
        print(f"Resultados como DataFrame:\n{df_results}")
        
        # Consulta de valor único
        count = query.execute_query_single_value(
            "SELECT COUNT(*) FROM processosrpa WHERE statusexecucao = :status",
            {"status": "NOVO"}
        )
        print(f"Total de registros: {count}")
        
    except Exception as e:
        print(f"Erro: {e}")
    
    # Inserção de um registro
    inserter = ProcessosRpaInserter(db_config)
    try:
        registro_id = inserter.insert(
            ambiente="HML",
            produto="FIDI-ferias",
            versao="1.0.0",
            nome_filial="TESTE",
            agrupamento="TESTE",
            chapa="123456",
            data_pagamento=datetime.now(),
            historico="TESTE"
        )
        print(f"Registro inserido com ID: {registro_id}")
        
        # Atualização do registro
        if registro_id is not None:
            updater = ProcessosRpaUpdater(db_config)
            success = updater.update(
                id=registro_id,
                lote="LOTE_TESTE",
                statusexecucao="SUCESSO"
            )
            print(f"Registro atualizado: {success}")
        else:
            print("Não foi possível atualizar o registro porque o ID é None")
        
    except Exception as e:
        print(f"Erro: {e}")
    
    # Exemplos de uso das novas classes de procedures
    try:
        # Executor de procedures
        executor = ProcedureExecutor(db_config)
        
        # Procedure sem retorno
        success = executor.execute_procedure_no_result("sp_update_status", ["ATIVO", 123])
        print(f"Procedure executada: {success}")
        
        # Procedure que retorna valor único
        next_id = executor.execute_procedure_single_value("sp_get_next_id", ["processosrpa"])
        print(f"Próximo ID: {next_id}")
        
        # Procedure que retorna boolean
        is_valid = executor.execute_procedure_boolean_result("sp_validate_record", [123])
        print(f"Registro válido: {is_valid}")
        
        # Procedure que retorna contagem
        affected_rows = executor.execute_procedure_count_result("sp_cleanup_temp_data", [])
        print(f"Registros afetados: {affected_rows}")
        
        # Helpers para procedures
        helpers = ProcedureHelpers(db_config)
        
        # Validação de dados
        is_data_valid = helpers.validate_data_procedure("processosrpa", 123)
        print(f"Dados válidos: {is_data_valid}")
        
        # Limpeza de dados antigos
        cleanup_count = helpers.cleanup_old_data("temp_table", 30)
        print(f"Registros limpos: {cleanup_count}")
        
        # Status do sistema
        system_status = helpers.get_system_status()
        print(f"Status do sistema: {system_status}")
        
    except Exception as e:
        print(f"Erro com procedures: {e}")