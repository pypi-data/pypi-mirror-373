"""Módulo de integração com serviços AWS.

Este módulo fornece clientes padronizados para serviços AWS como SQS, SNS,
Lambda e S3, facilitando a integração com a infraestrutura AWS e garantindo
boa práticas de segurança e configuração.
"""

from .common_aws import (
    AWSConfig,
    SQSClient,
    SNSClient,
    LambdaClient,
    S3Client,
    AWSClientFactory,
    create_message_with_metadata,
    validate_aws_credentials
)

__all__ = [
    'AWSConfig',
    'SQSClient',
    'SNSClient', 
    'LambdaClient',
    'S3Client',
    'AWSClientFactory',
    'create_message_with_metadata',
    'validate_aws_credentials'
]