import os
import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ.get("TABLE_NAME", "DroneInspectionTable")
DYNAMODB_ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL")  


def _get_table():
    """
    Returns a boto3 DynamoDB Table resource.

    Why a function instead of a module-level constant: Lambda execution
    environments are reused across warm invocations, but building the
    resource lazily like this keeps the module import fast (helps cold
    start) and makes it trivial to point at DynamoDB Local during testing
    via the DYNAMODB_ENDPOINT_URL env var, without touching production code.
    """
    if DYNAMODB_ENDPOINT_URL:
        resource = boto3.resource("dynamodb", endpoint_url=DYNAMODB_ENDPOINT_URL)
    else:
        resource = boto3.resource("dynamodb")
    return resource.Table(TABLE_NAME)


class DynamoRepository:
    """
    Encapsulates all raw DynamoDB operations.
    Services call these methods; they never touch boto3 directly.
    """

    def __init__(self):
        self.table = _get_table()

    def put_item(self, item: dict) -> None:
        self.table.put_item(Item=item)

    def get_warehouse(self, warehouse_id: str) -> dict | None:
        response = self.table.get_item(
            Key={"PK": f"WAREHOUSE#{warehouse_id}"}
        )