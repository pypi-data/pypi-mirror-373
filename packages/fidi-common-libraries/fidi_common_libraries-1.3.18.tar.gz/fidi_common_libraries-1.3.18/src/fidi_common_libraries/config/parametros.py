"""
Módulo para gerenciamento de parâmetros do sistema de RPA para a FIDI.

Este módulo fornece uma interface centralizada para acessar parâmetros armazenados
no banco de dados, com suporte a cache, tipagem forte e tratamento
de parâmetros sensíveis. Permite a configuração dinâmica do sistema sem
necessidade de alteração de código ou reimplantação.

Características principais:
- Acesso a parâmetros por ambiente e produto
- Cache com TTL configurável para reduzir consultas ao banco
- Conversão automática de tipos (string, int, float, bool, json, csv, date)
- Tratamento especial para parâmetros sensíveis (não exibidos em logs)
- Agrupamento de parâmetros para organização lógica

Classe principal:
- Parametros: Gerenciador de parâmetros do sistema
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union, cast
from datetime import datetime

from fidi_common_libraries.data.db_data import DatabaseConfig, DatabaseQuery
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Parametros:
    """
    Classe para gerenciamento de parâmetros do sistema.
    
    Fornece acesso aos parâmetros armazenados no banco de dados,
    com suporte a cache, conversão de tipos e tratamento de
    parâmetros sensíveis. Permite a configuração dinâmica do sistema
    sem necessidade de alteração de código ou reimplantação.
    
    Os parâmetros são armazenados na tabela parametrosrpa e podem
    ser organizados por ambiente, produto e agrupamento. O cache é
    utilizado para reduzir o número de consultas ao banco de dados.
    
    Attributes:
        ambiente: Ambiente de execução (ex: 'HML', 'PROD')
        produto: Nome do produto (ex: 'FIDI-ferias', 'FIDI-pos-folha')
        _cache: Dicionário com os parâmetros em cache
        _last_refresh: Dicionário com os timestamps da última atualização do cache
        _cache_ttl: Tempo de vida do cache em segundos (padrão: 300s = 5min)
        db_config: Configuração de conexão com o banco de dados
        db_query: Objeto para execução de consultas SQL
    """
    
    def __init__(self, ambiente: str, produto: str):
        """
        Inicializa o gerenciador de parâmetros.
        
        Args:
            ambiente: Ambiente de execução (ex: 'HML', 'PROD')
            produto: Nome do produto (ex: 'FIDI-ferias')
        """
        self.ambiente = ambiente
        self.produto = produto
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._last_refresh: Dict[str, datetime] = {}
        self._cache_ttl = 300  # 5 minutos em segundos
        
        # Carrega variáveis de ambiente para configuração do banco
        load_dotenv()
        
        # Configura conexão com o banco de dados
        self.db_config = DatabaseConfig.from_env('RPA_')
        self.db_query = DatabaseQuery(self.db_config)
        
        logger.info(f"Inicializando gerenciador de parâmetros para {produto} em {ambiente}")
    
    def get_parametro(self, nome: str, default: Any = None) -> Any:
        """
        Obtém o valor de um parâmetro do banco de dados ou do cache.
        
        Esta função busca um parâmetro pelo nome, primeiro verificando o cache
        e, se necessário, consultando o banco de dados. O valor é convertido
        automaticamente para o tipo apropriado conforme definido na coluna
        tipo_valor da tabela parametrosrpa.
        
        O resultado é armazenado em cache por um período definido por _cache_ttl
        para reduzir o número de consultas ao banco de dados.
        
        Parâmetros sensíveis (is_sensivel=True) não são exibidos nos logs.
        
        Args:
            nome: Nome do parâmetro a ser buscado
            default: Valor padrão a ser retornado caso o parâmetro não exista
            
        Returns:
            Valor do parâmetro convertido para o tipo apropriado ou o valor
            default se o parâmetro não for encontrado ou ocorrer um erro
        """
        try:
            # Verifica se o parâmetro está em cache e se o cache é válido
            if nome in self._cache and (
                datetime.now().timestamp() - self._last_refresh.get(nome, datetime(1970, 1, 1)).timestamp() < self._cache_ttl
            ):
                logger.debug(f"Usando parâmetro {nome} do cache")
                return self._cache[nome]["valor"]
            
            # Busca o parâmetro no banco de dados usando DatabaseQuery
            query = """
            SELECT id, ambiente, produto, parametro, agrupamento, valor, tipo_valor, is_sensivel, 
                   criado_em, atualizado_em, versao, ativo, descricao
            FROM parametrosrpa
            WHERE ambiente = :ambiente
              AND produto = :produto
              AND parametro = :parametro
              AND ativo = 1
            """
            
            params = {
                "ambiente": self.ambiente,
                "produto": self.produto,
                "parametro": nome
            }
            
            # Executa a consulta como lista de dicionários
            results = self.db_query.execute_query(query, params, result_type='dict')
            
            # Verificação explícita se há resultados
            if isinstance(results, list):
                if not results:  # Lista vazia
                    logger.warning(f"Parâmetro {nome} não encontrado, usando valor padrão: {default}")
                    return default
            else:
                # Se não for uma lista, verificamos se é um DataFrame
                try:
                    if results.empty:  # DataFrame vazio
                        logger.warning(f"Parâmetro {nome} não encontrado, usando valor padrão: {default}")
                        return default
                except (AttributeError, TypeError):
                    # Não é um DataFrame ou não tem o atributo 'empty'
                    logger.warning(f"Resultado inesperado ao buscar parâmetro {nome}, usando valor padrão: {default}")
                    return default
            
            # Extrair valores do primeiro resultado
            try:
                # Tenta acessar como lista
                if isinstance(results, list):
                    row = results[0]
                else:
                    # Tenta acessar como DataFrame
                    row = results.iloc[0].to_dict() if hasattr(results, 'iloc') else {}
                
                # Extrai valores com tratamento de erros
                try:
                    valor = str(row.get("valor", ""))
                    tipo_valor = str(row.get("tipo_valor", "string"))
                    is_sensivel = bool(row.get("is_sensivel", False))
                except (AttributeError, TypeError):
                    # Se row não tiver método get, tenta acessar como dicionário
                    try:
                        valor = str(row["valor"] if "valor" in row else "")
                        tipo_valor = str(row["tipo_valor"] if "tipo_valor" in row else "string")
                        is_sensivel = bool(row["is_sensivel"] if "is_sensivel" in row else False)
                    except (TypeError, KeyError):
                        # Se ainda falhar, usa valores padrão
                        logger.warning(f"Formato de resultado inesperado para parâmetro {nome}, usando valor padrão")
                        return default
            except (IndexError, TypeError):
                logger.warning(f"Erro ao acessar resultado para parâmetro {nome}, usando valor padrão")
                return default
            
            # Converte o valor para o tipo apropriado
            valor_convertido = self._converter_tipo(valor, tipo_valor)
            
            # Armazena em cache
            self._cache[nome] = {
                "valor": valor_convertido,
                "tipo": tipo_valor,
                "sensivel": is_sensivel
            }
            self._last_refresh[nome] = datetime.now()
            
            # Log apropriado baseado na sensibilidade do parâmetro
            if is_sensivel:
                logger.info(f"Parâmetro sensível {nome} carregado")
            else:
                logger.info(f"Parâmetro {nome} carregado: {valor_convertido}")
                
            return valor_convertido
            
        except Exception as e:
            logger.error(f"Erro ao obter parâmetro {nome}: {str(e)}")
            return default
    
    def get_parametros_por_grupo(self, agrupamento: str) -> Dict[str, Any]:
        """
        Obtém todos os parâmetros de um determinado agrupamento.
        
        Esta função busca todos os parâmetros pertencentes a um agrupamento específico,
        convertendo cada valor para o tipo apropriado e retornando um dicionário
        onde as chaves são os nomes dos parâmetros e os valores são os valores convertidos.
        
        Os parâmetros obtidos também são armazenados individualmente no cache.
        
        Exemplos de agrupamentos:
        - 'Conexao': Parâmetros de conexão com sistemas externos
        - 'Email': Configurações de envio de e-mail
        - 'Processo': Parâmetros específicos do processo de negócio
        - 'Sistema': Configurações gerais do sistema
        
        Args:
            agrupamento: Nome do agrupamento dos parâmetros
            
        Returns:
            Dicionário com os parâmetros do agrupamento, onde as chaves são os
            nomes dos parâmetros e os valores são os valores convertidos para
            os tipos apropriados
        """
        try:
            # Busca os parâmetros no banco de dados usando DatabaseQuery
            query = """
            SELECT id, ambiente, produto, parametro, agrupamento, valor, tipo_valor, is_sensivel, 
                   criado_em, atualizado_em, versao, ativo, descricao
            FROM parametrosrpa
            WHERE ambiente = :ambiente
              AND produto = :produto
              AND agrupamento = :agrupamento
              AND ativo = 1
            ORDER BY parametro
            """
            
            params = {
                "ambiente": self.ambiente,
                "produto": self.produto,
                "agrupamento": agrupamento
            }
            
            # Executa a consulta como lista de dicionários
            results = self.db_query.execute_query(query, params, result_type='dict')
            
            resultado: Dict[str, Any] = {}
            
            # Verificação explícita do tipo de resultado
            if not isinstance(results, list):
                try:
                    # Tenta converter DataFrame para lista de dicionários
                    if hasattr(results, 'to_dict'):
                        results = results.to_dict('records')
                    else:
                        logger.warning(f"Formato de resultado inesperado para agrupamento {agrupamento}")
                        return resultado
                except Exception:
                    logger.warning(f"Erro ao processar resultados para agrupamento {agrupamento}")
                    return resultado
            
            # Processa cada resultado
            for row in results:
                try:
                    # Tenta extrair valores com método get
                    parametro = None
                    valor = None
                    tipo_valor = None
                    is_sensivel = None
                    
                    try:
                        parametro = str(row.get("parametro", ""))
                        valor = str(row.get("valor", ""))
                        tipo_valor = str(row.get("tipo_valor", "string"))
                        is_sensivel = bool(row.get("is_sensivel", False))
                    except (AttributeError, TypeError):
                        # Se row não tiver método get, tenta acessar como dicionário
                        try:
                            parametro = str(row["parametro"] if "parametro" in row else "")
                            valor = str(row["valor"] if "valor" in row else "")
                            tipo_valor = str(row["tipo_valor"] if "tipo_valor" in row else "string")
                            is_sensivel = bool(row["is_sensivel"] if "is_sensivel" in row else False)
                        except (TypeError, KeyError):
                            # Se ainda falhar, pula este registro
                            logger.warning("Registro com formato inesperado encontrado, ignorando")
                            continue
                    
                    # Pula registros sem parâmetro válido
                    if not parametro:
                        continue
                    
                    valor_convertido = self._converter_tipo(valor, tipo_valor)
                    resultado[parametro] = valor_convertido
                    
                    # Atualiza o cache
                    self._cache[parametro] = {
                        "valor": valor_convertido,
                        "tipo": tipo_valor,
                        "sensivel": is_sensivel
                    }
                    self._last_refresh[parametro] = datetime.now()
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar registro: {str(e)}")
                    continue
            
            logger.info(f"Carregados {len(resultado)} parâmetros do agrupamento {agrupamento}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao obter parâmetros do agrupamento {agrupamento}: {str(e)}")
            return {}
    
    def atualizar_parametro(self, nome: str, valor: Any) -> bool:
        """
        Atualiza o valor de um parâmetro no banco de dados.
        
        Esta função atualiza o valor de um parâmetro existente no banco de dados
        e também atualiza o cache, se o parâmetro estiver presente nele.
        
        A atualização é feita através da stored procedure sp_atualizar_parametro,
        que verifica se o parâmetro existe e atualiza apenas o valor, mantendo
        os demais atributos (tipo_valor, is_sensivel, etc.) inalterados.
        
        O valor é sempre convertido para string antes de ser salvo no banco,
        mas é armazenado no cache já convertido para o tipo apropriado.
        
        Args:
            nome: Nome do parâmetro a ser atualizado
            valor: Novo valor do parâmetro (qualquer tipo, será convertido para string)
            
        Returns:
            True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            # Converte o valor para string antes de salvar
            valor_str = str(valor)
            
            # Executa a procedure de atualização via query direta
            query = """
            EXEC sp_atualizar_parametro 
                @ambiente = :ambiente, 
                @produto = :produto, 
                @parametro = :parametro, 
                @valor = :valor
            """
            
            params = {
                "ambiente": self.ambiente,
                "produto": self.produto,
                "parametro": nome,
                "valor": valor_str
            }
            
            # Para stored procedures que não retornam resultados, usamos try-except
            try:
                self.db_query.execute_query(query, params)
            except Exception as e:
                # Verifica se é o erro esperado de "result object does not return rows"
                if "does not return rows" in str(e):
                    # Este é um comportamento normal para stored procedures que não retornam dados
                    pass
                else:
                    # Se for outro tipo de erro, propaga a exceção
                    raise
            
            # Atualiza o cache se o parâmetro estiver presente
            if nome in self._cache:
                tipo_valor = self._cache[nome]["tipo"]
                is_sensivel = self._cache[nome]["sensivel"]
                
                self._cache[nome] = {
                    "valor": self._converter_tipo(valor_str, tipo_valor),
                    "tipo": tipo_valor,
                    "sensivel": is_sensivel
                }
                self._last_refresh[nome] = datetime.now()
            
            if self._cache.get(nome, {}).get("sensivel", False):
                logger.info(f"Parâmetro sensível {nome} atualizado")
            else:
                logger.info(f"Parâmetro {nome} atualizado para: {valor}")
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar parâmetro {nome}: {str(e)}")
            return False
    
    def limpar_cache(self, parametro: Optional[str] = None) -> None:
        """
        Limpa o cache de parâmetros.
        
        Esta função limpa o cache de parâmetros, forçando a próxima chamada
        a get_parametro() ou get_parametros_por_grupo() a buscar os valores
        diretamente do banco de dados.
        
        É útil quando se sabe que os parâmetros foram alterados diretamente
        no banco de dados por outro processo ou quando se deseja garantir
        que os valores mais recentes sejam utilizados.
        
        Args:
            parametro: Nome do parâmetro específico a ser limpo do cache.
                      Se None, limpa todo o cache.
        """
        if parametro:
            if parametro in self._cache:
                del self._cache[parametro]
                if parametro in self._last_refresh:
                    del self._last_refresh[parametro]
                logger.debug(f"Cache do parâmetro {parametro} limpo")
        else:
            self._cache.clear()
            self._last_refresh.clear()
            logger.debug("Cache de parâmetros completamente limpo")
    
    def _converter_tipo(self, valor: str, tipo_valor: str) -> Any:
        """
        Converte o valor para o tipo apropriado.
        
        Esta função interna converte um valor string para o tipo especificado.
        Suporta os seguintes tipos de conversão:
        
        - string: Mantém o valor como string (sem conversão)
        - int: Converte para inteiro
        - float: Converte para número de ponto flutuante
        - bool: Converte para booleano (true, 1, t, y, yes, sim são considerados True)
        - json: Converte para objeto Python usando json.loads()
        - csv: Converte para lista de strings, separando por vírgula
        - date: Converte para objeto datetime no formato YYYY-MM-DD
        
        Em caso de erro na conversão, retorna o valor original como string e
        registra o erro no log.
        
        Args:
            valor: Valor string a ser convertido
            tipo_valor: Tipo do valor ('string', 'int', 'float', 'bool', 'json', 'csv', 'date')
            
        Returns:
            Valor convertido para o tipo apropriado ou o valor original em caso de erro
        """
        try:
            if tipo_valor == 'string':
                return valor
            elif tipo_valor == 'int':
                return int(valor)
            elif tipo_valor == 'float':
                return float(valor)
            elif tipo_valor == 'bool':
                return valor.lower() in ('true', '1', 't', 'y', 'yes', 'sim')
            elif tipo_valor == 'json':
                return json.loads(valor)
            elif tipo_valor == 'csv':
                return [item.strip() for item in valor.split(',')]
            elif tipo_valor == 'date':
                return datetime.strptime(valor, '%Y-%m-%d')
            else:
                logger.warning(f"Tipo de valor desconhecido: {tipo_valor}, retornando como string")
                return valor
        except Exception as e:
            logger.error(f"Erro ao converter valor '{valor}' para tipo {tipo_valor}: {str(e)}")
            return valor  # Retorna o valor original em caso de erro