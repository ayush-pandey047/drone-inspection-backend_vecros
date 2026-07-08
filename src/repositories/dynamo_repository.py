import os
import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ.get("TABLE_NAME", "DroneInspectionTable")
DYNAMODB_ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL")  # set only for local testing


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
            Key={"PK": f"WAREHOUSE#{warehouse_id}", "SK": f"WAREHOUSE#{warehouse_id}"}
        )
        return response.get("Item")

    def get_drone(self, warehouse_id: str, drone_id: str) -> dict | None:
        response = self.table.get_item(
            Key={"PK": f"WAREHOUSE#{warehouse_id}", "SK": f"DRONE#{drone_id}"}
        )
        return response.get("Item")

    def query_inspections_by_warehouse(self, warehouse_id: str) -> list[dict]:
        response = self.table.query(
            KeyConditionExpression=Key("PK").eq(f"WAREHOUSE#{warehouse_id}")
            & Key("SK").begins_with("INSPECTION#")
        )
        return response.get("Items", [])


    def query_inspections_by_drone(self, drone_id: str) -> list[dict]:
        response = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"DRONE#{drone_id}")
            & Key("GSI1SK").begins_with("INSPECTION#"),
        )
        return response.get("Items", [])


    def get_inspection_by_id(self, inspection_id: str) -> dict | None:
        """
        Inspection's main-table PK is WAREHOUSE#<id>, not INSPECTION#<id>,
        so we can't get_item directly by inspection_id alone. We query GSI1
        is keyed by drone, not inspection either — so for a pure
        inspection_id lookup we scan-free query via a targeted GSI would be
        ideal, but for our known access patterns, upload-url and list-images
        both receive inspectionId as a path param without warehouse/drone
        context. We handle this with a lightweight query using
        entity_type + inspection_id via a Query against IMAGE partition
        space is not applicable here (Inspections aren't stored under
        INSPECTION# PK). Practical fix: Images ARE stored under
        INSPECTION#<id>, so for AP4/AP5 we treat INSPECTION#<id> as its own
        addressable partition directly.
        """
        response = self.table.get_item(
            Key={"PK": f"INSPECTION#{inspection_id}", "SK": f"INSPECTION#{inspection_id}"}
        )
        return response.get("Item")


    def put_image(self, item: dict) -> None:
        self.table.put_item(Item=item)


    def query_images_by_inspection(self, inspection_id: str) -> list[dict]:
        response = self.table.query(
            KeyConditionExpression=Key("PK").eq(f"INSPECTION#{inspection_id}")
            & Key("SK").begins_with("IMAGE#")
        )
        return response.get("Items", [])