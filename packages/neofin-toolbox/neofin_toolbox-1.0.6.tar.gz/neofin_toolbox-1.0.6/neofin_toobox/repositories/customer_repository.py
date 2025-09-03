from datetime import datetime
from decimal import Decimal

from neofin_toobox.configs.enums import TableConfigEnum
from neofin_toobox.exceptions.common_exceptions import CommonException
from neofin_toobox.repositories.dynamodb_repository import DynamoDbRepository

from typing import List, Dict, Any
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger(__name__)


class CustomerRepository(DynamoDbRepository):
    GSI_COMPANY_DOCUMENT = 'company_id-document'
    GSI_DOCUMENT = 'document'

    def __init__(self):
        super().__init__()
        self.table_customer = self.resource.Table(TableConfigEnum.CUSTOMER)

    def get_by_customer_id_and_company_id(self, customer_id: str, company_id: str) -> Dict[str, Any]:
        try:
            response = self.table_customer.get_item(Key = {'id': customer_id, 'company_id': company_id})
            return response.get('Item', {})
        except Exception as e:
            logger.error(f"Error querying customer: customer_id={customer_id}, error={str(e)}")
            raise CommonException("Failed to retrieve customer")

    def get_by_document_and_company(self, company_id: str, document: str) -> List[Dict[str, Any]]:
        try:
            customer_items = self._query_all_customers(company_id, document)

            if not customer_items:
                logger.info(
                    f"No customers found for company_id={company_id}, document={document}"
                )
                return []

            customer_items.sort(key=lambda x: x.get('set_up_at', ''))
            return customer_items

        except Exception as e:
            logger.error(f"Error querying customers: company_id={company_id}, document={document}, error={str(e)}")
            raise CommonException("Failed to retrieve customers") from e

    def get_by_document(self, document: str) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Querying customers by document: {document}")

            customer_items = self._query_customers_by_document(document)

            if not customer_items:
                logger.info(f"No customers found for document={document}")
                return []

            self._normalize_setup_timestamps(customer_items)

            customer_items.sort(key=lambda x: x['set_up_at'])
            return customer_items

        except Exception as e:
            logger.error(f"Error querying customers by document: document={document}, error={str(e)}")
            raise CommonException(f"Exception occurred when getting customer by document={document}") from e

    def _query_all_customers(self, company_id: str, document: str) -> List[Dict[str, Any]]:
        customer_items = []
        last_evaluated_key = None

        while True:
            query_params = {
                'IndexName': self.GSI_COMPANY_DOCUMENT,
                'KeyConditionExpression': (
                        Key('company_id').eq(company_id) &
                        Key('document').eq(document)
                )
            }

            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table_customer.query(**query_params)

            if response.get('Count', 0) > 0:
                customer_items.extend(response['Items'])

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        return customer_items

    def _query_customers_by_document(self, document: str) -> List[Dict[str, Any]]:
        customer_items = []
        last_evaluated_key = None

        while True:
            query_params = {
                'IndexName': self.GSI_DOCUMENT,
                'KeyConditionExpression': Key('document').eq(document)
            }

            if last_evaluated_key:
                query_params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table_customer.query(**query_params)

            if response.get('Count', 0) > 0:
                customer_items.extend(response['Items'])

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        return customer_items

    @staticmethod
    def _normalize_setup_timestamps(customer_items: List[Dict[str, Any]]) -> None:
        """Ensure all customers have a valid set_up_at timestamp.

        Args:
            customer_items: List of customer dictionaries to normalize
        """
        current_timestamp = int(datetime.now().timestamp())

        for customer in customer_items:
            if 'set_up_at' not in customer or customer['set_up_at'] is None:
                customer['set_up_at'] = current_timestamp
                logger.warning(f"Customer missing set_up_at, using current timestamp: {current_timestamp}")

    def get_by_company_id(self, company_id: str) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Scanning customers by company_id: {company_id}")

            customer_items = self._scan_customers_by_company_id(company_id)

            if not customer_items:
                logger.info(f"No customers found for company_id={company_id}")
                return []

            customer_items.sort(key=lambda x: Decimal(x.get('set_up_at', 99999999999)))

            return customer_items

        except Exception as e:
            logger.error(f"Error scanning customers by company_id: company_id={company_id}, error={str(e)}")
            raise CommonException(f"Exception occurred when getting customers by company_id: {company_id}") from e

    def _scan_customers_by_company_id(self, company_id: str) -> List[Dict[str, Any]]:
        customer_items = []
        last_evaluated_key = None

        while True:
            scan_params = {
                'FilterExpression': Key('company_id').eq(company_id)
            }

            if last_evaluated_key:
                scan_params['ExclusiveStartKey'] = last_evaluated_key

            response = self.table_customer.scan(**scan_params)

            if response.get('Count', 0) > 0:
                customer_items.extend(response['Items'])

            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

        return customer_items