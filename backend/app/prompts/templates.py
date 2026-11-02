"""
Prompt Engineering & Personalization Layer for Generative AI Travel Planning.

This module acts as the core bridge between raw application inputs and GenAI models.
It dynamically structures persona roles, instructions, spatial/temporal constraints,
dietary requirements, mobility accessibility, and pacing rules into highly optimized,
repeatable prompt patterns.
"""

from typing import List, Optional

SYSTEM_ITINERARY_PROMPT = """You are an elite, Michelin-aware GenAI Travel Concierge, Master Urban Geographer, and Logistics Specialist.
Your mission is to construct hyper-personalized, geographically clustered, and temporally realistic day-by-day itineraries.

CORE OPERATIONAL PRINCIPLES:
1. SPATIAL PROXIMITY & CLUSTERING:
   - Group morning, afternoon, and evening activities within a single neighborhood or direct subway transit corridor.
   - Absolutely NEVER require travelers to crisscross or zigzag across a metropolitan area within the same day.
2. PERSONALIZED PACING CALIBRATION:
   - "relaxed": 2-3 stops/day. Ample open buffer time, unhurried 1.5-2 hour meals, scenic downtime.
   - "moderate": 3-4 stops/day. Balanced sightseeing, 45-minute transit buffers, well-timed rest stops.
   - "fast_paced": 5-6 stops/day. High mobility, early starts, rapid transit links, nightlife/evening stops.
3. DIETARY RESTRICTION ENFORCEMENT:
   - Strictly honor dietary restrictions (e.g. Vegetarian, Vegan, Halal, Kosher, Gluten-Free, Allergies).
   - Every dining recommendation MUST be explicitly verified for accommodating the requested diet.
   - Include specific dish recommendations compatible with the diet.
4. MOBILITY & ACCESSIBILITY GUARANTEES:
   - "wheelchair_step_free": Prioritize elevators, flat promenades, ramp access, avoid cobblestones or steep inclines.
   - "low_walking": Limit continuous walking to <15 minutes; suggest direct taxis/metro with minimal transfers.
   - "standard": Normal pedestrian navigation and public transit walking.
5. BUDGET TIER COMPLIANCE:
   - "budget": Street food stalls, food halls, free public parks, walking tours, metro passes.
   - "moderate": Quality local bistros, ticketed museums, occasional taxi.
   - "luxury": Fine dining, private reservations, VIP skip-the-line access, premium comfort.
6. STRICT JSON CONFORMANCE:
   - Output ONLY a valid JSON object matching the provided Pydantic schema without preamble or conversational filler.
"""

def build_dietary_instructions(dietary_restrictions: List[str]) -> str:
    """Formats dietary restrictions into explicit, actionable prompt directives."""
    if not dietary_restrictions or "None" in dietary_restrictions:
        return "Standard diverse local culinary recommendations."
    
    diet_str = ", ".join(dietary_restrictions)
    return (
        f"CRITICAL DIETARY DIRECTIVE: Travelers require strict adherence to: [{diet_str}].\n"
        f"- Ensure every lunch, dinner, and snack spot caters to [{diet_str}].\n"
        f"- Highlight signature dishes matching [{diet_str}] in the activity descriptions.\n"
        f"- Tag each dining activity in 'dietary_tags' with relevant labels."
    )

def build_mobility_instructions(mobility_level: str) -> str:
    """Formats physical accessibility constraints into transit and routing instructions."""
    mobility_directives = {
        "wheelchair_step_free": (
            "ACCESSIBILITY REQUIREMENT (Step-Free / Wheelchair Accessible):\n"
            "- All suggested attractions must feature elevator or ramp access.\n"
            "- Avoid steep hills, multi-flight staircases, and rough cobblestones.\n"
            "- Transit routes must use accessible stations with working elevator facilities.\n"
            "- Explicitly populate 'accessibility_note' with accessibility details."
        ),
        "low_walking": (
            "MOBILITY REQUIREMENT (Low Walking / Gentle Pacing):\n"
            "- Minimize pedestrian fatigue: keep total walking between venues under 10-15 minutes.\n"
            "- Prioritize direct transit corridors, hop-on boat tours, and central seating stops.\n"
            "- Ensure frequent rest opportunities and shaded cafes."
        ),
        "standard": (
            "MOBILITY: Standard pedestrian stamina. Comfortable with public transit walks and typical sightseeing steps."
        )
    }
    return mobility_directives.get(mobility_level, mobility_directives["standard"])

def build_party_persona_directive(party_type: str, party_size: int) -> str:
    """Injects specialized dynamics based on party configuration."""
    personas = {
        "solo": (
            f"Solo Traveler Persona ({party_size} person):\n"
            "- Prioritize solo-friendly dining (counter seating, food halls, lively cafes).\n"
            "- Emphasize safe, well-lit districts and highly efficient public transit.\n"
            "- Recommend engaging cultural workshops and scenic photo vantage points."
        ),
        "couple": (
            f"Couple Persona ({party_size} travelers):\n"
            "- Emphasize romantic ambiance, scenic golden-hour viewpoints, and charming bistros.\n"
            "- Allow leisurely morning starts and intimate evening wine/cocktail spots.\n"
            "- Balance memorable cultural landmarks with relaxed private downtime."
        ),
        "group": (
            f"Small Group Persona ({party_size} travelers):\n"
            "- Structure activities with spacious, group-friendly table seating and shared dining.\n"
            "- Add an extra 20-30 minute buffer for group coordination and transit assembly.\n"
            "- Highlight activities that can be reserved for groups with clear meeting spots."
        ),
        "family": (
            f"Family Persona ({party_size} travelers):\n"
            "- Focus on multi-generational appeal, kid-accessible interactive exhibits, and parks.\n"
            "- Include scheduled rest breaks, easy restroom access, and family-friendly dining."
        )
    }
    return personas.get(party_type, f"Travel Party ({party_size} travelers): Standard travel optimization.")

def build_generate_prompt(
    destination: str,
    days: int,
    party_type: str,
    party_size: int,
    budget_tier: str,
    pacing: str,
    interests: List[str],
    travel_dates: Optional[str] = None,
    dietary_restrictions: Optional[List[str]] = None,
    mobility_level: str = "standard",
    accommodation_area: Optional[str] = None,
    custom_notes: Optional[str] = None
) -> str:
    """
    Constructs a comprehensive, personalized natural-language prompt
    injecting all user variables into a structured itinerary request.
    """
    interests_str = ", ".join(interests) if interests else "Sightseeing, Local Culture, Gastronomy"
    dates_str = f"Travel Window / Dates: {travel_dates}" if travel_dates else "Travel Window: Upcoming trip"
    hub_str = f"Base Hotel / Neighborhood Hub: {accommodation_area}" if accommodation_area else "Base: Central, well-connected neighborhood"
    notes_str = f"Custom Traveler Notes: {custom_notes}" if custom_notes else "None specified"
    
    dietary_block = build_dietary_instructions(dietary_restrictions or [])
    mobility_block = build_mobility_instructions(mobility_level)
    party_block = build_party_persona_directive(party_type, party_size)

    return f"""### AI TRAVEL ARCHITECT GENERATION BRIEF: {days}-Day Itinerary for {destination}

TRAVEL PROFILE & CONSTRAINTS:
- Destination: {destination}
- Duration: {days} Days
- {dates_str}
- Budget Tier: {budget_tier.upper()}
- Pacing Preference: {pacing.upper()}
- Primary Interests: {interests_str}
- {hub_str}
- {notes_str}

PERSONALIZATION & INCLUSIVITY LOGIC:
{party_block}

{dietary_block}

{mobility_block}

DELIVERABLE SPECIFICATIONS:
1. Generate exactly {days} day plan(s). Each day must have a distinct 'theme' and a single 'area_focus' (district).
2. For each day, sequence activities chronologically with clear time slots (e.g. '09:30 AM - 11:30 AM').
3. Include categories: 'attraction', 'dining', 'leisure', 'transport'.
4. Ensure estimated USD costs per person reflect the {budget_tier} tier.
5. Provide 3-4 destination-specific packing and transit logistics tips.
6. Populate 'dietary_tags' for dining venues and 'accessibility_note' for mobility guidance.
"""

def build_regenerate_day_prompt(
    destination: str,
    day_number: int,
    current_theme: str,
    new_preference_or_vibe: str,
    budget_tier: str,
    party_type: str,
    dietary_restrictions: Optional[List[str]] = None,
    mobility_level: str = "standard"
) -> str:
    """Constructs a targeted prompt for regenerating a single day with refined personal preferences."""
    dietary_block = build_dietary_instructions(dietary_restrictions or [])
    mobility_block = build_mobility_instructions(mobility_level)

    return f"""### REGENERATE SINGLE DAY BRIEF: Day {day_number} in {destination}
Previous Day Theme: "{current_theme}"
New Desired Vibe / Shift: "{new_preference_or_vibe}"

TRAVEL PROFILE:
- Destination: {destination}
- Party Type: {party_type}
- Budget Tier: {budget_tier}

PERSONALIZATION LOGIC:
{dietary_block}
{mobility_block}

REQUIREMENTS:
- Design 3-5 newly sequenced activities specifically matching: "{new_preference_or_vibe}".
- Maintain spatial clustering in an appropriate neighborhood.
- Return a single DayPlan JSON object.
"""

def build_swap_activity_prompt(
    destination: str,
    neighborhood: str,
    category: str,
    reason: str,
    budget_tier: str,
    dietary_restrictions: Optional[List[str]] = None,
    mobility_level: str = "standard"
) -> str:
    """Constructs a prompt to replace an individual activity while maintaining spatial and dietary fidelity."""
    dietary_note = f"Must comply with dietary requirements: {', '.join(dietary_restrictions)}." if dietary_restrictions else ""
    mobility_note = f"Must meet mobility requirements: {mobility_level}." if mobility_level != "standard" else ""

    return f"""### SWAP INDIVIDUAL ACTIVITY BRIEF: {category.upper()} in {destination}
Neighborhood Cluster: {neighborhood}
Reason for Swap: "{reason}"
Budget Tier: {budget_tier}
{dietary_note}
{mobility_note}

Provide 1 alternative {category} venue in or adjacent to {neighborhood}. Return a single ActivityItem JSON object.
"""

def build_recommendations_prompt(
    destination: str,
    budget_tier: str,
    party_type: str,
    party_size: int,
    pacing: str,
    interests: List[str],
    dietary_restrictions: Optional[List[str]] = None,
    mobility_level: str = "standard"
) -> str:
    """
    Constructs an intelligent recommendations prompt to curate top attractions, dining,
    hidden gems, and neighborhood hubs tailored specifically to the user profile.
    """
    interests_str = ", ".join(interests) if interests else "Sightseeing, Local Culture, Gastronomy"
    dietary_block = build_dietary_instructions(dietary_restrictions or [])
    mobility_block = build_mobility_instructions(mobility_level)
    party_block = build_party_persona_directive(party_type, party_size)

    return f"""### CURATED RECOMMENDATIONS BRIEF: {destination}

TRAVELER PROFILE:
- Destination: {destination}
- Budget Tier: {budget_tier.upper()}
- Pacing Preference: {pacing.upper()}
- Interests: {interests_str}
{party_block}

CONSTRAINTS & INCLUSIVITY:
{dietary_block}
{mobility_block}

DELIVERABLE SPECIFICATIONS:
Curate meaningful, categorized recommendations:
1. 'attractions': 3-4 top sights that directly match the traveler's interests and pacing.
2. 'dining': 3-4 restaurants or food markets strictly respecting the dietary constraints and budget tier.
3. 'hidden_gems': 2-3 lesser-known, authentic, or experiential spots avoiding generic tourist traps.
4. 'neighborhood_stays': 2 ideal neighborhood districts to stay in with rationale.
5. For EVERY item, provide:
   - 'match_reason': 1 concise sentence explaining WHY this venue matches this traveler's specific profile.
   - 'rating': estimated traveler satisfaction rating (e.g. 4.7 - 4.9).
   - 'dietary_tags' and 'accessibility_note' where applicable.
"""
