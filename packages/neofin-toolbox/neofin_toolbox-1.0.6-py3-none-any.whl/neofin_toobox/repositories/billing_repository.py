from typing import Optional, Dict, Any, List

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from neofin_toobox.configs.enums import TableConfigEnum
from neofin_toobox.exceptions.common_exceptions import CommonException
from neofin_toobox.repositories.dynamodb_repository import DynamoDbRepository

import logging

logger = logging.getLogger(__name__)

class BillingRepository(DynamoDbRepository):
    def __init__(self):
        super().__init__()
        self.table_billing = self.resource.Table(TableConfigEnum.BILLING)

    def get_by_company_id(self, company_id: str):
        logger.info("Getting billing by company id: %s", company_id)
        try:
            logger.debug(f"Getting billing by company id: {company_id}")

            response = self.table_billing.query(
                IndexName='company_id',
                KeyConditionExpression=Key('company_id').eq(company_id)
            )

            billings = response.get('Items', [])
            logger.debug(f"Found {len(billings)} billings for company: {company_id}")

            return billings

        except ClientError as e:
            logger.error(f"ClientError getting billings by company id {company_id}: {e}")
            raise CommonException(f"ClientError getting billings by company id {company_id}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error getting companies by document {company_id}: {e}")
            raise CommonException(f"Unexpected error retrieving companies by document: {e}") from e

    def get_by_id(self, billing_id: str):
        try:
            logger.debug(f"Retrieve billing by id {billing_id}")

            response = self.table_billing.get_item(
                Key={'id': billing_id}
            )

            billing = response.get('Item')
            if not billing:
                logger.info(f"Billing not found for id: {billing_id}")
                return None

            logger.debug(f"Found {len(billing)} billings for id: {billing_id}")
            return billing

        except ClientError as e:
            logger.error(f"ClientError getting billings by id {billing_id}: {e}")
            raise CommonException(f"ClientError getting billings by id {billing_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting billings by document {billing_id}: {e}")
            raise CommonException(f"Unexpected error retrieving billings by document: {e}")

    def put_item(self, payload: Dict[str, Any]) -> None:
        try:
            billing_id = payload.get('id', 'unknown')
            logger.debug(f"Putting billing: {billing_id}")

            self.table_billing.put_item(Item=payload)

            logger.info("Billing successfully stored: %s", billing_id)

        except ClientError as e:
            logger.error(f"ClientError putting billing: {e}")
            raise CommonException("ClientError putting billing") from e
        except Exception as e:
            logger.error(f"Unexpected error putting billing: {e}")
            raise CommonException("Unexpected error storing billing") from e