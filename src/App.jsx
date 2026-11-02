import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ScenarioPresets, { SCENARIOS } from './components/ScenarioPresets';
import TripWizard from './components/TripWizard';
import ItineraryDashboard from './components/ItineraryDashboard';
import SavedTrips from './components/SavedTrips';
import { 
  checkBackendHealth, 
  generateTrip, 
  regenerateDay, 
  swapActivity,
  listSavedTrips,
  getTripById,
  saveTrip,
  updateTrip,
  deleteTrip,
  duplicateTrip
} from './services/api';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export default function App() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [itinerary, setItinerary] = useState(null);
  const [savedTrips, setSavedTrips] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successToast, setSuccessToast] = useState(null);
  const [activeTab, setActiveTab] = useState('planner');
  const [wizardValues, setWizardValues] = useState(SCENARIOS[0].data);

  // Show auto-dismiss toast
  const triggerToast = (msg) => {
    setSuccessToast(msg);
    setTimeout(() => setSuccessToast(null), 4000);
  };

  const refreshSavedTrips = async () => {
    try {
      const data = await listSavedTrips();
      setSavedTrips(data.trips || []);
    } catch (e) {
      console.warn("Could not fetch saved trips:", e);
    }
  };

  useEffect(() => {
    // 1. Check backend health
    checkBackendHealth().then((status) => {
      setBackendStatus(status);
    });

    // 2. Fetch saved trips from database
    refreshSavedTrips();

    // 3. Auto-generate Scenario 1 for immediate visual interactivity
    handleGenerateTrip(SCENARIOS[0].data);
  }, []);

  const handleGenerateTrip = async (params) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const data = await generateTrip(params);
      setItinerary(data);
      refreshSavedTrips();
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to generate itinerary. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPreset = (presetData) => {
    setWizardValues(presetData);
    handleGenerateTrip(presetData);
    setActiveTab('planner');
  };

  const handleRegenerateDay = async (dayNumber, currentTheme, newVibe) => {
    if (!itinerary) return;
    const payload = {
      trip_id: itinerary.trip_id,
      destination: itinerary.destination,
      day_number: dayNumber,
      current_theme: currentTheme,
      new_preference_or_vibe: newVibe,
      budget_tier: itinerary.budget_tier,
      party_type: itinerary.party_type,
    };

    const newDay = await regenerateDay(payload);
    
    // Immutably replace the day in state
    setItinerary((prev) => {
      const updatedDays = prev.itinerary.map((d) => 
        d.day_number === dayNumber ? newDay : d
      );
      const newTotalPerPerson = updatedDays.reduce((acc, d) => acc + d.day_estimated_cost_usd, 0);
      return {
        ...prev,
        itinerary: updatedDays,
        cost_per_person_usd: Math.round(newTotalPerPerson),
        estimated_total_cost_usd: Math.round(newTotalPerPerson * prev.party_size)
      };
    });
    triggerToast(`Day ${dayNumber} successfully regenerated and persisted!`);
    refreshSavedTrips();
  };

  const handleActivitySwapped = async (swapPayload) => {
    const newActivity = await swapActivity(swapPayload);
    
    setItinerary((prev) => {
      const updatedDays = prev.itinerary.map((d) => {
        if (d.day_number === swapPayload.day_number) {
          const updatedActs = d.activities.map((a) => 
            a.id === swapPayload.activity_id ? newActivity : a
          );
          const newDayCost = updatedActs.reduce((acc, act) => acc + act.estimated_cost_usd, 0);
          return {
            ...d,
            activities: updatedActs,
            day_estimated_cost_usd: Math.round(newDayCost)
          };
        }
        return d;
      });

      const newTotalPerPerson = updatedDays.reduce((acc, d) => acc + d.day_estimated_cost_usd, 0);
      return {
        ...prev,
        itinerary: updatedDays,
        cost_per_person_usd: Math.round(newTotalPerPerson),
        estimated_total_cost_usd: Math.round(newTotalPerPerson * prev.party_size)
      };
    });
    triggerToast("Activity swapped and saved to database!");
    refreshSavedTrips();
  };

  // Database CRUD Handlers
  const handleLoadTrip = async (tripId) => {
    setIsLoading(true);
    try {
      const fullTrip = await getTripById(tripId);
      setItinerary(fullTrip);
      setActiveTab('planner');
      triggerToast(`Loaded "${fullTrip.trip_title}" from database!`);
    } catch (err) {
      setErrorMsg("Failed to load trip: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleManualSave = async (tripToSave) => {
    try {
      const saved = await saveTrip(tripToSave);
      setItinerary(saved);
      refreshSavedTrips();
      triggerToast("Trip successfully saved to persistent database!");
    } catch (err) {
      setErrorMsg("Failed to save trip: " + err.message);
    }
  };

  const handleUpdateTrip = async (tripId, updates) => {
    try {
      const updated = await updateTrip(tripId, updates);
      if (itinerary && itinerary.trip_id === tripId) {
        setItinerary(updated);
      }
      refreshSavedTrips();
      triggerToast("Trip updated in database!");
    } catch (err) {
      setErrorMsg("Failed to update trip: " + err.message);
    }
  };

  const handleDeleteTrip = async (tripId) => {
    try {
      await deleteTrip(tripId);
      refreshSavedTrips();
      if (itinerary && itinerary.trip_id === tripId) {
        setItinerary(null);
      }
      triggerToast("Trip deleted from database.");
    } catch (err) {
      setErrorMsg("Failed to delete trip: " + err.message);
    }
  };

  const handleDuplicateTrip = async (tripId) => {
    try {
      const duplicated = await duplicateTrip(tripId);
      refreshSavedTrips();
      triggerToast(`Cloned "${duplicated.trip_title}" in database!`);
    } catch (err) {
      setErrorMsg("Failed to duplicate trip: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar 
        backendStatus={backendStatus} 
        activeTab={activeTab}
        onTabChange={setActiveTab}
        savedTripsCount={savedTrips.length}
      />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Toast Notification */}
        {successToast && (
          <div className="mb-6 p-4 rounded-2xl bg-teal-50 border border-teal-200 text-teal-900 flex items-center gap-3 shadow-sm animate-fade-in">
            <CheckCircle2 className="w-5 h-5 shrink-0 text-teal-600" />
            <p className="text-xs sm:text-sm font-semibold">{successToast}</p>
          </div>
        )}

        {/* Error Alert */}
        {errorMsg && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 flex items-center gap-3 shadow-sm">
            <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
            <p className="text-xs sm:text-sm font-medium">{errorMsg}</p>
          </div>
        )}

        {/* TAB 1: TRIP PLANNER & ITINERARY */}
        {activeTab === 'planner' && (
          <>
            {/* Scenario 1, 2, 3 Quick Loaders */}
            <ScenarioPresets 
              onSelectPreset={handleSelectPreset}
              isLoading={isLoading}
            />

            {/* Trip Builder Wizard */}
            <TripWizard
              onGenerate={handleGenerateTrip}
              isLoading={isLoading}
              initialValues={wizardValues}
            />

            {/* Main Itinerary View */}
            {itinerary && (
              <ItineraryDashboard
                itinerary={itinerary}
                onRegenerateDay={handleRegenerateDay}
                onActivitySwapped={handleActivitySwapped}
                onSaveTrip={handleManualSave}
                onUpdateTrip={handleUpdateTrip}
                onDuplicateTrip={handleDuplicateTrip}
              />
            )}
          </>
        )}

        {/* TAB 2: SAVED TRIPS HISTORY DASHBOARD */}
        {activeTab === 'saved_trips' && (
          <SavedTrips
            trips={savedTrips}
            onLoadTrip={handleLoadTrip}
            onDeleteTrip={handleDeleteTrip}
            onDuplicateTrip={handleDuplicateTrip}
            onUpdateTrip={handleUpdateTrip}
            onNavigateToPlanner={() => setActiveTab('planner')}
          />
        )}

      </main>

      <footer className="border-t border-slate-200 bg-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-500">
          Personalized Travel Itinerary Planner • Full-stack GenAI Architecture (React + FastAPI + Supabase Persistent Storage)
        </div>
      </footer>
    </div>
  );
}
