import logging
from typing import List, Dict, Any, Optional
from boto3.dynamodb.conditions import Key, Attr, Or, And
from datetime import datetime

from neofin_toobox.configs.enums import TableConfigEnum
from neofin_toobox.repositories.dynamodb_repository import DynamoDbRepository

logger = logging.getLogger(__name__)

class InstallmentsRepository(DynamoDbRepository):
    def __init__(self):
        super().__init__()
        self.table_installments = self.resource.Table(TableConfigEnum.INSTALLMENTS)

    def get_overdue_installments_by_company_id(self, company_id: str) -> List[dict]:
        try:
            logger.info('Getting installments by company_id: %s', company_id)

            overdue_day = datetime.now()
            overdue_day_format = overdue_day.strftime("%Y-%m-%d")
            logger.debug("Overdue day: %s", overdue_day_format)

            key_condition = Key('company_id').eq(company_id) & Key('due_date').lt(overdue_day_format)
            filter_condition = Key('installment_status').eq('overdue') | Key('status').eq('overdue')

            query_params = {
                'IndexName': 'company_id-due_date',
                'KeyConditionExpression': key_condition,
                'FilterExpression': filter_condition
            }

            installments = self._paginated_query(query_params=query_params, table=self.table_installments)

            logger.info("Company ID: %s - Number of installments: %d", company_id, len(installments))

            return installments

        except Exception as ex:
            logger.error("Problems getting installments by company_id %s: %s", company_id, ex, exc_info=True)
            return []

    def get_overdue_installments_by_customer_id(self, customer_ids: List[str], company_id: str) -> List[dict]:
        try:
            logger.info('Getting installments by customer_ids: %s', customer_ids)

            overdue_filters = Or(
                And(Attr('customer_id').is_in(customer_ids), Attr('status').eq('overdue')),
                And(Attr('customer_id').is_in(customer_ids), Attr('installment_status').eq('overdue')),
            )

            query_params = {
                "IndexName": 'company_id',
                'KeyConditionExpression': Key('company_id').eq(company_id),
                'FilterExpression': overdue_filters
            }

            installments = self._paginated_query(query_params=query_params, table=self.table_installments)

            logger.info("Company ID: %s - Number of installments: %d", company_id, len(installments))

            return installments

        except Exception as ex:
            logger.error("Problems getting installments by customer_ids %s: %s", customer_ids, ex, exc_info=True)
            return []

    def get_installment_by_id(self, installment_id: str) -> Optional[dict]:

        try:
            logger.info('Getting installment by ID: %s', installment_id)

            if not installment_id:
                logger.warning("Empty installment_id provided")
                return None


            response = self.table_installments.get_item(Key={'id': installment_id})
            installment = response.get('Item')
            return installment

        except Exception as ex:
            logger.error("Problems getting installment by ID %s: %s", installment_id, ex, exc_info=True)
            return None

    def get_installments_by_ids(self, installment_ids: List[str], company_id: Optional[str] = None) -> List[dict]:
        try:
            logger.info('Getting installments by IDs: %s (count: %d)', installment_ids[:5], len(installment_ids))

            if not installment_ids:
                logger.warning("Empty installment_ids list provided")
                return []

            batch_size = 100
            all_installments = []

            for i in range(0, len(installment_ids), batch_size):
                batch_ids = installment_ids[i:i + batch_size]
                logger.debug("Processing batch %d/%d with %d IDs",
                             i // batch_size + 1,
                             (len(installment_ids) + batch_size - 1) // batch_size,
                             len(batch_ids))

                id_filter = Attr('id').is_in(batch_ids)
                query_params = {
                    "IndexName": 'company_id',
                    'KeyConditionExpression': Key('company_id').eq(company_id),
                    'FilterExpression': id_filter
                }
                batch_installments = self._paginated_query(query_params=query_params, table=self.table_installments)
                all_installments.extend(batch_installments)

                logger.debug("Batch completed. Found %d installments in this batch", len(batch_installments))

            logger.info("Total installments found: %d out of %d requested IDs",
                        len(all_installments), len(installment_ids))

            return all_installments

        except Exception as ex:
            logger.error("Problems getting installments by IDs %s: %s", installment_ids, ex, exc_info=True)
            return []

    def get_installments_by_billing_id(self, billing_id: str) -> List[dict]:
        try:
            logger.info('Getting installments by billing_id: %s', billing_id)

            response = self.table_installments.query(
                IndexName='billing_id',
                KeyConditionExpression=Key('billing_id').eq(billing_id)
            )

            installments = response.get('Items', []) or []
            logger.info("Found %d installments for billing_id: %s", len(installments), billing_id)

            return installments

        except Exception as ex:
            logger.error("Problems getting installments by billing_id %s: %s", billing_id, ex, exc_info=True)
            return []