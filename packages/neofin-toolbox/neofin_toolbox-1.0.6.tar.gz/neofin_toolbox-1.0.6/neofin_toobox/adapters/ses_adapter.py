from jinja2 import Environment, FileSystemLoader
import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Any, Optional
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SESAdapter:
    """
    Classe para envio de emails usando Amazon SES com templates Jinja2.

    Attributes:
        region_name (str): Região AWS para o serviço SES
        template_folder (str): Caminho para a pasta de templates
        default_source_email (str): Email remetente padrão
    """

    def __init__(
            self,
            region_name: str = 'us-east-1',
            template_folder: Optional[str] = None,
            default_source_email: str = "noreply@neofin.com.br"
    ):
        """
        Inicializa a classe SES.

        Args:
            region_name: Região AWS (padrão: us-east-1)
            template_folder: Caminho para templates (padrão: ./templates)
            default_source_email: Email remetente padrão
        """
        self.region_name = region_name
        self.default_source_email = default_source_email

        # Configurar pasta de templates
        if template_folder is None:
            template_folder = os.path.join(os.path.dirname(__file__), 'templates')

        self.template_folder = template_folder

        if not os.path.exists(self.template_folder):
            raise FileNotFoundError(f"Template folder not found: {self.template_folder}")

        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Inicializa os clientes SES e Jinja2."""
        try:
            self.ses_client = boto3.client('ses', region_name=self.region_name)
            self.jinja_env = Environment(
                loader=FileSystemLoader(self.template_folder),
                autoescape=True  # Segurança contra XSS
            )
            logger.info(f"SES client initialized in region: {self.region_name}")
        except NoCredentialsError as e:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
            raise

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renderiza um template Jinja2 com o contexto fornecido.

        Args:
            template_name: Nome do arquivo de template
            context: Dicionário com variáveis para o template

        Returns:
            String com o HTML renderizado

        Raises:
            FileNotFoundError: Se o template não for encontrado
            Exception: Para outros erros de renderização
        """
        try:
            template = self.jinja_env.get_template(template_name)
            rendered_content = template.render(context)
            logger.info(f"Template '{template_name}' rendered successfully")
            return rendered_content
        except FileNotFoundError as e:
            logger.error(f"Template '{template_name}' not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error rendering template '{template_name}': {e}")
            raise

    def send_email(
            self,
            to_addresses: List[str],
            subject: str,
            template_name: str,
            context: Dict[str, Any],
            source_email: Optional[str] = None,
            cc_addresses: Optional[List[str]] = None,
            bcc_addresses: Optional[List[str]] = None,
            reply_to_addresses: Optional[List[str]] = None,
            include_text_version: bool = False
    ) -> Dict[str, Any]:
        """
        Envia email usando Amazon SES.

        Args:
            to_addresses: Lista de emails destinatários
            subject: Assunto do email
            template_name: Nome do template Jinja2
            context: Contexto para renderização do template
            source_email: Email remetente (opcional)
            cc_addresses: Lista de emails em cópia (opcional)
            bcc_addresses: Lista de emails em cópia oculta (opcional)
            reply_to_addresses: Lista de emails para resposta (opcional)
            include_text_version: Se deve incluir versão texto simples

        Returns:
            Resposta do SES com MessageId

        Raises:
            ValueError: Para parâmetros inválidos
            ClientError: Para erros do SES
        """
        # Validations
        if not to_addresses:
            raise ValueError("Recipient list cannot be empty")

        if not subject.strip():
            raise ValueError("Subject cannot be empty")

        # Use default email if not specified
        source = source_email or self.default_source_email

        try:
            # Render HTML template
            body_html = self.render_template(template_name, context)

            # Configure recipients
            destination = {'ToAddresses': to_addresses}
            if cc_addresses:
                destination['CcAddresses'] = cc_addresses
            if bcc_addresses:
                destination['BccAddresses'] = bcc_addresses

            # Configure message body
            message_body = {
                'Html': {
                    'Data': body_html,
                    'Charset': 'UTF-8'
                }
            }

            if include_text_version:
                try:
                    text_template_name = template_name.replace('.html', '.txt')
                    body_text = self.render_template(text_template_name, context)
                    message_body['Text'] = {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    }
                except FileNotFoundError:
                    logger.warning(f"Text template '{text_template_name}' not found")

            # Send email
            response = self.ses_client.send_email(
                Source=source,
                Destination=destination,
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': message_body
                },
                ReplyToAddresses=reply_to_addresses or []
            )

            message_id = response['MessageId']
            logger.info(f"Email sent successfully. MessageId: {message_id}")

            return response

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"SES error ({error_code}): {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            raise

    def send_bulk_emails(
            self,
            email_data: List[Dict[str, Any]],
            template_name: str,
            source_email: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Sends multiple emails with different contexts.

        Args:
            email_data: List of dictionaries with email data
                       Format: [{'to': ['email@example.com'], 'subject': 'Subject', 'context': {...}}]
            template_name: Template name to be used
            source_email: Sender email (optional)

        Returns:
            List with results of each send
        """
        results = []

        for i, data in enumerate(email_data):
            try:
                result = self.send_email(
                    to_addresses=data['to'],
                    subject=data['subject'],
                    template_name=template_name,
                    context=data['context'],
                    source_email=source_email
                )
                results.append({
                    'index': i,
                    'status': 'success',
                    'message_id': result['MessageId'],
                    'to': data['to']
                })

            except Exception as e:
                logger.error(f"Error sending email {i}: {e}")
                results.append({
                    'index': i,
                    'status': 'error',
                    'error': str(e),
                    'to': data['to']
                })

        return results

    def verify_email_address(self, email: str) -> bool:
        """
        Verifies if an email address is verified in SES.

        Args:
            email: Email address to be verified

        Returns:
            True if verified, False otherwise
        """
        try:
            response = self.ses_client.get_identity_verification_attributes(
                Identities=[email]
            )

            verification_attrs = response['VerificationAttributes']
            if email in verification_attrs:
                status = verification_attrs[email]['VerificationStatus']
                return status == 'Success'

            return False

        except ClientError as e:
            logger.error(f"Error verifying email {email}: {e}")
            return False

    def get_send_statistics(self) -> Dict[str, Any]:
        """
        Gets SES send statistics.

        Returns:
            Dictionary with send statistics
        """
        try:
            response = self.ses_client.get_send_statistics()
            return response['SendDataPoints']
        except ClientError as e:
            logger.error(f"Error getting statistics: {e}")
            raise