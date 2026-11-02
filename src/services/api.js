const API_BASE = '/api';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (error) {
    console.warn('Backend health check error:', error);
    return null;
  }
}

export async function generateTrip(payload) {
  const res = await fetch(`${API_BASE}/trips/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to generate itinerary' }));
    throw new Error(err.detail || 'Trip generation failed');
  }
  return await res.json();
}

export async function regenerateDay(payload) {
  const res = await fetch(`${API_BASE}/trips/regenerate-day`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to regenerate day' }));
    throw new Error(err.detail || 'Day regeneration failed');
  }
  return await res.json();
}

export async function swapActivity(payload) {
  const res = await fetch(`${API_BASE}/trips/swap-activity`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to swap activity' }));
    throw new Error(err.detail || 'Activity swap failed');
  }
  return await res.json();
}

// ==========================================
// SUPABASE DATABASE CRUD OPERATIONS
// ==========================================

export async function listSavedTrips(params = {}) {
  const queryParams = new URLSearchParams();
  if (params.query) queryParams.append('query', params.query);
  if (params.party_type) queryParams.append('party_type', params.party_type);
  if (params.budget_tier) queryParams.append('budget_tier', params.budget_tier);
  
  const res = await fetch(`${API_BASE}/trips?${queryParams.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch saved trips');
  return await res.json();
}

export async function getTripById(tripId) {
  const res = await fetch(`${API_BASE}/trips/${tripId}`);
  if (!res.ok) throw new Error('Failed to retrieve trip');
  return await res.json();
}

export async function saveTrip(tripPayload) {
  const res = await fetch(`${API_BASE}/trips`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tripPayload),
  });
  if (!res.ok) throw new Error('Failed to save trip to database');
  return await res.json();
}

export async function updateTrip(tripId, updates) {
  const res = await fetch(`${API_BASE}/trips/${tripId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error('Failed to update trip');
  return await res.json();
}

export async function deleteTrip(tripId) {
  const res = await fetch(`${API_BASE}/trips/${tripId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete trip');
  return await res.json();
}

export async function duplicateTrip(tripId) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/duplicate`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to duplicate trip');
  return await res.json();
}
