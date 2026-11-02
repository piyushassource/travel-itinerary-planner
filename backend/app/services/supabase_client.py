import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import httpx
from app.config import settings
from app.schemas import (
    ItineraryResponse, 
    TripUpdateRequest, 
    TripSummaryItem, 
    TripListResponse,
    DayPlan
)

logger = logging.getLogger("supabase_database")

# In-memory store for seamless offline / zero-setup operation
_LOCAL_STORE: Dict[str, dict] = {}

class SupabaseClientContext:
    """
    Manages HTTP communication with the Supabase PostgREST and Auth APIs.
    Wraps standard anon and elevated service-role privileges.
    """
    def __init__(self, base_url: str, api_key: str, is_admin: bool = False):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.is_admin = is_admin
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    async def get(self, endpoint: str, params: Optional[dict] = None) -> httpx.Response:
        url = f"{self.base_url}/rest/v1/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            return await client.get(url, headers=self.headers, params=params)

    async def post(self, endpoint: str, json_data: Any) -> httpx.Response:
        url = f"{self.base_url}/rest/v1/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            return await client.post(url, headers=self.headers, json=json_data)

    async def patch(self, endpoint: str, json_data: Any, params: Optional[dict] = None) -> httpx.Response:
        url = f"{self.base_url}/rest/v1/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            return await client.patch(url, headers=self.headers, json=json_data, params=params)

    async def delete(self, endpoint: str, params: Optional[dict] = None) -> httpx.Response:
        url = f"{self.base_url}/rest/v1/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            return await client.delete(url, headers=self.headers, params=params)


# Reusable client factories (FastAPI Dependency Injection ready)
def get_client() -> SupabaseClientContext:
    """
    Provides standard public/anon Supabase client for user-scoped operations.
    Enforces Row Level Security (RLS) on PostgreSQL.
    """
    return SupabaseClientContext(
        base_url=settings.SUPABASE_URL,
        api_key=settings.SUPABASE_ANON_KEY,
        is_admin=False
    )

def get_service_client() -> SupabaseClientContext:
    """
    Provides elevated service-role Supabase client for backend/admin operations.
    Bypasses RLS for administrative maintenance, bulk cleanup, and system queries.
    """
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    return SupabaseClientContext(
        base_url=settings.SUPABASE_URL,
        api_key=key,
        is_admin=bool(settings.SUPABASE_SERVICE_ROLE_KEY)
    )


class DatabaseService:
    """
    Centralized database layer for trip persistence and CRUD operations.
    Acts as the primary data orchestrator between FastAPI and Supabase.
    """

    @classmethod
    async def save_trip(cls, trip: ItineraryResponse, client: Optional[SupabaseClientContext] = None) -> ItineraryResponse:
        """
        Saves or inserts a new trip and its itinerary into persistent storage.
        """
        client = client or get_client()
        now_iso = datetime.now(timezone.utc).isoformat()
        
        trip_dict = trip.model_dump()
        trip_dict["created_at"] = trip_dict.get("created_at") or now_iso
        trip_dict["updated_at"] = now_iso
        
        # Save to local store
        _LOCAL_STORE[trip.trip_id] = trip_dict

        # Persist to Supabase if configured
        if client.is_configured():
            try:
                # 1. Upsert into 'trips' table
                res = await client.post("trips", {
                    "id": trip.trip_id,
                    "title": trip.trip_title,
                    "destination": trip.destination,
                    "party_type": trip.party_type,
                    "party_size": trip.party_size,
                    "budget_tier": trip.budget_tier,
                    "pacing": trip.pacing,
                    "estimated_total_cost": trip.estimated_total_cost_usd,
                    "raw_ai_response": trip_dict,
                    "created_at": trip_dict["created_at"],
                    "updated_at": trip_dict["updated_at"]
                })
                if res.status_code not in (200, 201):
                    logger.warning(f"Supabase save trip non-200: {res.status_code} {res.text}")
            except Exception as e:
                logger.error(f"Error persisting trip to Supabase: {e}")

        return ItineraryResponse(**trip_dict)

    @classmethod
    async def get_trip(cls, trip_id: str, client: Optional[SupabaseClientContext] = None) -> Optional[ItineraryResponse]:
        """
        Retrieves a complete trip by its unique ID.
        """
        # Check local store first
        if trip_id in _LOCAL_STORE:
            return ItineraryResponse(**_LOCAL_STORE[trip_id])

        client = client or get_client()
        if client.is_configured():
            try:
                res = await client.get("trips", params={"id": f"eq.{trip_id}", "select": "*"})
                if res.status_code == 200 and res.json():
                    row = res.json()[0]
                    raw = row.get("raw_ai_response")
                    if raw:
                        _LOCAL_STORE[trip_id] = raw
                        return ItineraryResponse(**raw)
            except Exception as e:
                logger.error(f"Error fetching trip from Supabase: {e}")

        return None

    @classmethod
    async def list_trips(
        cls, 
        query: Optional[str] = None,
        party_type: Optional[str] = None,
        budget_tier: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        client: Optional[SupabaseClientContext] = None
    ) -> TripListResponse:
        """
        Lists stored trips with optional search and filter criteria.
        """
        all_trips: List[dict] = []
        client = client or get_client()

        if client.is_configured():
            try:
                params = {"select": "*", "order": "created_at.desc", "limit": str(limit), "offset": str(offset)}
                if party_type:
                    params["party_type"] = f"eq.{party_type}"
                if budget_tier:
                    params["budget_tier"] = f"eq.{budget_tier}"
                if query:
                    params["destination"] = f"ilike.*{query}*"

                res = await client.get("trips", params=params)
                if res.status_code == 200:
                    for row in res.json():
                        raw = row.get("raw_ai_response")
                        if raw:
                            all_trips.append(raw)
            except Exception as e:
                logger.error(f"Error listing trips from Supabase: {e}")

        # Fallback / merge with local store
        if not all_trips:
            local_items = list(_LOCAL_STORE.values())
            # Reverse chronological
            local_items.reverse()
            for item in local_items:
                if party_type and item.get("party_type") != party_type:
                    continue
                if budget_tier and item.get("budget_tier") != budget_tier:
                    continue
                if query:
                    q = query.lower()
                    dest = item.get("destination", "").lower()
                    title = item.get("trip_title", "").lower()
                    if q not in dest and q not in title:
                        continue
                all_trips.append(item)

        summaries: List[TripSummaryItem] = []
        for t in all_trips[offset:offset + limit]:
            summaries.append(TripSummaryItem(
                trip_id=t.get("trip_id", ""),
                trip_title=t.get("trip_title", "Untitled Trip"),
                destination=t.get("destination", "Unknown"),
                total_days=t.get("total_days", len(t.get("itinerary", []))),
                party_type=t.get("party_type", "solo"),
                party_size=t.get("party_size", 1),
                budget_tier=t.get("budget_tier", "moderate"),
                pacing=t.get("pacing", "moderate"),
                estimated_total_cost_usd=float(t.get("estimated_total_cost_usd", 0.0)),
                cost_per_person_usd=float(t.get("cost_per_person_usd", 0.0)),
                created_at=t.get("created_at"),
                summary=t.get("summary")
            ))

        return TripListResponse(trips=summaries, total_count=len(all_trips))

    @classmethod
    async def update_trip(
        cls, 
        trip_id: str, 
        updates: TripUpdateRequest, 
        client: Optional[SupabaseClientContext] = None
    ) -> Optional[ItineraryResponse]:
        """
        Updates an existing trip's details or entire itinerary plan.
        """
        existing = await cls.get_trip(trip_id, client=client)
        if not existing:
            return None

        client = client or get_client()
        updated_dict = existing.model_dump()
        now_iso = datetime.now(timezone.utc).isoformat()
        updated_dict["updated_at"] = now_iso

        update_data = updates.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            if v is not None:
                updated_dict[k] = v

        # Recalculate totals if itinerary was updated
        if "itinerary" in update_data and update_data["itinerary"]:
            days = updated_dict["itinerary"]
            cost_per_p = sum(d.get("day_estimated_cost_usd", 0) for d in days)
            updated_dict["cost_per_person_usd"] = round(cost_per_p, 2)
            updated_dict["estimated_total_cost_usd"] = round(cost_per_p * updated_dict.get("party_size", 1), 2)
            updated_dict["total_days"] = len(days)

        _LOCAL_STORE[trip_id] = updated_dict

        if client.is_configured():
            try:
                await client.patch("trips", {
                    "title": updated_dict.get("trip_title"),
                    "destination": updated_dict.get("destination"),
                    "budget_tier": updated_dict.get("budget_tier"),
                    "pacing": updated_dict.get("pacing"),
                    "estimated_total_cost": updated_dict.get("estimated_total_cost_usd"),
                    "raw_ai_response": updated_dict,
                    "updated_at": now_iso
                }, params={"id": f"eq.{trip_id}"})
            except Exception as e:
                logger.error(f"Error updating trip in Supabase: {e}")

        return ItineraryResponse(**updated_dict)

    @classmethod
    async def delete_trip(
        cls, 
        trip_id: str, 
        is_admin: bool = False,
        client: Optional[SupabaseClientContext] = None
    ) -> bool:
        """
        Deletes a trip from the database.
        Admin client can delete any trip with elevated permissions.
        """
        existed = trip_id in _LOCAL_STORE
        _LOCAL_STORE.pop(trip_id, None)

        client = client or (get_service_client() if is_admin else get_client())
        if client.is_configured():
            try:
                res = await client.delete("trips", params={"id": f"eq.{trip_id}"})
                return res.status_code in (200, 204)
            except Exception as e:
                logger.error(f"Error deleting trip from Supabase: {e}")

        return existed

    @classmethod
    async def duplicate_trip(cls, trip_id: str, client: Optional[SupabaseClientContext] = None) -> Optional[ItineraryResponse]:
        """
        Duplicates an existing trip, assigning a fresh UUID and timestamp.
        """
        original = await cls.get_trip(trip_id, client=client)
        if not original:
            return None

        new_dict = original.model_dump()
        new_dict["trip_id"] = str(uuid.uuid4())
        new_dict["trip_title"] = f"{original.trip_title} (Copy)"
        now_iso = datetime.now(timezone.utc).isoformat()
        new_dict["created_at"] = now_iso
        new_dict["updated_at"] = now_iso

        return await cls.save_trip(ItineraryResponse(**new_dict), client=client)
