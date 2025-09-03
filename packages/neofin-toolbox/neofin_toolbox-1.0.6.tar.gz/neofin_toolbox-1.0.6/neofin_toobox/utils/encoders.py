import json
from decimal import Decimal

from boto3.dynamodb.types import TypeDeserializer

deserializer = TypeDeserializer()

def deserialize_item(item):
    return {k: deserializer.deserialize(v) for k, v in item.items()}


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if len(str(obj)) == 10:
                return int(obj)
            return str(obj)
        return json.JSONEncoder.default(self, obj)