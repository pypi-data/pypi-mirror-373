import boto3

from dataclasses import dataclass
from boto3.dynamodb.conditions import Key


RETURN_VALUES = 'UPDATED_NEW'


@dataclass
class DynamoDBTable(object):
    table_name: str

    def __post_init__(self):
        self._table = boto3.resource('dynamodb').Table(self.table_name)

    def get(self, key: dict):
        return self._table.get_item(Key=key).get('Item')

    def get_all(self):
        return self._table.scan().get('Items')

    def upsert(self, key, attributes):
        return self.put({**key, **attributes})


    def filter_by(self, attribute: str, target_value: str):
        return self._table.query(
            FilterExpression=Key(attribute).eq(target_value),
        ).get('Items')

    def put(self, attributes: dict, condition: dict = None):
        extra_args = {}
        if condition:
            extra_args['ConditionExpression'] = condition
        return self._table.put_item(Item=attributes, **extra_args)


    def update(self, key: str, attributes: dict):
        return self._table.update_item(
            Key=key,
            UpdateExpression=self._update_expression(attributes),
            ExpressionAttributeNames=self._expression_attribute_names(attributes),
            ExpressionAttributeValues=self._expression_attribute_values(attributes),
            ReturnValues=RETURN_VALUES,
        )

    def delete(self, key: dict):
        return self._table.delete_item(Key=key)

    def count(self) -> int:
        return self._table.item_count

    @classmethod
    def _update_expression(cls, attributes):
        return 'SET {param}'.format(
            param=','.join(
                '#{key}=:{key}'.format(
                    key=key,
                )
                for key in attributes
            ),
        )

    @classmethod
    def _expression_attribute_names(cls, attributes):
        return {
            '#{key}'.format(key=key): key for key in attributes
        }

    @classmethod
    def _expression_attribute_values(cls, attributes):
        return {
            ':{key}'.format(key=key): attr for key, attr in attributes.items()
        }
