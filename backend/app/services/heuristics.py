import uuid
from typing import List, Optional
from app.schemas import (
    TripGenerationRequest,
    ItineraryResponse,
    DayPlan,
    ActivityItem,
    DayRegenerateRequest,
    ActivitySwapRequest
)

DESTINATION_KNOWLEDGE = {
    "tokyo": {
        "neighborhoods": [
            ("Shinjuku & Shibuya", "Modern Vibe & Neon Skylines"),
            ("Asakusa & Ueno", "Old Town Temples & Traditional Markets"),
            ("Ginza & Tsukiji", "Culinary Delights & World-Class Shopping"),
            ("Roppongi & Tokyo Tower", "Panoramic Views & Contemporary Art")
        ],
        "activities": {
            "attraction": [
                ("Senso-ji Temple & Nakamise-dori", "Historic Buddhist temple with sacred incense hall and artisan stalls", "Asakusa & Ueno", 0.0, False, "Step-free ramp at main hall"),
                ("Shibuya Sky Observatory", "Breathtaking 360-degree open-air rooftop view over the famous crossing", "Shinjuku & Shibuya", 18.0, True, "Full elevator accessibility to roof deck"),
                ("Meiji Jingu Shrine & Yoyogi Forest", "Serene evergreen forest and grand Shinto shrine in central Tokyo", "Shinjuku & Shibuya", 0.0, False, "Wide gravel paths, accessible restrooms"),
                ("Mori Art Museum & Roppongi Hills", "Cutting-edge contemporary art space featuring panoramic city views", "Roppongi & Tokyo Tower", 14.0, True, "Elevator and wheelchair loans on site")
            ],
            "dining": [
                ("Tsukiji Outer Market Tasting Crawl", "Sample fresh tamagoyaki, sashimi bowls, and wagyu skewers", "Ginza & Tsukiji", 25.0, False),
                ("Omoide Yokocho Yakitori Alleys", "Atmospheric retro alleys serving sizzling charcoal-grilled yakitori", "Shinjuku & Shibuya", 20.0, False),
                ("Kappo Ryokan Kaiseki Experience", "Multi-course seasonal Japanese dining showcasing artisan techniques", "Ginza & Tsukiji", 95.0, True)
            ],
            "leisure": [
                ("Shinjuku Gyoen National Garden", "Sprawling traditional Japanese landscape gardens with teahouses", "Shinjuku & Shibuya", 4.0, False, "Paved circuits and barrier-free routes"),
                ("Meguro Riverwalk Evening Stroll", "Picturesque tree-lined canal adorned with evening lanterns", "Shinjuku & Shibuya", 0.0, False, "Flat paved river promenade")
            ]
        },
        "tips": [
            "Purchase a digital Suica or Pasmo IC card on your smartphone for seamless metro tap-and-go.",
            "Wear comfortable slip-on walking shoes as many traditional venues and temples require shoe removal.",
            "Carry a small amount of cash (1,000-5,000 JPY notes) for traditional street food and temple charms."
        ]
    },
    "paris": {
        "neighborhoods": [
            ("Le Marais & Île de la Cité", "Gothic Grandeur & Historic Boutiques"),
            ("Montmartre & Pigalle", "Bohemian Art & Sacré-Cœur Panoramas"),
            ("Saint-Germain-des-Prés & Latin Quarter", "Literary Cafes & Classical Gardens"),
            ("Eiffel & Trocadéro", "Iconic Monuments & Seine Riverfront")
        ],
        "activities": {
            "attraction": [
                ("Louvre Museum Curated Wing", "Masterpieces of antiquity and Renaissance art in the former royal palace", "Le Marais & Île de la Cité", 22.0, True, "Elevator access via Pyramid entrance"),
                ("Sacré-Cœur Basilica & Place du Tertre", "Iconic domed basilica and charming open-air painters' square", "Montmartre & Pigalle", 0.0, False, "Funicular railway bypasses hillside steps"),
                ("Musée d'Orsay Impressionist Gallery", "Stunning Beaux-Arts railway station home to Monet, Van Gogh, and Degas", "Saint-Germain-des-Prés", 18.0, True, "Full barrier-free access with ramps and elevators"),
                ("Sainte-Chapelle Stained Glass Marvel", "Spectacular 13th-century Gothic royal chapel with towering stained glass", "Le Marais & Île de la Cité", 14.0, True, "Elevator available for upper chapel")
            ],
            "dining": [
                ("Café de Flore / Les Deux Magots", "Iconic sidewalk terrace for morning espresso and fresh butter croissants", "Saint-Germain-des-Prés", 15.0, False),
                ("Traditional Bistro Chez Janou", "Provençal flavors, slow-cooked duck confit, and endless chocolate mousse bowl", "Le Marais & Île de la Cité", 38.0, True),
                ("Seine Riverfront Sunset Wine & Fromage", "Casual picnic by Pont des Arts with fresh baguette and Comté cheese", "Le Marais & Île de la Cité", 15.0, False)
            ],
            "leisure": [
                ("Jardin du Luxembourg Stroll", "Classical Medici fountain, chestnut trees, and antique sailboat pond", "Saint-Germain-des-Prés", 0.0, False, "Flat shaded gravel promenades"),
                ("Seine Evening Sightseeing Cruise", "Illuminated view of bridges and historic monuments from the water", "Eiffel & Trocadéro", 19.0, True, "Boarding ramps with assisted wheelchair access")
            ]
        },
        "tips": [
            "Book Louvre and Eiffel Tower time slots at least 2 weeks in advance to avoid 2-hour queue lines.",
            "Validate Metro tickets or load the Navigo Easy pass on your phone for unlimited zone 1-2 travel.",
            "Always greet shopkeepers and waitstaff with a polite 'Bonjour' before asking questions."
        ]
    },
    "new york": {
        "neighborhoods": [
            ("Lower Manhattan & Brooklyn Bridge", "Historic Seaport & Architectural Marvels"),
            ("Midtown & Broadway", "Skyscrapers, Theaters & Iconic Landmarks"),
            ("Greenwich Village & SoHo", "Cobblestone Streets & Trendsetting Eateries"),
            ("Central Park & Museum Mile", "Grand Park Vistas & World-Class Culture")
        ],
        "activities": {
            "attraction": [
                ("The High Line & Little Island", "Elevated park built on historic freight rail with Hudson River views", "Greenwich Village & SoHo", 0.0, False, "Elevator access at 14th, 23rd, and 30th streets"),
                ("Metropolitan Museum of Art (The Met)", "5,000 years of global art and breathtaking rooftop sculpture garden", "Central Park & Museum Mile", 30.0, True, "Full ADA compliant street-level entrance & elevators"),
                ("Brooklyn Bridge Walk & DUMBO", "Iconic suspension bridge promenade with skyline photo spots", "Lower Manhattan", 0.0, False, "Paved walkway with gentle incline"),
                ("Summit One Vanderbilt", "Immersive multisensory glass observatory above Grand Central", "Midtown & Broadway", 42.0, True, "Full ADA elevator access throughout")
            ],
            "dining": [
                ("Chelsea Market Culinary Hall", "Artisanal lobster rolls, fresh tacos, and gourmet pastries", "Greenwich Village & SoHo", 25.0, False),
                ("Classic Greenwich Village Trattoria", "Handmade pasta and candlelit ambiance in an intimate townhouse setting", "Greenwich Village & SoHo", 45.0, True),
                ("Chinatown Dim Sum Gathering", "Steaming dumplings, char siu pork buns, and jasmine tea at Nom Wah", "Lower Manhattan", 20.0, False)
            ],
            "leisure": [
                ("Central Park Bow Bridge & Ramble", "Picturesque stroll across Victorian bridges and shaded woodlands", "Central Park & Museum Mile", 0.0, False, "Paved paths around lake"),
                ("West Village Jazz Cellar", "Intimate live jazz performance at Village Vanguard or Smalls", "Greenwich Village & SoHo", 35.0, True, "Stairs to cellar; alternative ground-floor seating available upon request")
            ]
        },
        "tips": [
            "Use OMNY contactless tap (Apple Pay/Google Pay/credit card) at all subway turnstiles.",
            "Wear sturdy footwear: you will comfortably log 15,000 to 20,000 steps per day in Manhattan.",
            "Standard dining tip in NYC is 18% to 22% of the pre-tax bill."
        ]
    }
}

def generate_heuristic_itinerary(req: TripGenerationRequest) -> ItineraryResponse:
    dest_key = req.destination.lower()
    matched_key = None
    for k in DESTINATION_KNOWLEDGE:
        if k in dest_key:
            matched_key = k
            break
            
    city_data = DESTINATION_KNOWLEDGE.get(matched_key)
    cost_mult = {"budget": 0.6, "moderate": 1.0, "luxury": 2.2}.get(req.budget_tier, 1.0)
    stops_count = {"relaxed": 3, "moderate": 4, "fast_paced": 5}.get(req.pacing, 4)

    # Determine dietary tags to inject
    active_dietary = req.dietary_restrictions if req.dietary_restrictions and "None" not in req.dietary_restrictions else []
    
    # Accessibility note helper
    def get_access_note(default_note: Optional[str] = None) -> Optional[str]:
        if req.mobility_level == "wheelchair_step_free":
            return default_note or "Step-free ramp/elevator access available"
        elif req.mobility_level == "low_walking":
            return "Minimal walking; bench seating and transit hub nearby"
        return default_note

    days_list: List[DayPlan] = []
    total_cost_usd = 0.0

    for day_idx in range(1, req.days + 1):
        if city_data:
            nb_info = city_data["neighborhoods"][(day_idx - 1) % len(city_data["neighborhoods"])]
            area_name, theme_name = nb_info
            
            attractions = city_data["activities"]["attraction"]
            dining = city_data["activities"]["dining"]
            leisure = city_data["activities"]["leisure"]
            
            day_acts: List[ActivityItem] = []
            
            # Morning activity
            att_choice = attractions[(day_idx - 1) % len(attractions)]
            cost1 = round(att_choice[3] * cost_mult, 1)
            day_acts.append(ActivityItem(
                id=f"act_d{day_idx}_1",
                time_slot="09:30 AM - 12:00 PM",
                title=att_choice[0],
                category="attraction",
                description=att_choice[1],
                neighborhood=att_choice[2],
                estimated_cost_usd=cost1,
                booking_required=att_choice[4],
                pacing_tag="immersive" if req.pacing == "relaxed" else "standard",
                dietary_tags=[],
                accessibility_note=get_access_note(att_choice[5] if len(att_choice) > 5 else None)
            ))
            
            # Lunch dining
            dine_choice = dining[(day_idx - 1) % len(dining)]
            cost2 = round(dine_choice[3] * cost_mult, 1)
            day_acts.append(ActivityItem(
                id=f"act_d{day_idx}_2",
                time_slot="12:30 PM - 02:00 PM",
                title=dine_choice[0],
                category="dining",
                description=f"{dine_choice[1]} (Offers verified {', '.join(active_dietary) if active_dietary else 'local specialty'} options)",
                neighborhood=area_name,
                estimated_cost_usd=cost2,
                booking_required=dine_choice[4],
                pacing_tag="relaxed",
                dietary_tags=active_dietary,
                accessibility_note=get_access_note("Ground floor seating accessible")
            ))
            
            # Afternoon leisure
            lei_choice = leisure[(day_idx - 1) % len(leisure)]
            cost3 = round(lei_choice[3] * cost_mult, 1)
            day_acts.append(ActivityItem(
                id=f"act_d{day_idx}_3",
                time_slot="02:30 PM - 05:00 PM",
                title=lei_choice[0],
                category="leisure",
                description=lei_choice[1],
                neighborhood=area_name,
                estimated_cost_usd=cost3,
                booking_required=lei_choice[4],
                pacing_tag="relaxed",
                dietary_tags=[],
                accessibility_note=get_access_note(lei_choice[5] if len(lei_choice) > 5 else None)
            ))
            
            if stops_count >= 4:
                dine_eve = dining[(day_idx) % len(dining)]
                cost4 = round((dine_eve[3] + 15) * cost_mult, 1)
                day_acts.append(ActivityItem(
                    id=f"act_d{day_idx}_4",
                    time_slot="06:30 PM - 09:00 PM",
                    title=f"Evening Dining & Sunset at {area_name}",
                    category="dining",
                    description=f"Savor culinary specialties in {area_name} followed by an atmospheric evening walk. Accommodates {', '.join(active_dietary) if active_dietary else 'standard cuisine'}.",
                    neighborhood=area_name,
                    estimated_cost_usd=cost4,
                    booking_required=True if req.party_type in ["couple", "group"] else False,
                    pacing_tag="relaxed",
                    dietary_tags=active_dietary,
                    accessibility_note=get_access_note("Step-free dining room")
                ))
                
            day_cost = sum(a.estimated_cost_usd for a in day_acts)
            total_cost_usd += day_cost
            
            days_list.append(DayPlan(
                day_number=day_idx,
                theme=theme_name,
                area_focus=area_name,
                activities=day_acts,
                day_estimated_cost_usd=round(day_cost, 2)
            ))
        else:
            # Generic fallback
            area_name = f"Central {req.destination} District"
            day_acts = [
                ActivityItem(
                    id=f"act_d{day_idx}_1",
                    time_slot="09:00 AM - 11:30 AM",
                    title=f"Iconic Landmarks & Heritage of {req.destination}",
                    category="attraction",
                    description=f"Explore the celebrated cultural monuments and historic architecture in {req.destination}.",
                    neighborhood=area_name,
                    estimated_cost_usd=round(20.0 * cost_mult, 1),
                    booking_required=True,
                    pacing_tag="immersive",
                    dietary_tags=[],
                    accessibility_note=get_access_note("Wheelchair ramps and elevators available")
                ),
                ActivityItem(
                    id=f"act_d{day_idx}_2",
                    time_slot="12:00 PM - 01:30 PM",
                    title=f"Artisanal Lunch Tasting in {area_name}",
                    category="dining",
                    description=f"Sample quintessential regional dishes in a top-rated eatery. Accommodating {', '.join(active_dietary) if active_dietary else 'local menu'}.",
                    neighborhood=area_name,
                    estimated_cost_usd=round(22.0 * cost_mult, 1),
                    booking_required=False,
                    pacing_tag="relaxed",
                    dietary_tags=active_dietary,
                    accessibility_note=get_access_note("Ground-level access")
                ),
                ActivityItem(
                    id=f"act_d{day_idx}_3",
                    time_slot="02:30 PM - 05:00 PM",
                    title=f"{req.destination} Scenic Promenade & Cultural Walk",
                    category="leisure",
                    description="Stroll through vibrant pedestrian districts, artisan shops, and scenic viewpoints.",
                    neighborhood=area_name,
                    estimated_cost_usd=0.0,
                    booking_required=False,
                    pacing_tag="relaxed",
                    dietary_tags=[],
                    accessibility_note=get_access_note("Flat promenade")
                ),
                ActivityItem(
                    id=f"act_d{day_idx}_4",
                    time_slot="06:30 PM - 08:30 PM",
                    title=f"Curated Evening Dinner & Twilight Atmosphere",
                    category="dining",
                    description="Relaxed dinner highlighting seasonal ingredients with great evening ambiance.",
                    neighborhood=area_name,
                    estimated_cost_usd=round(35.0 * cost_mult, 1),
                    booking_required=True,
                    pacing_tag="relaxed",
                    dietary_tags=active_dietary,
                    accessibility_note=get_access_note("Step-free dining room")
                )
            ]
            day_cost = sum(a.estimated_cost_usd for a in day_acts)
            total_cost_usd += day_cost
            days_list.append(DayPlan(
                day_number=day_idx,
                theme=f"Discovering {req.destination} - Part {day_idx}",
                area_focus=area_name,
                activities=day_acts,
                day_estimated_cost_usd=round(day_cost, 2)
            ))

    grand_total = round(total_cost_usd * req.party_size, 2)
    per_person = round(total_cost_usd, 2)
    
    tips = city_data["tips"] if city_data else [
        f"Download offline maps of {req.destination} on your phone for easy navigation.",
        "Check attraction reservation requirements 1-2 weeks prior to departure.",
        "Keep local transit passes handy for seamless inner-city travel."
    ]

    return ItineraryResponse(
        trip_id=str(uuid.uuid4()),
        trip_title=f"{req.days}-Day {req.party_type.capitalize()} Journey in {req.destination}",
        destination=req.destination,
        total_days=req.days,
        party_type=req.party_type,
        party_size=req.party_size,
        budget_tier=req.budget_tier,
        pacing=req.pacing,
        travel_dates=req.travel_dates,
        dietary_restrictions=req.dietary_restrictions,
        mobility_level=req.mobility_level,
        summary=f"A personalized {req.days}-day {req.pacing} {req.party_type} itinerary exploring {req.destination}, balancing top sights, spatial proximity, and dietary/accessibility preferences.",
        itinerary=days_list,
        estimated_total_cost_usd=grand_total,
        cost_per_person_usd=per_person,
        packing_and_logistics_tips=tips
    )

def regenerate_heuristic_day(req: DayRegenerateRequest) -> DayPlan:
    cost_mult = {"budget": 0.6, "moderate": 1.0, "luxury": 2.2}.get(req.budget_tier, 1.0)
    area_name = f"Custom District of {req.destination}"
    vibe = req.new_preference_or_vibe or "Bespoke Experiential Day"
    active_dietary = req.dietary_restrictions if req.dietary_restrictions else []
    
    access_note = "Step-free ramp/elevator access" if req.mobility_level == "wheelchair_step_free" else None

    acts = [
        ActivityItem(
            id=f"act_d{req.day_number}_1_regen",
            time_slot="10:00 AM - 12:30 PM",
            title=f"Curated {vibe.title()} Experience",
            category="attraction",
            description=f"Tailored morning session focusing on {vibe} with insider access.",
            neighborhood=area_name,
            estimated_cost_usd=round(28.0 * cost_mult, 1),
            booking_required=True,
            pacing_tag="immersive",
            dietary_tags=[],
            accessibility_note=access_note
        ),
        ActivityItem(
            id=f"act_d{req.day_number}_2_regen",
            time_slot="01:00 PM - 02:30 PM",
            title=f"Artisanal Lunch matching {vibe.title()}",
            category="dining",
            description=f"Handpicked dining venue complementing your new {vibe} preference. Verified for {', '.join(active_dietary) if active_dietary else 'standard diet'}.",
            neighborhood=area_name,
            estimated_cost_usd=round(24.0 * cost_mult, 1),
            booking_required=False,
            pacing_tag="relaxed",
            dietary_tags=active_dietary,
            accessibility_note="Ground-level entry"
        ),
        ActivityItem(
            id=f"act_d{req.day_number}_3_regen",
            time_slot="03:00 PM - 05:30 PM",
            title=f"Leisure Stroll & Scenic Discovery",
            category="leisure",
            description=f"Scenic open exploration and relaxed afternoon vibe in {area_name}.",
            neighborhood=area_name,
            estimated_cost_usd=0.0,
            booking_required=False,
            pacing_tag="relaxed",
            dietary_tags=[],
            accessibility_note=access_note
        ),
        ActivityItem(
            id=f"act_d{req.day_number}_4_regen",
            time_slot="07:00 PM - 09:30 PM",
            title=f"Intimate Evening & Atmosphere",
            category="dining",
            description=f"Signature dinner experience perfectly attuned to {vibe}.",
            neighborhood=area_name,
            estimated_cost_usd=round(42.0 * cost_mult, 1),
            booking_required=True,
            pacing_tag="relaxed",
            dietary_tags=active_dietary,
            accessibility_note="Step-free accessible dining room"
        )
    ]
    day_cost = sum(a.estimated_cost_usd for a in acts)
    return DayPlan(
        day_number=req.day_number,
        theme=f"Refined {vibe.title()} Exploration",
        area_focus=area_name,
        activities=acts,
        day_estimated_cost_usd=round(day_cost, 2)
    )

def swap_heuristic_activity(req: ActivitySwapRequest) -> ActivityItem:
    cost_mult = {"budget": 0.6, "moderate": 1.0, "luxury": 2.2}.get(req.budget_tier, 1.0)
    category = req.activity_category or "attraction"
    active_dietary = req.dietary_restrictions if req.dietary_restrictions else []
    access_note = "Step-free ramp/elevator access" if req.mobility_level == "wheelchair_step_free" else None

    return ActivityItem(
        id=f"swap_{req.activity_id}_{uuid.uuid4().hex[:4]}",
        time_slot="Flexible 2-Hour Window",
        title=f"Alternative {category.capitalize()} in {req.neighborhood or req.destination}",
        category=category if category in ["attraction", "dining", "transport", "leisure"] else "attraction",
        description=f"Curated replacement venue selected for: {req.reason}. Perfectly situated to preserve route efficiency.",
        neighborhood=req.neighborhood or f"Central {req.destination}",
        estimated_cost_usd=round(25.0 * cost_mult, 1),
        booking_required=True if category == "dining" else False,
        pacing_tag="standard",
        dietary_tags=active_dietary if category == "dining" else [],
        accessibility_note=access_note
    )
