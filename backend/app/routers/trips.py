import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas import (
    TripGenerationRequest,
    ItineraryResponse,
    DayPlan,
    ActivityItem,
    DayRegenerateRequest,
    ActivitySwapRequest,
    TripUpdateRequest,
    TripListResponse
)
from app.services.ai_planner import (
    generate_itinerary_ai,
    regenerate_single_day_ai,
    swap_single_activity_ai
)
from app.services.supabase_client import (
    DatabaseService,
    SupabaseClientContext,
    get_client
)

logger = logging.getLogger("router.trips")
router = APIRouter()

# ==========================================
# 1. AI ITINERARY GENERATION & MODULAR EDITING
# ==========================================

@router.post("/generate", response_model=ItineraryResponse, summary="Generate Full Personalized Itinerary")
async def generate_trip(
    payload: TripGenerationRequest, 
    db_client: SupabaseClientContext = Depends(get_client)
):
    """
    Orchestrates AI itinerary generation by combining user inputs (destination, dates,
    travel style, budget, group size, dietary & mobility) through prompt engineering.
    Automatically persists the generated itinerary into the database.
    """
    try:
        itinerary = await generate_itinerary_ai(payload)
        saved_itinerary = await DatabaseService.save_trip(itinerary, client=db_client)
        return saved_itinerary
    except Exception as e:
        logger.error(f"Error in generate_trip: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regenerate-day", response_model=DayPlan, summary="Regenerate Single Day with New Vibe")
async def regenerate_day(
    payload: DayRegenerateRequest, 
    db_client: SupabaseClientContext = Depends(get_client)
):
    """
    Regenerates a single day's plan with refined vibe or dietary/accessibility constraints
    without altering the remaining days. Updates database in-place if trip exists.
    """
    try:
        new_day = await regenerate_single_day_ai(payload)
        
        existing_trip = await DatabaseService.get_trip(payload.trip_id, client=db_client)
        if existing_trip:
            updated_days = [
                new_day if d.day_number == payload.day_number else d 
                for d in existing_trip.itinerary
            ]
            await DatabaseService.update_trip(
                payload.trip_id, 
                TripUpdateRequest(itinerary=updated_days), 
                client=db_client
            )

        return new_day
    except Exception as e:
        logger.error(f"Error in regenerate_day: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/swap-activity", response_model=ActivityItem, summary="Swap Individual Activity")
async def swap_activity(
    payload: ActivitySwapRequest, 
    db_client: SupabaseClientContext = Depends(get_client)
):
    """
    Swaps an individual activity with an alternative venue while strictly preserving
    geographic clustering, dietary compliance, and mobility constraints.
    """
    try:
        new_activity = await swap_single_activity_ai(payload)
        
        existing_trip = await DatabaseService.get_trip(payload.trip_id, client=db_client)
        if existing_trip:
            for day in existing_trip.itinerary:
                if day.day_number == payload.day_number:
                    day.activities = [
                        new_activity if a.id == payload.activity_id else a 
                        for a in day.activities
                    ]
            await DatabaseService.update_trip(
                payload.trip_id,
                TripUpdateRequest(itinerary=existing_trip.itinerary),
                client=db_client
            )

        return new_activity
    except Exception as e:
        logger.error(f"Error in swap_activity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 2. CRUD DATABASE OPERATIONS
# ==========================================

@router.get("", response_model=TripListResponse, summary="List Stored Trips")
async def list_trips(
    query: Optional[str] = Query(None, description="Search by title or destination"),
    party_type: Optional[str] = Query(None, description="Filter by solo, couple, group, family"),
    budget_tier: Optional[str] = Query(None, description="Filter by budget, moderate, luxury"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db_client: SupabaseClientContext = Depends(get_client)
):
    """List all stored trips and itineraries from the database with filtering and pagination."""
    try:
        return await DatabaseService.list_trips(
            query=query,
            party_type=party_type,
            budget_tier=budget_tier,
            limit=limit,
            offset=offset,
            client=db_client
        )
    except Exception as e:
        logger.error(f"Error listing trips: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=ItineraryResponse, summary="Save Trip into Storage")
async def save_trip_explicit(
    payload: ItineraryResponse, 
    db_client: SupabaseClientContext = Depends(get_client)
):
    """Save or persist an itinerary into database storage."""
    try:
        return await DatabaseService.save_trip(payload, client=db_client)
    except Exception as e:
        logger.error(f"Error saving trip: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{trip_id}", response_model=ItineraryResponse, summary="Get Trip Details by ID")
async def get_trip_by_id(
    trip_id: str, 
    db_client: SupabaseClientContext = Depends(get_client)
):
    """Retrieve complete day-by-day itinerary and activities by trip ID."""
    trip = await DatabaseService.get_trip(trip_id, client=db_client)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.put("/{trip_id}", response_model=ItineraryResponse, summary="Update Trip")
async def update_trip(
    trip_id: str, 
    payload: TripUpdateRequest, 
    db_client: SupabaseClientContext = Depends(get_client)
):
    """Update trip details (title, summary, notes) or modify entire itinerary plans."""
    updated = await DatabaseService.update_trip(trip_id, payload, client=db_client)
    if not updated:
        raise HTTPException(status_code=404, detail="Trip not found")
    return updated

@router.delete("/{trip_id}", summary="Delete Trip")
async def delete_trip(
    trip_id: str, 
    db_client: SupabaseClientContext = Depends(get_client)
):
    """Delete a trip from persistent storage."""
    deleted = await DatabaseService.delete_trip(trip_id, is_admin=False, client=db_client)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trip not found or already deleted")
    return {"message": "Trip successfully deleted", "trip_id": trip_id}

@router.post("/{trip_id}/duplicate", response_model=ItineraryResponse, summary="Duplicate / Clone Trip")
async def duplicate_trip(
    trip_id: str, 
    db_client: SupabaseClientContext = Depends(get_client)
):
    """Clone an existing trip into a new record for easy experimentation."""
    cloned = await DatabaseService.duplicate_trip(trip_id, client=db_client)
    if not cloned:
        raise HTTPException(status_code=404, detail="Trip not found to duplicate")
    return cloned
