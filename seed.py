"""
Seeds DynamoDB Local with a test Warehouse and Drone so that
create_inspection has valid referential data to check against.

Run this ONCE after starting DynamoDB Local and creating the table:
    python seed.py
"""

import boto3

TABLE_NAME = "DroneInspectionTable"
DYNAMODB_ENDPOINT_URL = "http://localhost:8000"

WAREHOUSE_ID = "wh-001"
DRONE_ID = "drone-001"


def seed():
    dynamodb = boto3.resource("dynamodb", endpoint_url=DYNAMODB_ENDPOINT_URL)
    table = dynamodb.Table(TABLE_NAME)

    # Warehouse item: PK == SK == WAREHOUSE#<id>, matching how
    # InspectionService.get_warehouse() looks it up.
    table.put_item(
        Item={
            "PK": f"WAREHOUSE#{WAREHOUSE_ID}",
            "SK": f"WAREHOUSE#{WAREHOUSE_ID}",
            "entity_type": "WAREHOUSE",
            "warehouse_id": WAREHOUSE_ID,
            "name": "Pune Central Warehouse",
            "location": "Pune, Maharashtra",
        }
    )
    print(f"Seeded Warehouse: {WAREHOUSE_ID}")

    # Drone item: lives UNDER the warehouse partition (PK = WAREHOUSE#<id>,
    # SK = DRONE#<id>), matching InspectionService.get_drone().
    table.put_item(
        Item={
            "PK": f"WAREHOUSE#{WAREHOUSE_ID}",
            "SK": f"DRONE#{DRONE_ID}",
            "entity_type": "DRONE",
            "drone_id": DRONE_ID,
            "warehouse_id": WAREHOUSE_ID,
            "model": "DJI Matrice 300",
            "status": "ACTIVE",
        }
    )
    print(f"Seeded Drone: {DRONE_ID} under Warehouse: {WAREHOUSE_ID}")

    print("\nSeed complete. Use these IDs in your test requests:")
    print(f"  warehouse_id = {WAREHOUSE_ID}")
    print(f"  drone_id     = {DRONE_ID}")


if __name__ == "__main__":
    seed()