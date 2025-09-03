import logging
from typing import Dict, Any

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from neofin_toobox.configs.enums import TableConfigEnum
from neofin_toobox.exceptions.repositories.roles_repository_exception import RolesRepositoryException, RolesNotFoundException
from neofin_toobox.repositories.dynamodb_repository import DynamoDbRepository

logger = logging.getLogger(__name__)


class RolesRepository(DynamoDbRepository):
    """
    Repository for role operations in DynamoDB.

    Extends DynamoDbRepository to provide role-specific operations
    with proper error handling, validation, and structured logging.
    """
    GSI_INDEX_NAME = 'company_id-role_name'

    def __init__(self):
        """
        Initialize the role repository.
        """
        super().__init__()
        self.table_role = self.resource.Table(TableConfigEnum.ROLES.value)

    def get_role_by_id(self, role_id: str) -> Dict[str, Any]:
        """
        Get role by ID.

        Args:
            role_id: Role ID

        Returns:
            Role data

        Raises:
            RoleNotFoundError: If role is not found
            RoleRepositoryError: For other errors
        """
        if not role_id or not role_id.strip():
            logger.error("Role ID validation failed - empty or None", extra={
                "role_id": role_id,
                "operation": "get_role_by_id"
            })
            raise RolesRepositoryException("Role ID cannot be empty")

        role_id = role_id.strip()

        logger.debug("Starting role retrieval", extra={
            "role_id": role_id,
            "operation": "get_role_by_id"
        })

        try:
            response = self.table_role.get_item(
                Key={'id': role_id},
            )

            role_data = response.get('Item')
            if not role_data:
                logger.warning("Role not found in database", extra={
                    "role_id": role_id,
                    "operation": "get_role_by_id",
                    "error_type": "role_not_found"
                })
                raise RolesNotFoundException(f"Role not found: {role_id}")

            logger.info("Role retrieved successfully", extra={
                "role_id": role_id,
                "operation": "get_role_by_id",
                "role_name": role_data.get('name'),
            })
            return role_data

        except ClientError as e:

            logger.error("ClientError while retrieving role", extra={
                "role_id": role_id,
                "operation": "get_role_by_id",
                "error_message": str(e),
            })

            raise RolesRepositoryException(f"Error retrieving role: {e}")
        except RolesNotFoundException:

            raise
        except Exception as e:
            logger.error("Unexpected error while retrieving role", extra={
                "role_id": role_id,
                "operation": "get_role_by_id",
                "error_message": str(e),
            })
            raise RolesRepositoryException(f"Unexpected error retrieving role: {e}")

    def get_roles_by_company_id_and_name(self, company_id: str, role_name: str):
        company_id = company_id.strip()
        role_name = role_name.strip()
        logger.debug("Starting role lookup by company_id and name", extra={
            "company_id": company_id,
            "role_name": role_name,
            "operation": "get_roles_by_company_id_and_name"
        })
        try:
            response = self.table_role.query(
                IndexName=RolesRepository.GSI_INDEX_NAME,
                KeyConditionExpression=Key('company_id').eq(company_id) & Key('role_name').eq(role_name)
            )

            items = response.get('Items', [])
            role_data = items[0] if items else None
            if role_data:
                logger.info("Role found", extra={
                    "company_id": company_id,
                    "role_name": role_name,
                    "operation": "get_roles_by_company_id_and_name",
                    "role_id": role_data.get("id")
                })
            else:
                logger.warning("Role not found", extra={
                    "company_id": company_id,
                    "role_name": role_name,
                    "operation": "get_roles_by_company_id_and_name"
                })

            return role_data

        except ClientError as e:
            logger.error("ClientError while retrieving role", extra={
                "company_id": company_id,
                "role_name": role_name,
                "operation": "get_roles_by_company_id_and_name",
                "error_message": str(e),
            })

            raise RolesRepositoryException(f"Error retrieving role: {e}")
        except Exception as e:
            logger.error("Unexpected error while retrieving role", extra={
                "company_id": company_id,
                "role_name": role_name,
                "operation": "get_roles_by_company_id_and_name",
                "error_message": str(e),
            })
            raise RolesRepositoryException(f"Unexpected error retrieving role: {e}")

    def put_role(self, payload: Dict[str, Any]) -> None:
        """
        Put role data into DynamoDB.

        Args:
            payload: Role data to be stored

        Raises:
            Exception: If DynamoDB operation fails
        """
        try:
            role_id = payload.get('id', 'unknown')
            logger.debug(f"Putting role: {role_id}")

            self.table_role.put_item(Item=payload)

            logger.info(f"Role successfully stored: {role_id}")

        except ClientError as e:
            logger.error(f"ClientError putting role: {e}")