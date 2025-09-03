from abc import ABC
from typing import Dict, Any, List

import boto3


class DynamoDbRepository(ABC):
    def __init__(self):
        self.client = boto3.client(
            "dynamodb"
        )
        self.resource = boto3.resource(
            "dynamodb"
        )


    @staticmethod
    def _paginated_query(table, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Reutilizável para realizar queries paginadas no DynamoDB.
        """
        items = []
        response = table.query(**query_params)

        items.extend(response.get('Items', []))

        while 'LastEvaluatedKey' in response:
            query_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = table.query(**query_params)
            items.extend(response.get('Items', []))

        return items
