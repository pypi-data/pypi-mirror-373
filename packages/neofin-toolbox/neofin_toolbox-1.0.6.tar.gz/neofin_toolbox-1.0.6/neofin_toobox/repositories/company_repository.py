from typing import Optional, Dict, Any, List

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from neofin_toobox.configs.enums import TableConfigEnum
from neofin_toobox.exceptions.common_exceptions import CommonException
from neofin_toobox.repositories.dynamodb_repository import DynamoDbRepository

import logging

logger = logging.getLogger(__name__)


class CompanyRepository(DynamoDbRepository):
    def __init__(self):
        super().__init__()
        self.table_company = self.resource.Table(TableConfigEnum.COMPANY)

    def get_company_by_id(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a company by its ID.

        Args:
            company_id: The company identifier

        Returns:
            Company data as dictionary or None if not found

        Raises:
            Exception: If DynamoDB operation fails
        """
        try:
            logger.debug(f"Getting company by id: {company_id}")

            response = self.table_company.get_item(
                Key={'id': company_id}
            )

            company = response.get('Item')
            if not company:
                logger.info(f"Company not found for id: {company_id}")
                return None

            logger.debug(f"Company found for id: {company_id}")
            return company

        except ClientError as e:
            logger.error(f"ClientError getting company by id {company_id}: {e}")
            raise CommonException(f"Failed to retrieve company: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error getting company by id {company_id}: {e}")
            raise CommonException(f"Unexpected error retrieving company: {e}") from e

    def get_companies_by_document(self, document: str) -> List[Dict[str, Any]]:
        """Retrieve companies by document number.

        Args:
            document: The document number to search for

        Returns:
            List of company data dictionaries

        Raises:
            Exception: If DynamoDB operation fails
        """
        try:
            logger.debug(f"Getting companies by document: {document}")

            response = self.table_company.query(
                IndexName='document',
                KeyConditionExpression=Key('document').eq(document)
            )

            companies = response.get('Items', [])
            logger.debug(f"Found {len(companies)} companies for document: {document}")

            return companies

        except ClientError as e:
            logger.error(f"ClientError getting companies by document {document}: {e}")
            raise CommonException(f"Failed to retrieve companies by document: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error getting companies by document {document}: {e}")
            raise CommonException(f"Unexpected error retrieving companies by document: {e}") from e

    def put_company(self, payload: Dict[str, Any]) -> None:
        """Create or update a company record.

        Args:
            payload: Company data to store

        Raises:
            Exception: If DynamoDB operation fails
        """
        try:
            company_id = payload.get('id', 'unknown')
            logger.debug(f"Putting company: {company_id}")

            self.table_company.put_item(Item=payload)

            logger.info(f"Company successfully stored: {company_id}")

        except ClientError as e:
            logger.error(f"ClientError putting company: {e}")
            raise CommonException(f"Failed to store company: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error putting company: {e}")
            raise CommonException(f"Unexpected error storing company: {e}") from e