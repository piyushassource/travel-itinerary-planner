import json
import logging
import uuid
from typing import Optional
from app.config import settings
from app.schemas import (
    TripGenerationRequest,
    ItineraryResponse,
    DayPlan,
    ActivityItem,
    DayRegenerateRequest,
    ActivitySwapRequest
)
from app.prompts.templates import (
    SYSTEM_ITINERARY_PROMPT,
    build_generate_prompt,
    build_regenerate_day_prompt,
    build_swap_activity_prompt
)
from app.services.heuristics import (
    generate_heuristic_itinerary,
    regenerate_heuristic_day,
    swap_heuristic_activity
)

logger = logging.getLogger("ai_planner")

async def generate_itinerary_ai(req: TripGenerationRequest) -> ItineraryResponse:
    """Generates an itinerary using Gemini / OpenAI LLM, with graceful fallback to heuristics."""
    prompt = build_generate_prompt(
        destination=req.destination,
        days=req.days,
        party_type=req.party_type,
        party_size=req.party_size,
        budget_tier=req.budget_tier,
        pacing=req.pacing,
        interests=req.interests,
        travel_dates=req.travel_dates,
        dietary_restrictions=req.dietary_restrictions,
        mobility_level=req.mobility_level,
        accommodation_area=req.accommodation_area,
        custom_notes=req.custom_notes
    )

    # 1. Try Gemini if configured
    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.DEFAULT_MODEL,
                contents=f"{SYSTEM_ITINERARY_PROMPT}\n\n{prompt}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ItineraryResponse
                }
            )
            data = json.loads(response.text)
            if not data.get("trip_id"):
                data["trip_id"] = str(uuid.uuid4())
            data["dietary_restrictions"] = req.dietary_restrictions
            data["mobility_level"] = req.mobility_level
            data["travel_dates"] = req.travel_dates
            return ItineraryResponse(**data)
        except Exception as e:
            logger.warning(f"Gemini generation failed, falling back to heuristics: {e}")

    # 2. Try OpenAI if configured
    if settings.OPENAI_API_KEY:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                res = await http_client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": SYSTEM_ITINERARY_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"}
                    }
                )
                if res.status_code == 200:
                    raw_json = res.json()["choices"][0]["message"]["content"]
                    data = json.loads(raw_json)
                    if not data.get("trip_id"):
                        data["trip_id"] = str(uuid.uuid4())
                    data["dietary_restrictions"] = req.dietary_restrictions
                    data["mobility_level"] = req.mobility_level
                    data["travel_dates"] = req.travel_dates
                    return ItineraryResponse(**data)
        except Exception as e:
            logger.warning(f"OpenAI generation failed, falling back to heuristics: {e}")

    # 3. Resilient fallback generator (ensures zero crashes and full immediate interactivity)
    return generate_heuristic_itinerary(req)

async def regenerate_single_day_ai(req: DayRegenerateRequest) -> DayPlan:
    """Regenerates a single day with new preference while preserving the rest of the trip."""
    prompt = build_regenerate_day_prompt(
        destination=req.destination,
        day_number=req.day_number,
        current_theme=req.current_theme,
        new_preference_or_vibe=req.new_preference_or_vibe,
        budget_tier=req.budget_tier,
        party_type=req.party_type,
        dietary_restrictions=req.dietary_restrictions,
        mobility_level=req.mobility_level
    )

    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.DEFAULT_MODEL,
                contents=f"{SYSTEM_ITINERARY_PROMPT}\n\n{prompt}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": DayPlan
                }
            )
            data = json.loads(response.text)
            return DayPlan(**data)
        except Exception as e:
            logger.warning(f"Gemini single day regen failed: {e}")

    return regenerate_heuristic_day(req)

async def swap_single_activity_ai(req: ActivitySwapRequest) -> ActivityItem:
    """Swaps an individual activity for an alternative preserving geographic cluster."""
    prompt = build_swap_activity_prompt(
        destination=req.destination,
        neighborhood=req.neighborhood,
        category=req.activity_category,
        reason=req.reason or "Alternative venue preference",
        budget_tier=req.budget_tier,
        dietary_restrictions=req.dietary_restrictions,
        mobility_level=req.mobility_level
    )

    if settings.GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.DEFAULT_MODEL,
                contents=f"{SYSTEM_ITINERARY_PROMPT}\n\n{prompt}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ActivityItem
                }
            )
            data = json.loads(response.text)
            return ActivityItem(**data)
        except Exception as e:
            logger.warning(f"Gemini activity swap failed: {e}")

    return swap_heuristic_activity(req)
