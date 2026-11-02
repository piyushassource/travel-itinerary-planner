-- ==============================================================================
-- PERSONALIZED TRAVEL ITINERARY PLANNER - SUPABASE POSTGRESQL SCHEMA
-- ==============================================================================

create extension if not exists "uuid-ossp";

-- 1. TRIPS TABLE
create table if not exists public.trips (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references auth.users(id) on delete cascade,
    title text not null,
    destination text not null,
    party_type text check (party_type in ('solo', 'couple', 'group', 'family')) default 'solo',
    party_size integer default 1 check (party_size >= 1),
    budget_tier text check (budget_tier in ('budget', 'moderate', 'luxury')) default 'moderate',
    pacing text check (pacing in ('relaxed', 'moderate', 'fast_paced')) default 'moderate',
    estimated_total_cost numeric(10, 2) default 0.00,
    raw_ai_response jsonb not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. ITINERARY DAYS TABLE
create table if not exists public.itinerary_days (
    id uuid primary key default uuid_generate_v4(),
    trip_id uuid references public.trips(id) on delete cascade not null,
    day_number integer not null check (day_number >= 1),
    theme text,
    area_focus text,
    day_estimated_cost numeric(10, 2) default 0.00,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. ACTIVITIES TABLE
create table if not exists public.activities (
    id uuid primary key default uuid_generate_v4(),
    day_id uuid references public.itinerary_days(id) on delete cascade not null,
    order_index integer not null default 0,
    time_slot text not null,
    title text not null,
    category text check (category in ('attraction', 'dining', 'transport', 'leisure', 'accommodation')) default 'attraction',
    description text,
    neighborhood text,
    estimated_cost_usd numeric(10, 2) default 0.00,
    booking_required boolean default false,
    pacing_tag text default 'standard',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- INDEXES FOR FAST QUERYING
create index if not exists idx_trips_user_id on public.trips(user_id);
create index if not exists idx_itinerary_days_trip on public.itinerary_days(trip_id);
create index if not exists idx_activities_day on public.activities(day_id);

-- ROW LEVEL SECURITY (RLS) POLICIES
alter table public.trips enable row level security;
alter table public.itinerary_days enable row level security;
alter table public.activities enable row level security;

-- Allow public read/write if unauthenticated or authenticated user access
create policy "Allow anonymous and authenticated read access"
on public.trips for select
using (true);

create policy "Allow anonymous and authenticated insert"
on public.trips for insert
with check (true);

create policy "Allow anonymous and authenticated update"
on public.trips for update
using (true);
