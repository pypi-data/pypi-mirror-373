import json
import boto3


def invoke_lambda(function_name: str, payload: dict) -> dict | list | None:
    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload),
    )

    return json.loads(response['Payload'].read().decode('utf-8'))