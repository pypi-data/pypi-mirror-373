import json
import logging
from typing import Union, Dict, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
import boto3

from neofin_toobox.exceptions.adapters.sqs_adapter_exception import SQSAdapterException

logger = logging.getLogger(__name__)


class SQSAdapter:
    """
    Adaptador para operações com Amazon SQS.

    Provides methods to send messages to SQS queues with proper error handling
    and message serialization.
    """

    def __init__(self):
        """
        Inicializa o adaptador SQS.

        """
        try:
            self.sqs_resource = boto3.resource("sqs")

        except Exception as e:
            logger.error(f"Erro ao inicializar cliente SQS: {e}")
            raise SQSAdapterException(f"Falha na inicialização do SQS: {e}") from e

    def _get_queue(self, queue_name: str):
        """
        Obtém a fila SQS, utilizando cache para performance.

        Args:
            queue_name: Nome da fila

        Returns:
            Objeto da fila SQS

        Raises:
            SQSAdapterError: Se a fila não for encontrada
        """
        try:
            queue = self.sqs_resource.get_queue_by_name(QueueName=queue_name)
            return queue
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AWS.SimpleQueueService.NonExistentQueue':
                raise SQSAdapterException(f"Fila '{queue_name}' não encontrada")
            else:
                raise SQSAdapterException(f"Erro ao acessar fila '{queue_name}': {e}") from e

    def send_message(
            self,
            queue_name: str,
            message: Union[str, dict, list],
            delay_seconds: int = 0
    ) -> Dict[str, Any]:
        """
        Envia uma mensagem para a fila SQS.

        Args:
            queue_name: Nome da fila
            message: Mensagem a ser enviada (string, dict ou list)
            delay_seconds: Segundos para atrasar a entrega (0-900)
            message_attributes: Atributos adicionais da mensagem

        Returns:
            Resposta do SQS contendo MessageId e MD5OfBody

        Raises:
            SQSAdapterError: Se houver erro no envio
        """
        if not queue_name:
            raise SQSAdapterException("Nome da fila é obrigatório")

        if not message:
            raise SQSAdapterException("Mensagem não pode estar vazia")

        if not (0 <= delay_seconds <= 900):
            raise SQSAdapterException("delay_seconds deve estar entre 0 e 900")

        try:
            queue = self._get_queue(queue_name)

            send_params = {
                'MessageBody': message,
                'DelaySeconds': delay_seconds
            }

            response = queue.send_message(**send_params)

            logger.info(f"Mensagem enviada para fila '{queue_name}' - MessageId: {response.get('MessageId')}")
            return response

        except SQSAdapterException:
            raise
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Erro AWS ao enviar mensagem para '{queue_name}': {e}")
            raise SQSAdapterException(f"Erro ao enviar mensagem: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar mensagem para '{queue_name}': {e}")
            raise SQSAdapterException(f"Erro inesperado: {e}")

    def send_batch_messages(
            self,
            queue_name: str,
            messages: list,
            delay_seconds: int = 0
    ) -> Dict[str, Any]:
        """
        Envia múltiplas mensagens em lote (até 10 por vez).

        Args:
            queue_name: Nome da fila
            messages: Lista de mensagens
            delay_seconds: Segundos para atrasar a entrega

        Returns:
            Resposta do SQS com successful e failed messages
        """
        if not messages:
            raise SQSAdapterException("Lista de mensagens não pode estar vazia")

        if len(messages) > 10:
            raise SQSAdapterException("Máximo de 10 mensagens por lote")

        try:
            queue = self._get_queue(queue_name)

            entries = []
            for i, message in enumerate(messages):
                entries.append({
                    'Id': str(i),
                    'MessageBody': message,
                    'DelaySeconds': delay_seconds
                })

            response = queue.send_messages(Entries=entries)

            logger.info(f"Lote de {len(messages)} mensagens enviado para '{queue_name}'")
            return response

        except Exception as e:
            logger.error(f"Erro ao enviar lote para '{queue_name}': {e}")
            raise SQSAdapterException(f"Erro no envio em lote: {e}")