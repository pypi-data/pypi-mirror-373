import logging
from typing import Dict, Any

from boto3.exceptions import Boto3Error
from botocore.exceptions import ClientError

from neofin_toobox.configs.enums import TableConfigEnum
from neofin_toobox.repositories.dynamodb_repository import DynamoDbRepository

logger = logging.getLogger(__name__)


class AuditRepository(DynamoDbRepository):
    def __init__(self):
        super().__init__()
        self.table_audit = self.resource.Table(TableConfigEnum.AUDIT)

    def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.debug("Starting item insertion into DynamoDB table '%s': %s", TableConfigEnum.AUDIT, item)
            response = self.table_audit.put_item(Item=item)
            logger.info("Item successfully inserted into table '%s'. Response: %s", TableConfigEnum.AUDIT, response)
            return response

        except ClientError as e:
            logger.error("ClientError while inserting item into table '%s': %s", TableConfigEnum.AUDIT, e.response['Error'])
            raise

        except Boto3Error as e:
            logger.error("Boto3Error while inserting item into table '%s': %s", TableConfigEnum.AUDIT, str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error while inserting item into table '%s': %s", TableConfigEnum.AUDIT, str(e))
            raise
