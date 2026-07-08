"""
Quick local end-to-end test — exercises the service layer directly
(bypassing Lambda/API Gateway plumbing) against DynamoDB Local.
"""

from src.services.inspection_service import InspectionService
from src.services.image_service import ImageService
from src.utils.exceptions import AppError

WAREHOUSE_ID = "wh-001"
DRONE_ID = "drone-001"

print("=" * 60)
print("TEST 1: Create Inspection")
print("=" * 60)
inspection_service = InspectionService()
inspection = inspection_service.create_inspection(
    warehouse_id=WAREHOUSE_ID,
    drone_id=DRONE_ID,
    notes="Routine quarterly inspection",
)
print(inspection.to_response_dict())
inspection_id = inspection.inspection_id

print("\n" + "=" * 60)
print("TEST 2: List Inspections by Warehouse")
print("=" * 60)
results = inspection_service.list_by_warehouse(WAREHOUSE_ID)
for r in results:
    print(r.to_response_dict())

print("\n" + "=" * 60)
print("TEST 3: List Inspections by Drone")
print("=" * 60)
results = inspection_service.list_by_drone(DRONE_ID)
for r in results:
    print(r.to_response_dict())

print("\n" + "=" * 60)
print("TEST 4: Create Inspection with INVALID warehouse (should fail with 404)")
print("=" * 60)
try:
    inspection_service.create_inspection(warehouse_id="fake-wh", drone_id=DRONE_ID)
    print("FAILED: should have raised NotFoundError")
except AppError as e:
    print(f"PASSED: correctly raised {e.__class__.__name__} ({e.status_code}): {e.message}")

print("\n" + "=" * 60)
print("TEST 5: Generate Upload URL (requires local S3 mock - may fail, see note below)")
print("=" * 60)
try:
    image_service = ImageService()
    result = image_service.generate_upload_url(inspection_id)
    print(result)
except Exception as e:
    print(f"Expected to fail without local S3 running: {e}")

print("\n" + "=" * 60)
print("TEST 6: List Images for Inspection")
print("=" * 60)
image_service = ImageService()
images = image_service.list_images(inspection_id)
for img in images:
    print(img.to_response_dict())

print("\nAll core tests completed.")
