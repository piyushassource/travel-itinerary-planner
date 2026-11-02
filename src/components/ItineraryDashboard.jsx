import React, { useState } from 'react';
import { 
  Compass, MapPin, Calendar, Clock, 
  Users, DollarSign, Gauge, Sparkles, Filter,
  Bookmark, Check, Edit3, Copy, X
} from 'lucide-react';
import DayCard from './DayCard';
import CostSummary from './CostSummary';

export default function ItineraryDashboard({ 
  itinerary, 
  onRegenerateDay, 
  onActivitySwapped,
  onSaveTrip,
  onUpdateTrip,
  onDuplicateTrip
}) {
  const [selectedDayFilter, setSelectedDayFilter] = useState('all');
  const [isSaved, setIsSaved] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editTitle, setEditTitle] = useState(itinerary.trip_title);
  const [editNotes, setEditNotes] = useState(itinerary.summary);

  // Sync title when itinerary changes
  React.useEffect(() => {
    setEditTitle(itinerary.trip_title);
    setEditNotes(itinerary.summary);
    setIsSaved(true);
  }, [itinerary.trip_id]);

  const filteredDays = selectedDayFilter === 'all'
    ? itinerary.itinerary
    : itinerary.itinerary.filter((d) => d.day_number === parseInt(selectedDayFilter));

  const handleManualSave = async () => {
    if (onSaveTrip) {
      await onSaveTrip(itinerary);
      setIsSaved(true);
    }
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (onUpdateTrip) {
      await onUpdateTrip(itinerary.trip_id, {
        trip_title: editTitle,
        summary: editNotes
      });
      setShowEditModal(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Banner */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-teal-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider bg-teal-500/20 text-teal-300 border border-teal-500/30 px-3 py-1 rounded-full">
                {itinerary.party_type} Journey • {itinerary.party_size} traveler{itinerary.party_size > 1 ? 's' : ''}
              </span>
              <span className="text-[11px] font-bold uppercase tracking-wider bg-white/10 text-slate-200 px-3 py-1 rounded-full">
                {itinerary.budget_tier} Tier
              </span>
              <span className="text-[11px] font-bold uppercase tracking-wider bg-white/10 text-slate-200 px-3 py-1 rounded-full">
                {itinerary.pacing} Pacing
              </span>
            </div>

            {/* Persistence & Action Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowEditModal(true)}
                className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition-all flex items-center gap-1.5"
                title="Edit trip title & custom notes"
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Edit Details</span>
              </button>

              {onDuplicateTrip && (
                <button
                  onClick={() => onDuplicateTrip(itinerary.trip_id)}
                  className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition-all flex items-center gap-1.5"
                  title="Clone this trip in database"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Duplicate</span>
                </button>
              )}

              <button
                onClick={handleManualSave}
                className="px-3.5 py-1.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs transition-all flex items-center gap-1.5 shadow-sm"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Saved to Database</span>
              </button>
            </div>
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
            {itinerary.trip_title}
          </h1>

          <p className="mt-3 text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
            {itinerary.summary}
          </p>
        </div>

        {/* Decorative background glow */}
        <div className="absolute -right-10 -bottom-10 w-72 h-72 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* Day Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <button
          onClick={() => setSelectedDayFilter('all')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shrink-0 ${
            selectedDayFilter === 'all'
              ? 'bg-teal-600 text-white shadow-sm'
              : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          All {itinerary.total_days} Days
        </button>

        {itinerary.itinerary.map((d) => (
          <button
            key={d.day_number}
            onClick={() => setSelectedDayFilter(d.day_number.toString())}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shrink-0 ${
              selectedDayFilter === d.day_number.toString()
                ? 'bg-teal-600 text-white shadow-sm'
                : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            Day {d.day_number} ({d.area_focus})
          </button>
        ))}
      </div>

      {/* Main Grid: Days on Left, Cost & Logistics on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Timeline Column */}
        <div className="lg:col-span-2 space-y-6">
          {filteredDays.map((day) => (
            <DayCard
              key={day.day_number}
              day={day}
              destination={itinerary.destination}
              budgetTier={itinerary.budget_tier}
              partyType={itinerary.party_type}
              onRegenerateDay={onRegenerateDay}
              onActivitySwapped={onActivitySwapped}
            />
          ))}
        </div>

        {/* Financial & Logistics Sidebar */}
        <div className="lg:sticky lg:top-24">
          <CostSummary itinerary={itinerary} />
        </div>
      </div>

      {/* Edit Details Modal */}
      {showEditModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleSaveEdit} className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-teal-600" />
                Edit Trip Title & Notes
              </h3>
              <button
                type="button"
                onClick={() => setShowEditModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Trip Title
              </label>
              <input
                type="text"
                required
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 font-medium text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Trip Summary / Notes
              </label>
              <textarea
                rows={3}
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                className="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 text-slate-700"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowEditModal(false)}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs"
              >
                Save to Database
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
