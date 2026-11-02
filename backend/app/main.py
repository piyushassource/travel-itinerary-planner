import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
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
    get_client,
    get_service_client
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(
    title=settings.APP_NAME,
    description="Full-stack AI-powered Personalized Travel Itinerary Planner with Supabase CRUD Storage",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "ai_provider": "Gemini" if settings.GEMINI_API_KEY else ("OpenAI" if settings.OPENAI_API_KEY else "HeuristicEngine"),
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY),
        "service_role_configured": bool(settings.SUPABASE_SERVICE_ROLE_KEY)
    }

# ==========================================
# 1. AI GENERATION & MODULAR EDITING ROUTES
# ==========================================

@app.post("/api/trips/generate", response_model=ItineraryResponse)
async def generate_trip(payload: TripGenerationRequest, db_client: SupabaseClientContext = Depends(get_client)):
    """
    Generate a full personalized travel itinerary based on preferences,
    budget, and party type, then securely persist it to the database.
    """
    try:
        itinerary = await generate_itinerary_ai(payload)
        saved_itinerary = await DatabaseService.save_trip(itinerary, client=db_client)
        return saved_itinerary
    except Exception as e:
        logger.error(f"Error in generate_trip: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trips/regenerate-day", response_model=DayPlan)
async def regenerate_day(payload: DayRegenerateRequest, db_client: SupabaseClientContext = Depends(get_client)):
    """
    Regenerate a single day with a new vibe or constraint (Scenario 2: Couple refinement).
    Automatically updates the database record if the trip exists.
    """
    try:
        new_day = await regenerate_single_day_ai(payload)
        
        # If trip is in database, update the day in place
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

@app.post("/api/trips/swap-activity", response_model=ActivityItem)
async def swap_activity(payload: ActivitySwapRequest, db_client: SupabaseClientContext = Depends(get_client)):
    """
    Swap an individual activity with an alternative venue while preserving
    geographic clustering, updating persistent database storage.
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
# 2. FULL CRUD DATABASE MANAGEMENT ROUTES
# ==========================================

@app.get("/api/trips", response_model=TripListResponse)
async def list_trips(
    query: Optional[str] = Query(None, description="Search by title or destination"),
    party_type: Optional[str] = Query(None, description="Filter by solo, couple, group, family"),
    budget_tier: Optional[str] = Query(None, description="Filter by budget, moderate, luxury"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db_client: SupabaseClientContext = Depends(get_client)
):
    """
    List all stored trips and itineraries from the database with filtering and pagination.
    """
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

@app.post("/api/trips", response_model=ItineraryResponse)
async def save_trip_explicit(payload: ItineraryResponse, db_client: SupabaseClientContext = Depends(get_client)):
    """
    Save or persist a trip into database storage.
    """
    try:
        return await DatabaseService.save_trip(payload, client=db_client)
    except Exception as e:
        logger.error(f"Error saving trip: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trips/{trip_id}", response_model=ItineraryResponse)
async def get_trip_by_id(trip_id: str, db_client: SupabaseClientContext = Depends(get_client)):
    """
    Retrieve complete day-by-day itinerary and activities by trip ID.
    """
    trip = await DatabaseService.get_trip(trip_id, client=db_client)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@app.put("/api/trips/{trip_id}", response_model=ItineraryResponse)
async def update_trip(trip_id: str, payload: TripUpdateRequest, db_client: SupabaseClientContext = Depends(get_client)):
    """
    Update trip details (title, summary, notes) or modify entire itinerary plans.
    """
    updated = await DatabaseService.update_trip(trip_id, payload, client=db_client)
    if not updated:
        raise HTTPException(status_code=404, detail="Trip not found")
    return updated

@app.delete("/api/trips/{trip_id}")
async def delete_trip(trip_id: str, db_client: SupabaseClientContext = Depends(get_client)):
    """
    Delete a trip from persistent storage.
    """
    deleted = await DatabaseService.delete_trip(trip_id, is_admin=False, client=db_client)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trip not found or already deleted")
    return {"message": "Trip successfully deleted", "trip_id": trip_id}

@app.post("/api/trips/{trip_id}/duplicate", response_model=ItineraryResponse)
async def duplicate_trip(trip_id: str, db_client: SupabaseClientContext = Depends(get_client)):
    """
    Clone an existing trip into a new record for easy experimentation.
    """
    cloned = await DatabaseService.duplicate_trip(trip_id, client=db_client)
    if not cloned:
        raise HTTPException(status_code=404, detail="Trip not found to duplicate")
    return cloned

# ==========================================
# 3. ADMIN-LEVEL SERVICE ROLE ROUTES
# ==========================================

@app.delete("/api/admin/trips/{trip_id}")
async def admin_delete_trip(trip_id: str, service_client: SupabaseClientContext = Depends(get_service_client)):
    """
    Elevated Admin route: Delete trip bypassing RLS using service-role client.
    """
    deleted = await DatabaseService.delete_trip(trip_id, is_admin=True, client=service_client)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Admin deleted trip successfully", "trip_id": trip_id, "admin": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
