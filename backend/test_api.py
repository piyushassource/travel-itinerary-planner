import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.schemas import (
    TripGenerationRequest,
    DayRegenerateRequest,
    ActivitySwapRequest,
    TripUpdateRequest
)
from app.services.ai_planner import (
    generate_itinerary_ai,
    regenerate_single_day_ai,
    swap_single_activity_ai
)
from app.services.supabase_client import (
    DatabaseService,
    get_client,
    get_service_client
)

async def run_tests():
    print("=" * 65)
    print("RUNNING EXTENDED CRUD & STORAGE TEST SUITE FOR TRAVEL PLANNER")
    print("=" * 65)

    # 1. Test Client Initialization
    print("\n[Test 1] Testing Supabase Client Initialization...")
    public_client = get_client()
    assert public_client.is_admin is False
    service_client = get_service_client()
    print(" -> Public Client initialized successfully.")
    print(f" -> Service Client initialized (is_admin={service_client.is_admin}).")

    # 2. Test Scenario 1 Generation & Auto-Save
    print("\n[Test 2] Scenario 1: Solo Weekend in Tokyo (Generate & Save)...")
    solo_req = TripGenerationRequest(
        destination="Tokyo, Japan",
        days=3,
        party_type="solo",
        party_size=1,
        budget_tier="budget",
        pacing="fast_paced",
        interests=["food", "sightseeing"],
        accommodation_area="Shinjuku"
    )
    solo_itinerary = await generate_itinerary_ai(solo_req)
    saved_trip = await DatabaseService.save_trip(solo_itinerary)
    assert saved_trip.trip_id == solo_itinerary.trip_id
    print(f" -> Generated & Saved Trip: '{saved_trip.trip_title}' (ID: {saved_trip.trip_id})")

    # 3. Test Read (GET)
    print("\n[Test 3] Testing Trip Retrieval (GET /api/trips/{id})...")
    fetched_trip = await DatabaseService.get_trip(saved_trip.trip_id)
    assert fetched_trip is not None
    assert fetched_trip.destination == "Tokyo, Japan"
    print(f" -> Retrieved Trip successfully: {fetched_trip.trip_title}")

    # 4. Test Update (PUT)
    print("\n[Test 4] Testing Trip Update (PUT /api/trips/{id})...")
    updated_title = "Piyush's Solo Tokyo Adventure 2026"
    updated_trip = await DatabaseService.update_trip(
        saved_trip.trip_id,
        TripUpdateRequest(trip_title=updated_title, custom_notes="Include late night Shinjuku ramen")
    )
    assert updated_trip is not None
    assert updated_trip.trip_title == updated_title
    print(f" -> Updated Trip title successfully to: '{updated_trip.trip_title}'")

    # 5. Test Duplicate (POST /duplicate)
    print("\n[Test 5] Testing Trip Duplication (POST /api/trips/{id}/duplicate)...")
    duplicated_trip = await DatabaseService.duplicate_trip(saved_trip.trip_id)
    assert duplicated_trip is not None
    assert duplicated_trip.trip_id != saved_trip.trip_id
    assert "(Copy)" in duplicated_trip.trip_title
    print(f" -> Cloned Trip successfully! New ID: {duplicated_trip.trip_id}")

    # 6. Test List & Filter (GET /api/trips)
    print("\n[Test 6] Testing Trip Listing with Filters (GET /api/trips)...")
    trip_list = await DatabaseService.list_trips(query="Tokyo")
    assert trip_list.total_count >= 2
    print(f" -> Found {trip_list.total_count} trip(s) matching 'Tokyo'.")

    # 7. Test Delete (DELETE /api/trips/{id})
    print("\n[Test 7] Testing Trip Deletion (DELETE /api/trips/{id})...")
    delete_result = await DatabaseService.delete_trip(duplicated_trip.trip_id)
    assert delete_result is True
    check_deleted = await DatabaseService.get_trip(duplicated_trip.trip_id)
    assert check_deleted is None
    print(f" -> Successfully deleted cloned trip {duplicated_trip.trip_id}.")

    # 8. Test Elevated Admin Delete
    print("\n[Test 8] Testing Admin Service Role Delete...")
    admin_del = await DatabaseService.delete_trip(saved_trip.trip_id, is_admin=True)
    assert admin_del is True
    print(" -> Admin service role deletion executed cleanly.")

    print("\n" + "=" * 65)
    print("ALL STORAGE & CRUD TESTS COMPLETED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_tests())
