import logging
from typing import Dict, Any

from botocore.exceptions import ClientError

from neofin_toobox.configs.enums import TableConfigEnum
from neofin_toobox.exceptions.repositories.user_repository_exception import UserRepositoryException, UserNotFoundException
from neofin_toobox.repositories.dynamodb_repository import DynamoDbRepository

logger = logging.getLogger(__name__)


class UserRepository(DynamoDbRepository):
    """
    Repository for user operations in DynamoDB.

    Extends DynamoDbRepository to provide user-specific operations
    with proper error handling, validation, and caching.
    """

    def __init__(self):
        """
            Initialize the user repository.
        """
        super().__init__()
        self.table_user = self.resource.Table(TableConfigEnum.USERS.value)



    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User data

        Raises:
            UserNotFoundError: If user is not found
            UserRepositoryError: For other errors
        """
        if not user_id or not user_id.strip():
            logger.error("User ID validation failed - empty or None", extra={
                "user_id": user_id,
                "operation": "get_user_by_id"
            })
            raise UserRepositoryException("User ID cannot be empty")

        user_id = user_id.strip()

        logger.debug("Starting user retrieval", extra={
            "user_id": user_id,
            "operation": "get_user_by_id"
        })

        try:
            response = self.table_user.get_item(
                Key={'id': user_id},
            )

            user_data = response.get('Item')
            if not user_data:
                logger.warning("User not found in database", extra={
                    "user_id": user_id,
                    "operation": "get_user_by_id",
                    "error_type": "user_not_found"
                })
                raise UserNotFoundException(f"User not found: {user_id}")

            logger.info("User retrieved successfully", extra={
                "user_id": user_id
            })
            return user_data

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))

            logger.error("DynamoDB error while retrieving user", extra={
                "user_id": user_id,
                "operation": "get_user_by_id",
                "error_code": error_code,
                "error_message": error_message,
                "aws_request_id": e.response.get('ResponseMetadata', {}).get('RequestId'),
                "error_type": "dynamodb_client_error"
            })
            raise UserRepositoryException(f"Error retrieving user: {e}") from e
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error("Unexpected error while retrieving user", extra={
                "user_id": user_id,
                "operation": "get_user_by_id",
                "error_type": "unexpected_error",
                "error_message": str(e),
                "exception_class": e.__class__.__name__
            })
            raise UserRepositoryException(f"Unexpected error retrieving user: {e}") from e