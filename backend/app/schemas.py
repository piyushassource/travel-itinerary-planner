from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class ActivityItem(BaseModel):
    id: str = Field(description="Unique activity ID e.g. act_day1_1")
    time_slot: str = Field(description="Time window e.g. 09:30 AM - 11:30 AM")
    title: str = Field(description="Name of attraction, venue, or dining spot")
    category: Literal["attraction", "dining", "transport", "leisure", "accommodation"] = "attraction"
    description: str = Field(description="Engaging description with actionable local travel tip")
    neighborhood: str = Field(description="Area/district to ensure spatial clustering")
    estimated_cost_usd: float = Field(default=0.0, description="Estimated cost per person in USD")
    booking_required: bool = Field(default=False, description="Whether advance reservation is needed")
    pacing_tag: Literal["quick_stop", "standard", "immersive", "relaxed"] = "standard"
    dietary_tags: List[str] = Field(default_factory=list, description="Dietary badges e.g. Vegetarian, Halal, Gluten-Free")
    accessibility_note: Optional[str] = Field(default=None, description="Accessibility details e.g. Step-free access, elevator available")

class DayPlan(BaseModel):
    day_number: int = Field(ge=1)
    date: Optional[str] = None
    theme: str = Field(description="Day theme or focus, e.g. 'Old Town Charm & Night Bazaar'")
    area_focus: str = Field(description="Geographic neighborhood anchor for the day")
    activities: List[ActivityItem] = Field(default_factory=list)
    day_estimated_cost_usd: float = 0.0

class ItineraryResponse(BaseModel):
    trip_id: str
    trip_title: str
    destination: str
    total_days: int
    party_type: Literal["solo", "couple", "group", "family"]
    party_size: int = 1
    budget_tier: Literal["budget", "moderate", "luxury"]
    pacing: Literal["relaxed", "moderate", "fast_paced"]
    travel_dates: Optional[str] = None
    dietary_restrictions: List[str] = Field(default_factory=list)
    mobility_level: Literal["standard", "low_walking", "wheelchair_step_free"] = "standard"
    summary: str
    itinerary: List[DayPlan]
    estimated_total_cost_usd: float
    cost_per_person_usd: float
    packing_and_logistics_tips: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TripGenerationRequest(BaseModel):
    destination: str = Field(min_length=2, example="Kyoto, Japan")
    days: int = Field(ge=1, le=14, default=3)
    party_type: Literal["solo", "couple", "group", "family"] = "solo"
    party_size: int = Field(ge=1, default=1)
    budget_tier: Literal["budget", "moderate", "luxury"] = "moderate"
    pacing: Literal["relaxed", "moderate", "fast_paced"] = "moderate"
    travel_dates: Optional[str] = Field(default=None, example="Weekend Getaway / Spring")
    dietary_restrictions: List[str] = Field(default_factory=list, example=["Vegetarian", "Halal"])
    mobility_level: Literal["standard", "low_walking", "wheelchair_step_free"] = "standard"
    interests: List[str] = Field(default_factory=lambda: ["sightseeing", "food"])
    accommodation_area: Optional[str] = None
    custom_notes: Optional[str] = None

class DayRegenerateRequest(BaseModel):
    trip_id: str
    destination: str
    day_number: int
    current_theme: str
    new_preference_or_vibe: str
    budget_tier: Literal["budget", "moderate", "luxury"] = "moderate"
    party_type: Literal["solo", "couple", "group", "family"] = "couple"
    dietary_restrictions: List[str] = Field(default_factory=list)
    mobility_level: Literal["standard", "low_walking", "wheelchair_step_free"] = "standard"
    interests: List[str] = Field(default_factory=list)

class ActivitySwapRequest(BaseModel):
    trip_id: str
    destination: str
    day_number: int
    activity_id: str
    activity_category: str
    neighborhood: str
    reason: Optional[str] = "Prefer alternative venue"
    budget_tier: str = "moderate"
    dietary_restrictions: List[str] = Field(default_factory=list)
    mobility_level: Literal["standard", "low_walking", "wheelchair_step_free"] = "standard"

class TripUpdateRequest(BaseModel):
    trip_title: Optional[str] = None
    summary: Optional[str] = None
    destination: Optional[str] = None
    budget_tier: Optional[Literal["budget", "moderate", "luxury"]] = None
    pacing: Optional[Literal["relaxed", "moderate", "fast_paced"]] = None
    travel_dates: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    mobility_level: Optional[Literal["standard", "low_walking", "wheelchair_step_free"]] = None
    itinerary: Optional[List[DayPlan]] = None
    estimated_total_cost_usd: Optional[float] = None
    cost_per_person_usd: Optional[float] = None
    custom_notes: Optional[str] = None

class TripSummaryItem(BaseModel):
    trip_id: str
    trip_title: str
    destination: str
    total_days: int
    party_type: str
    party_size: int
    budget_tier: str
    pacing: str
    travel_dates: Optional[str] = None
    dietary_restrictions: List[str] = Field(default_factory=list)
    mobility_level: str = "standard"
    estimated_total_cost_usd: float
    cost_per_person_usd: float
    created_at: Optional[str] = None
    summary: Optional[str] = None

class TripListResponse(BaseModel):
    trips: List[TripSummaryItem]
    total_count: int

# =======================================================
# INTELLIGENT RECOMMENDATIONS SCHEMAS
# =======================================================

class RecommendationItem(BaseModel):
    id: str
    title: str
    category: Literal["attraction", "dining", "hidden_gem", "accommodation", "leisure"]
    neighborhood: str
    description: str
    estimated_cost_usd: float = 0.0
    dietary_tags: List[str] = Field(default_factory=list)
    accessibility_note: Optional[str] = None
    match_reason: str = Field(description="Explanation of why this matches the traveler profile")
    rating: float = 4.8

class RecommendationsRequest(BaseModel):
    destination: str
    budget_tier: Literal["budget", "moderate", "luxury"] = "moderate"
    party_type: Literal["solo", "couple", "group", "family"] = "solo"
    party_size: int = 1
    pacing: Literal["relaxed", "moderate", "fast_paced"] = "moderate"
    interests: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    mobility_level: Literal["standard", "low_walking", "wheelchair_step_free"] = "standard"

class RecommendationsResponse(BaseModel):
    destination: str
    summary: str
    attractions: List[RecommendationItem]
    dining: List[RecommendationItem]
    hidden_gems: List[RecommendationItem]
    neighborhood_stays: List[RecommendationItem]
