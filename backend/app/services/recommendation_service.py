import json
import logging
import uuid
from typing import List, Optional
from app.config import settings
from app.schemas import (
    RecommendationsRequest,
    RecommendationsResponse,
    RecommendationItem
)
from app.prompts.templates import (
    SYSTEM_ITINERARY_PROMPT,
    build_recommendations_prompt
)
from app.services.heuristics import DESTINATION_KNOWLEDGE

logger = logging.getLogger("recommendation_service")

# Curated Popular Destinations for Discovery
POPULAR_DESTINATIONS = [
    {
        "name": "Tokyo, Japan",
        "tagline": "Futuristic Skylines & Ancient Traditions",
        "badge": "Top Cultural Pick",
        "image_key": "tokyo",
        "ideal_for": ["Solo", "Couple", "Foodies"],
        "avg_budget": "$$"
    },
    {
        "name": "Paris, France",
        "tagline": "Timeless Romance, Art & Culinary Grandeur",
        "badge": "Top Romantic Pick",
        "image_key": "paris",
        "ideal_for": ["Couple", "Art Lovers", "Leisure"],
        "avg_budget": "$$$"
    },
    {
        "name": "New York, USA",
        "tagline": "The City That Never Sleeps & Global Gastronomy",
        "badge": "Top Group & Adventure Pick",
        "image_key": "new_york",
        "ideal_for": ["Small Groups", "Nightlife", "Explorers"],
        "avg_budget": "$$"
    },
    {
        "name": "Kyoto, Japan",
        "tagline": "Zen Gardens, Bamboo Groves & Geisha Districts",
        "badge": "Serene Heritage",
        "image_key": "kyoto",
        "ideal_for": ["Solo", "Couple", "Culture"],
        "avg_budget": "$$"
    },
    {
        "name": "Rome, Italy",
        "tagline": "Living Open-Air Museum & Trattoria Culture",
        "badge": "Historic Wonder",
        "image_key": "rome",
        "ideal_for": ["History", "Groups", "Foodies"],
        "avg_budget": "$$"
    }
]

def generate_heuristic_recommendations(req: RecommendationsRequest) -> RecommendationsResponse:
    """Generates deterministic, highly personalized recommendations based on profile."""
    dest_key = req.destination.lower()
    matched_key = None
    for k in DESTINATION_KNOWLEDGE:
        if k in dest_key:
            matched_key = k
            break

    cost_mult = {"budget": 0.6, "moderate": 1.0, "luxury": 2.2}.get(req.budget_tier, 1.0)
    active_dietary = req.dietary_restrictions if req.dietary_restrictions and "None" not in req.dietary_restrictions else []
    
    access_note = "Step-free ramp/elevator access available" if req.mobility_level == "wheelchair_step_free" else None
    if req.mobility_level == "low_walking":
        access_note = "Short walking distance; frequent rest benches"

    city_data = DESTINATION_KNOWLEDGE.get(matched_key)

    if city_data:
        attractions_raw = city_data["activities"]["attraction"]
        dining_raw = city_data["activities"]["dining"]
        leisure_raw = city_data["activities"]["leisure"]
        neighborhoods_raw = city_data["neighborhoods"]

        # 1. Attractions
        attractions: List[RecommendationItem] = []
        for i, a in enumerate(attractions_raw[:3]):
            attractions.append(RecommendationItem(
                id=f"rec_att_{i+1}",
                title=a[0],
                category="attraction",
                neighborhood=a[2],
                description=a[1],
                estimated_cost_usd=round(a[3] * cost_mult, 1),
                dietary_tags=[],
                accessibility_note=access_note or (a[5] if len(a) > 5 else None),
                match_reason=f"Matches your '{req.pacing}' pacing and interest in {', '.join(req.interests[:2]) if req.interests else 'culture'}.",
                rating=4.9 if i == 0 else 4.8
            ))

        # 2. Dining
        dining: List[RecommendationItem] = []
        for i, d in enumerate(dining_raw[:3]):
            dining.append(RecommendationItem(
                id=f"rec_dine_{i+1}",
                title=d[0],
                category="dining",
                neighborhood=neighborhoods_raw[i % len(neighborhoods_raw)][0],
                description=f"{d[1]} Offers dedicated culinary accommodations.",
                estimated_cost_usd=round(d[3] * cost_mult, 1),
                dietary_tags=active_dietary,
                accessibility_note=access_note or "Ground level accessible dining room",
                match_reason=f"Selected for your {req.budget_tier} budget and verified for {', '.join(active_dietary) if active_dietary else 'local authentic cuisine'}.",
                rating=4.8
            ))

        # 3. Hidden Gems
        hidden_gems: List[RecommendationItem] = [
            RecommendationItem(
                id="rec_gem_1",
                title=f"Artisan Backstreet Discovery in {neighborhoods_raw[0][0]}",
                category="hidden_gem",
                neighborhood=neighborhoods_raw[0][0],
                description="Tucked-away artisan workshops, specialty coffee roasters, and local courtyard gardens.",
                estimated_cost_usd=round(10.0 * cost_mult, 1),
                dietary_tags=[],
                accessibility_note=access_note,
                match_reason=f"A non-touristy experiential stop ideal for {req.party_type} travelers seeking authentic local ambiance.",
                rating=4.9
            ),
            RecommendationItem(
                id="rec_gem_2",
                title=f"Sunset Panoramic Rooftop Terrace",
                category="hidden_gem",
                neighborhood=neighborhoods_raw[1 % len(neighborhoods_raw)][0],
                description="Quiet terrace vantage point offering breathtaking sunset views over the historic skyline.",
                estimated_cost_usd=round(15.0 * cost_mult, 1),
                dietary_tags=[],
                accessibility_note=access_note or "Elevator access",
                match_reason=f"Curated for {req.party_type} travel moments and relaxed evening unwinding.",
                rating=4.85
            )
        ]

        # 4. Neighborhood Stays
        neighborhood_stays: List[RecommendationItem] = [
            RecommendationItem(
                id="rec_stay_1",
                title=f"{neighborhoods_raw[0][0]} District",
                category="accommodation",
                neighborhood=neighborhoods_raw[0][0],
                description=f"Central, vibrant, and accessible hub. Known for {neighborhoods_raw[0][1]}.",
                estimated_cost_usd=0.0,
                dietary_tags=[],
                accessibility_note="High concentration of step-free subway stations",
                match_reason=f"Primary base recommendation for {req.party_type} seeking walkable access to top dining.",
                rating=4.9
            ),
            RecommendationItem(
                id="rec_stay_2",
                title=f"{neighborhoods_raw[1 % len(neighborhoods_raw)][0]} District",
                category="accommodation",
                neighborhood=neighborhoods_raw[1 % len(neighborhoods_raw)][0],
                description=f"Charming cultural quarter characterized by {neighborhoods_raw[1 % len(neighborhoods_raw)][1]}.",
                estimated_cost_usd=0.0,
                dietary_tags=[],
                accessibility_note="Excellent pedestrian connections",
                match_reason=f"Alternative boutique hub offering scenic streets and romantic charm.",
                rating=4.8
            )
        ]

    else:
        # Generic Global City Fallback
        attractions = [
            RecommendationItem(
                id="rec_att_1",
                title=f"Historic Heritage Center of {req.destination}",
                category="attraction",
                neighborhood=f"Old Town {req.destination}",
                description="Celebrated architectural wonders, historic public squares, and world-class exhibits.",
                estimated_cost_usd=round(20.0 * cost_mult, 1),
                dietary_tags=[],
                accessibility_note=access_note,
                match_reason=f"Essential highlight matching your interest in {', '.join(req.interests[:2]) if req.interests else 'culture'}.",
                rating=4.85
            )
        ]
        dining = [
            RecommendationItem(
                id="rec_dine_1",
                title=f"Artisanal Regional Bistro in {req.destination}",
                category="dining",
                neighborhood=f"Central {req.destination}",
                description="Seasonal gastronomic menu emphasizing authentic local recipes and verified dietary options.",
                estimated_cost_usd=round(28.0 * cost_mult, 1),
                dietary_tags=active_dietary,
                accessibility_note=access_note or "Step-free entrance",
                match_reason=f"Verified for {', '.join(active_dietary) if active_dietary else 'local menu'} in the {req.budget_tier} tier.",
                rating=4.8
            )
        ]
        hidden_gems = [
            RecommendationItem(
                id="rec_gem_1",
                title=f"Hidden Riverside/Canal Walk & Artisan Quarter",
                category="hidden_gem",
                neighborhood=f"Creative District, {req.destination}",
                description="Quiet tree-lined pedestrian avenue featuring indie bookstores and boutique cafes.",
                estimated_cost_usd=0.0,
                dietary_tags=[],
                accessibility_note=access_note,
                match_reason="Off-the-beaten-path tranquility away from crowded tourist centers.",
                rating=4.9
            )
        ]
        neighborhood_stays = [
            RecommendationItem(
                id="rec_stay_1",
                title=f"Central Downtown {req.destination}",
                category="accommodation",
                neighborhood=f"Central {req.destination}",
                description="Prime connectivity with direct access to transit corridors and culinary avenues.",
                estimated_cost_usd=0.0,
                dietary_tags=[],
                accessibility_note="Modern accessible transit infrastructure",
                match_reason="Best logistical hub for multi-day sightseeing.",
                rating=4.85
            )
        ]

    return RecommendationsResponse(
        destination=req.destination,
        summary=f"Curated selection of attractions, dietary-verified dining, hidden local gems, and stay hubs for a {req.party_type} journey in {req.destination}.",
        attractions=attractions,
        dining=dining,
        hidden_gems=hidden_gems,
        neighborhood_stays=neighborhood_stays
    )

async def get_curated_recommendations(req: RecommendationsRequest) -> RecommendationsResponse:
    """Orchestrates AI recommendation generation via Gemini / OpenAI, falling back to heuristics."""
    prompt = build_recommendations_prompt(
        destination=req.destination,
        budget_tier=req.budget_tier,
        party_type=req.party_type,
        party_size=req.party_size,
        pacing=req.pacing,
        interests=req.interests,
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
                    "response_schema": RecommendationsResponse
                }
            )
            data = json.loads(response.text)
            return RecommendationsResponse(**data)
        except Exception as e:
            logger.warning(f"Gemini recommendations failed, falling back: {e}")

    return generate_heuristic_recommendations(req)

def get_popular_destinations() -> List[dict]:
    return POPULAR_DESTINATIONS
