import json
import boto3

from dataclasses import dataclass


@dataclass
class SQSQueue(object):
    queue_url: str
    visibility_timeout: int = 60 * 10
    waiting_timeout: int = 20

    def __post_init__(self):
        self._client = boto3.client('sqs')

    def send_message(
        self,
        payload: dict,
        message_attributes: dict = None,
        delay_seconds: dict = None,
        message_group_id: dict = None,
        message_deduplication_id: dict =None,
    ):
        message_params = {
            'QueueUrl': self.queue_url,
            'MessageBody': json.dumps(payload),
            'MessageAttributes': message_attributes,
            'DelaySeconds': delay_seconds,
            'MessageGroupId': message_group_id,
            'MessageDeduplicationId': message_deduplication_id,
        }
        clean_params = {key: value for key, value in message_params.items() if value}
        return self._client.send_message(**clean_params)

    def delete_message(self, receipt_handle: str):
        return self._client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )

    def fetch_messages(self, num_messages: int = 1) -> list[dict]:
        response = self._client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=num_messages,
            VisibilityTimeout=self.visibility_timeout,
            WaitTimeSeconds=self.waiting_timeout,
        )
        return response.get('Messages', [])