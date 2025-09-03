"""
Utilitários AWS reutilizáveis para projetos FIDI.

Fornece clientes padronizados para SQS, SNS e configurações comuns AWS.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError


@dataclass
class AWSConfig:
    """Configuração AWS centralizada."""
    
    region: str = 'sa-east-1'
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    
    @classmethod
    def from_env(cls, prefix: str = 'AWS_') -> 'AWSConfig':
        """Cria configuração a partir de variáveis de ambiente."""
        return cls(
            region=os.getenv(f'{prefix}REGION', 'sa-east-1'),
            access_key=os.getenv(f'{prefix}ACCESS_KEY_ID'),
            secret_key=os.getenv(f'{prefix}SECRET_ACCESS_KEY')
        )
    
    def get_session(self) -> boto3.Session:
        """Retorna sessão boto3 configurada.
        
        Returns:
            boto3.Session: Sessão boto3 configurada com as credenciais e região especificadas
        """
        if self.access_key and self.secret_key:
            return boto3.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
        return boto3.Session(region_name=self.region)


class SQSClient:
    """Cliente SQS padronizado com funcionalidades comuns."""
    
    def __init__(self, config: AWSConfig):
        self.config = config
        self.client = config.get_session().client('sqs')
    
    def validate_queue_url(self, queue_url: str) -> bool:
        """Valida formato da URL da fila SQS.
        
        Args:
            queue_url: URL da fila SQS a ser validada
            
        Returns:
            bool: True se a URL estiver em formato válido, False caso contrário
        """
        pattern = r'^https://sqs\.[\w-]+\.amazonaws\.com/\d+/[\w-]+$'
        return bool(re.match(pattern, queue_url))
    
    def get_queue_info(self, queue_url: str) -> Dict[str, Any]:
        """Obtém informações da fila."""
        try:
            response = self.client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['All']
            )
            return response.get('Attributes', {})
        except ClientError as e:
            raise Exception(f"Erro ao obter informações da fila: {e}")
    
    def send_message(self, queue_url: str, message: Union[str, Dict[str, Any]], 
                    message_attributes: Optional[Dict[str, Dict[str, str]]] = None) -> str:
        """Envia mensagem para fila SQS.
        
        Args:
            queue_url: URL da fila SQS
            message: Mensagem a ser enviada (string ou dicionário que será convertido para JSON)
            message_attributes: Atributos da mensagem no formato esperado pelo SQS:
                               {'Nome': {'StringValue': 'valor', 'DataType': 'String'}}
                               
        Returns:
            str: ID da mensagem enviada
            
        Raises:
            Exception: Se ocorrer um erro ao enviar a mensagem
        """
        try:
            body = json.dumps(message) if isinstance(message, dict) else message
            
            # Preparar os parâmetros básicos
            params: Dict[str, Any] = {
                'QueueUrl': queue_url,
                'MessageBody': body
            }
            
            # Adicionar os atributos da mensagem se fornecidos
            if message_attributes:
                params['MessageAttributes'] = message_attributes
            
            response = self.client.send_message(**params)
            return response['MessageId']
            
        except ClientError as e:
            raise Exception(f"Erro ao enviar mensagem: {e}")
    
    def receive_messages(self, queue_url: str, max_messages: int = 10, 
                        wait_time: int = 20) -> List[Dict[str, Any]]:
        """Recebe mensagens da fila SQS."""
        try:
            response = self.client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            return response.get('Messages', [])
            
        except ClientError as e:
            raise Exception(f"Erro ao receber mensagens: {e}")
    
    def delete_message(self, queue_url: str, receipt_handle: str) -> bool:
        """Remove mensagem da fila."""
        try:
            self.client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
        except ClientError:
            return False
    
    def purge_queue(self, queue_url: str) -> bool:
        """Limpa todas as mensagens da fila."""
        try:
            self.client.purge_queue(QueueUrl=queue_url)
            return True
        except ClientError:
            return False


class SNSClient:
    """Cliente SNS padronizado com funcionalidades comuns."""
    
    def __init__(self, config: AWSConfig):
        self.config = config
        self.client = config.get_session().client('sns')
    
    def publish_message(self, topic_arn: str, message: Union[str, Dict[str, Any]], 
                       subject: Optional[str] = None,
                       message_attributes: Optional[Dict[str, Dict[str, str]]] = None) -> str:
        """Publica mensagem no tópico SNS.
        
        Args:
            topic_arn: ARN do tópico SNS
            message: Mensagem a ser publicada (string ou dicionário que será convertido para JSON)
            subject: Assunto da mensagem (opcional)
            message_attributes: Atributos da mensagem no formato esperado pelo SNS:
                               {'Nome': {'StringValue': 'valor', 'DataType': 'String'}}
                               
        Returns:
            str: ID da mensagem publicada
            
        Raises:
            Exception: Se ocorrer um erro ao publicar a mensagem
        """
        try:
            body = json.dumps(message) if isinstance(message, dict) else message
            
            # Preparar os parâmetros básicos
            params: Dict[str, Any] = {
                'TopicArn': topic_arn,
                'Message': body
            }
            
            # Adicionar o assunto se fornecido
            if subject:
                params['Subject'] = subject
            
            # Adicionar os atributos da mensagem se fornecidos
            if message_attributes:
                params['MessageAttributes'] = message_attributes
            
            response = self.client.publish(**params)
            return response['MessageId']
            
        except ClientError as e:
            raise Exception(f"Erro ao publicar mensagem: {e}")
    
    def get_topic_attributes(self, topic_arn: str) -> Dict[str, Any]:
        """Obtém atributos do tópico SNS."""
        try:
            response = self.client.get_topic_attributes(TopicArn=topic_arn)
            return response.get('Attributes', {})
        except ClientError as e:
            raise Exception(f"Erro ao obter atributos do tópico: {e}")
    
    def list_subscriptions(self, topic_arn: str) -> List[Dict[str, Any]]:
        """Lista assinantes do tópico."""
        try:
            response = self.client.list_subscriptions_by_topic(TopicArn=topic_arn)
            return response.get('Subscriptions', [])
        except ClientError as e:
            raise Exception(f"Erro ao listar assinantes: {e}")


class LambdaClient:
    """Cliente Lambda padronizado com funcionalidades comuns."""
    
    def __init__(self, config: AWSConfig):
        self.config = config
        self.client = config.get_session().client('lambda')
    
    def invoke_function(self, function_name: str, payload: Dict[str, Any], 
                       invocation_type: str = 'RequestResponse') -> Dict[str, Any]:
        """Invoca função Lambda."""
        try:
            response = self.client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(payload)
            )
            
            result = {
                'StatusCode': response['StatusCode'],
                'ExecutedVersion': response.get('ExecutedVersion'),
                'LogResult': response.get('LogResult')
            }
            
            if 'Payload' in response:
                payload_data = response['Payload'].read()
                if payload_data:
                    result['Payload'] = json.loads(payload_data)
            
            return result
            
        except ClientError as e:
            raise Exception(f"Erro ao invocar função Lambda: {e}")
    
    def get_function_info(self, function_name: str) -> Dict[str, Any]:
        """Obtém informações da função Lambda."""
        try:
            response = self.client.get_function(FunctionName=function_name)
            return response
        except ClientError as e:
            raise Exception(f"Erro ao obter informações da função: {e}")


class S3Client:
    """Cliente S3 padronizado com funcionalidades comuns."""
    
    def __init__(self, config: AWSConfig):
        self.config = config
        self.client = config.get_session().client('s3')
    
    def upload_file(self, file_path: str, bucket: str, key: str) -> bool:
        """Faz upload de arquivo para S3."""
        try:
            self.client.upload_file(file_path, bucket, key)
            return True
        except ClientError:
            return False
    
    def download_file(self, bucket: str, key: str, file_path: str) -> bool:
        """Faz download de arquivo do S3."""
        try:
            self.client.download_file(bucket, key, file_path)
            return True
        except ClientError:
            return False
    
    def get_object(self, bucket: str, key: str) -> bytes:
        """Obtém objeto do S3."""
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Erro ao obter objeto: {e}")
    
    def put_object(self, bucket: str, key: str, data: Union[str, bytes]) -> bool:
        """Coloca objeto no S3."""
        try:
            body = data.encode() if isinstance(data, str) else data
            self.client.put_object(Bucket=bucket, Key=key, Body=body)
            return True
        except ClientError:
            return False
    
    def list_objects(self, bucket: str, prefix: str = '') -> List[str]:
        """Lista objetos no bucket S3."""
        try:
            response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            raise Exception(f"Erro ao listar objetos: {e}")


class AWSClientFactory:
    """Factory para criar clientes AWS padronizados."""
    
    def __init__(self, config: Optional[AWSConfig] = None):
        self.config = config or AWSConfig.from_env()
    
    def get_sqs_client(self) -> SQSClient:
        """Retorna cliente SQS configurado."""
        return SQSClient(self.config)
    
    def get_sns_client(self) -> SNSClient:
        """Retorna cliente SNS configurado."""
        return SNSClient(self.config)
    
    def get_lambda_client(self) -> LambdaClient:
        """Retorna cliente Lambda configurado."""
        return LambdaClient(self.config)
    
    def get_s3_client(self) -> S3Client:
        """Retorna cliente S3 configurado."""
        return S3Client(self.config)


# Utilitários de conveniência
def create_message_with_metadata(data: Dict[str, Any], 
                               source: str = 'fidi-common-libraries') -> Dict[str, Any]:
    """Cria mensagem padronizada com metadados.
    
    Args:
        data: Dados a serem incluídos na mensagem
        source: Fonte da mensagem (default: 'fidi-common-libraries')
        
    Returns:
        Dict[str, Any]: Mensagem formatada com timestamp, source e dados
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'source': source,
        'data': data
    }


def validate_aws_credentials(config: AWSConfig) -> bool:
    """Valida credenciais AWS.
    
    Args:
        config: Configuração AWS contendo credenciais a serem validadas
        
    Returns:
        bool: True se as credenciais são válidas, False caso contrário
    """
    try:
        session = config.get_session()
        sts = session.client('sts')
        sts.get_caller_identity()
        return True
    except (NoCredentialsError, ClientError):
        return False