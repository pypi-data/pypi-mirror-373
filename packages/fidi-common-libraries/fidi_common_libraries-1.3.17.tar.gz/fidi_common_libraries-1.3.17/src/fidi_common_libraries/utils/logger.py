"""
Módulo de logging em banco de dados para o sistema de RPA para a FIDI.

Este módulo implementa funções para registro de logs em diferentes bancos de dados,
permitindo o acompanhamento centralizado das operações do hub. Suporta Oracle, PostgreSQL
e SQL Server, detectando automaticamente o tipo de conexão fornecida.
"""

import json
import oracledb
import psycopg2
import pyodbc
from datetime import datetime
from typing import Union, Optional, Dict, Any

def registrar_log_banco(
    conn,
    ambiente: str,
    produto: str,
    versao: str,
    nivel: str,
    modulo: str,
    processo: str,
    acao: str,
    lote: str,
    mensagem: str,
    usuario: str,
    status_execucao: str,
    hostname: str,
    ip_origem: str,
    detalhes: Optional[Union[str, Dict[str, Any]]] = None,
    correlation_id: Optional[str] = None,
    duracao_ms: Optional[int] = None,
    categoria: Optional[str] = None
):
    """
    Wrapper genérico para registrar log no banco, detectando o tipo de conexão.
    
    Esta função identifica automaticamente o tipo de conexão de banco de dados
    (Oracle, PostgreSQL ou SQL Server) e encaminha para a função específica
    de registro de log.
    
    Args:
        conn: Conexão com o banco de dados (oracledb, psycopg2 ou pyodbc)
        ambiente: Ambiente (DEV, HML, PRD)
        produto: Nome do produto (ex: FIDI-ferias, FIDI-pos-folha)
        versao: Versão do produto
        nivel: Nível do log (INFO, ERROR, WARNING, DEBUG)
        modulo: Módulo que gerou o log
        processo: Processo que gerou o log
        acao: Ação executada
        lote: Identificador de lote
        mensagem: Mensagem do log
        usuario: Usuário que executou a ação
        status_execucao: Status da execução (SUCESSO, ERRO, PENDENTE)
        hostname: Nome da máquina
        ip_origem: IP da máquina
        detalhes: Detalhes adicionais em formato JSON ou string
        correlation_id: ID de correlação para rastreamento
        duracao_ms: Duração em milissegundos
        categoria: Categoria do log
        
    Raises:
        ValueError: Se o tipo de conexão não for suportado
    """
    if isinstance(conn, oracledb.Connection):
        registrar_log_rpa_oracle(
            conn, ambiente, produto, versao, nivel, modulo, processo, acao,
            lote, mensagem, usuario, status_execucao, hostname, ip_origem, 
            detalhes, correlation_id, duracao_ms, categoria
        )
    elif isinstance(conn, psycopg2.extensions.connection):
        registrar_log_rpa_postgres(
            conn, ambiente, produto, versao, nivel, modulo, processo, acao,
            lote, mensagem, usuario, status_execucao, hostname, ip_origem, 
            detalhes, correlation_id, duracao_ms, categoria
        )
    elif isinstance(conn, pyodbc.Connection):
        registrar_log_rpa_sqlserver(
            conn, ambiente, produto, versao, nivel, modulo, processo, acao,
            lote, mensagem, usuario, status_execucao, hostname, ip_origem, 
            detalhes, correlation_id, duracao_ms, categoria
        )
    else:
        raise ValueError("Tipo de conexão não suportado.")

# ------------------------- ORACLE -------------------------

def registrar_log_rpa_oracle(
    conn, 
    ambiente: str, 
    produto: str, 
    versao: str, 
    nivel: str, 
    modulo: str, 
    processo: str,
    acao: str, 
    lote: str, 
    mensagem: str, 
    usuario: str, 
    status_execucao: str,
    hostname: str, 
    ip_origem: str, 
    detalhes: Optional[Union[str, Dict[str, Any]]], 
    correlation_id: Optional[str] = None,
    duracao_ms: Optional[int] = None, 
    categoria: Optional[str] = None
):
    """
    Registra log no banco de dados Oracle.
    
    Esta função utiliza a procedure FIDI.inserir_log_execucao para registrar
    logs em um banco de dados Oracle.
    
    Args:
        conn: Conexão com o banco de dados Oracle (oracledb)
        ambiente: Ambiente (DEV, HML, PRD)
        produto: Nome do produto
        versao: Versão do produto
        nivel: Nível do log (INFO, ERROR, WARNING, DEBUG)
        modulo: Módulo que gerou o log
        processo: Processo que gerou o log
        acao: Ação executada
        lote: Identificador de lote
        mensagem: Mensagem do log
        usuario: Usuário que executou a ação
        status_execucao: Status da execução
        hostname: Nome da máquina
        ip_origem: IP da máquina
        detalhes: Detalhes adicionais em formato JSON ou string
        correlation_id: ID de correlação para rastreamento
        duracao_ms: Duração em milissegundos
        categoria: Categoria do log
    """
    with conn.cursor() as cur:
        detalhes_json = json.dumps(detalhes) if isinstance(detalhes, dict) else detalhes
        detalhes_clob = cur.var(oracledb.DB_TYPE_CLOB)
        detalhes_clob.setvalue(0, detalhes_json)

        cur.callproc("FIDI.inserir_log_execucao", [
            datetime.now(), ambiente, produto, versao, nivel, modulo,
            processo, acao, lote, mensagem, usuario, status_execucao,
            detalhes_clob, hostname, ip_origem, correlation_id, duracao_ms, categoria
        ])
    # 👇 Comitar após a chamada da procedure
    conn.commit()

# ------------------------ POSTGRES ------------------------

def registrar_log_rpa_postgres(
    conn, 
    ambiente: str, 
    produto: str, 
    versao: str, 
    nivel: str, 
    modulo: str, 
    processo: str,
    acao: str, 
    lote: str, 
    mensagem: str, 
    usuario: str, 
    status_execucao: str,
    hostname: str, 
    ip_origem: str, 
    detalhes: Optional[Union[str, Dict[str, Any]]], 
    correlation_id: Optional[str] = None,
    duracao_ms: Optional[int] = None, 
    categoria: Optional[str] = None
):
    """
    Registra log no banco de dados PostgreSQL.
    
    Esta função insere um registro de log na tabela logexecucaorpa
    em um banco de dados PostgreSQL.
    
    Args:
        conn: Conexão com o banco de dados PostgreSQL (psycopg2)
        ambiente: Ambiente (DEV, HML, PRD)
        produto: Nome do produto
        versao: Versão do produto
        nivel: Nível do log (INFO, ERROR, WARNING, DEBUG)
        modulo: Módulo que gerou o log
        processo: Processo que gerou o log
        acao: Ação executada
        lote: Identificador de lote
        mensagem: Mensagem do log
        usuario: Usuário que executou a ação
        status_execucao: Status da execução
        hostname: Nome da máquina
        ip_origem: IP da máquina
        detalhes: Detalhes adicionais em formato JSON ou string
        correlation_id: ID de correlação para rastreamento
        duracao_ms: Duração em milissegundos
        categoria: Categoria do log
    """
    with conn.cursor() as cur:
        detalhes_json = json.dumps(detalhes) if isinstance(detalhes, dict) else detalhes

        cur.execute("""
            INSERT INTO logexecucaorpa (
                datahora, ambiente, produto, versao, nivel, modulo, processo,
                acao, lote, mensagem, usuario, statusexecucao, detalhes, hostname, 
                iporigem, correlationid, duracao_ms, categoria
            ) VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            ambiente, produto, versao, nivel, modulo, processo,
            acao, lote, mensagem, usuario, status_execucao,
            detalhes_json, hostname, ip_origem, correlation_id, duracao_ms, categoria
        ))

# ------------------------ SQL SERVER ----------------------

def registrar_log_rpa_sqlserver(
    conn, 
    ambiente: str, 
    produto: str, 
    versao: str, 
    nivel: str, 
    modulo: str, 
    processo: str,
    acao: str, 
    lote: str, 
    mensagem: str, 
    usuario: str, 
    status_execucao: str,
    hostname: str, 
    ip_origem: str, 
    detalhes: Optional[Union[str, Dict[str, Any]]], 
    correlation_id: Optional[str] = None,
    duracao_ms: Optional[int] = None, 
    categoria: Optional[str] = None
):
    """
    Registra log no banco de dados SQL Server.
    
    Esta função tenta usar a procedure inserir_log_execucao se existir,
    caso contrário, faz uma inserção direta na tabela logexecucaorpa.
    Inclui tratamento de erro para não interromper o fluxo principal.
    
    Args:
        conn: Conexão com o banco de dados SQL Server (pyodbc)
        ambiente: Ambiente (DEV, HML, PRD)
        produto: Nome do produto
        versao: Versão do produto
        nivel: Nível do log (INFO, ERROR, WARNING, DEBUG)
        modulo: Módulo que gerou o log
        processo: Processo que gerou o log
        acao: Ação executada
        lote: Identificador de lote
        mensagem: Mensagem do log
        usuario: Usuário que executou a ação
        status_execucao: Status da execução
        hostname: Nome da máquina
        ip_origem: IP da máquina
        detalhes: Detalhes adicionais em formato JSON ou string
        correlation_id: ID de correlação para rastreamento
        duracao_ms: Duração em milissegundos
        categoria: Categoria do log
    """
    with conn.cursor() as cur:
        detalhes_json = json.dumps(detalhes) if isinstance(detalhes, dict) else detalhes

        try:
            # Verificar se a procedure existe
            cur.execute("SELECT 1 FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_NAME = 'inserir_log_execucao'")
            procedure_exists = cur.fetchone() is not None
            
            if procedure_exists:
                # Usar a procedure
                sql = "{CALL inserir_log_execucao (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}"
                cur.execute(sql, (
                    datetime.now(), ambiente, produto, versao, nivel, modulo, processo,
                    acao, lote, mensagem, usuario, status_execucao, detalhes_json,
                    hostname, ip_origem, correlation_id, duracao_ms, categoria
                ))
            else:
                # Fallback para inserção direta
                cur.execute("""
                    INSERT INTO logexecucaorpa (
                        datahora, ambiente, produto, versao, nivel, modulo, processo,
                        acao, lote, mensagem, usuario, statusexecucao, detalhes, hostname, 
                        iporigem, correlationid, duracao_ms, categoria
                    ) VALUES (GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ambiente, produto, versao, nivel.upper(), modulo, processo,
                    acao, lote, mensagem, usuario, status_execucao.upper(), detalhes_json,
                    hostname, ip_origem, correlation_id, duracao_ms, categoria
                ))
            
            # Commit após a inserção
            conn.commit()
            
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
            # Não propagar o erro para não interromper o fluxo principal