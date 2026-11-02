import React, { useState } from 'react';
import { 
  MapPin, Calendar, Users, DollarSign, Clock, 
  Trash2, Copy, Edit3, ArrowRight, Search, 
  Filter, Sparkles, AlertCircle, Check, X, Bookmark 
} from 'lucide-react';

export default function SavedTrips({ 
  trips, 
  onLoadTrip, 
  onDeleteTrip, 
  onDuplicateTrip, 
  onUpdateTrip, 
  onNavigateToPlanner 
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPartyFilter, setSelectedPartyFilter] = useState('all');
  const [editingTrip, setEditingTrip] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  // Filter trips based on search query and party type
  const filteredTrips = trips.filter((t) => {
    const matchesSearch = 
      t.destination.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.trip_title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesParty = 
      selectedPartyFilter === 'all' || t.party_type === selectedPartyFilter;
    return matchesSearch && matchesParty;
  });

  const handleStartEdit = (trip) => {
    setEditingTrip(trip);
    setEditTitle(trip.trip_title);
    setEditNotes(trip.summary || '');
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editingTrip) return;
    await onUpdateTrip(editingTrip.trip_id, {
      trip_title: editTitle,
      summary: editNotes
    });
    setEditingTrip(null);
  };

  const handleDeleteConfirm = async (tripId) => {
    if (window.confirm("Are you sure you want to delete this trip from persistent storage?")) {
      setDeletingId(tripId);
      try {
        await onDeleteTrip(tripId);
      } finally {
        setDeletingId(null);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <Bookmark className="w-5 h-5 text-teal-600" />
              Saved Trips History
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Securely stored in database. Manage, edit, re-open, or duplicate your itineraries anytime.
            </p>
          </div>

          <button
            onClick={onNavigateToPlanner}
            className="self-start sm:self-auto px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs shadow-md shadow-teal-600/20 flex items-center gap-1.5 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Create New Itinerary</span>
          </button>
        </div>

        {/* Search and Filters */}
        <div className="pt-4 flex flex-col md:flex-row gap-3 items-center justify-between">
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search destination or trip title..."
              className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 bg-slate-50/50"
            />
          </div>

          {/* Party Filter Chips */}
          <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mr-1 hidden sm:inline">
              Filter:
            </span>
            {['all', 'solo', 'couple', 'group'].map((filter) => (
              <button
                key={filter}
                onClick={() => setSelectedPartyFilter(filter)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold capitalize transition-all shrink-0 ${
                  selectedPartyFilter === filter
                    ? 'bg-teal-600 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {filter === 'all' ? 'All Trips' : filter}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Trips Grid */}
      {filteredTrips.length === 0 ? (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3">
            <Bookmark className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-slate-800 text-base">No Saved Trips Found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {searchQuery 
              ? `No itineraries match "${searchQuery}". Try clearing your search.` 
              : "You haven't saved any travel itineraries yet. Generate one in the Planner to save it here!"}
          </p>
          <button
            onClick={onNavigateToPlanner}
            className="mt-4 px-4 py-2 rounded-xl bg-teal-600 text-white font-bold text-xs hover:bg-teal-700 transition-colors"
          >
            Go to Trip Planner
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTrips.map((trip) => (
            <div 
              key={trip.trip_id}
              className="bg-white rounded-3xl border border-slate-200/90 p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                {/* Card Header */}
                <div className="flex items-start justify-between gap-2 mb-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-teal-50 text-teal-800 border border-teal-200">
                    {trip.destination}
                  </span>
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <span className="capitalize text-[11px] font-medium bg-slate-100 px-2 py-0.5 rounded-full">
                      {trip.party_type} • {trip.total_days}d
                    </span>
                  </div>
                </div>

                {/* Title & Summary */}
                <h3 className="font-extrabold text-slate-900 text-base group-hover:text-teal-700 transition-colors line-clamp-1">
                  {trip.trip_title}
                </h3>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                  {trip.summary || "Full day-by-day itinerary tailored to user preferences and spatial clustering."}
                </p>

                {/* Metadata Pills */}
                <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-50 p-2 rounded-xl border border-slate-100">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Total Est.</span>
                    <span className="font-extrabold text-slate-800">${trip.estimated_total_cost_usd}</span>
                  </div>
                  <div className="bg-slate-50 p-2 rounded-xl border border-slate-100">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Per Person</span>
                    <span className="font-extrabold text-teal-700">${trip.cost_per_person_usd}</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                <button
                  onClick={() => onLoadTrip(trip.trip_id)}
                  className="px-3.5 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs flex items-center gap-1 transition-colors shadow-sm"
                >
                  <span>Open Itinerary</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleStartEdit(trip)}
                    title="Edit title & notes"
                    className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => onDuplicateTrip(trip.trip_id)}
                    title="Duplicate trip"
                    className="p-2 text-slate-400 hover:text-teal-600 hover:bg-teal-50 rounded-lg transition-colors"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>

                  <button
                    disabled={deletingId === trip.trip_id}
                    onClick={() => handleDeleteConfirm(trip.trip_id)}
                    title="Delete trip from database"
                    className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {editingTrip && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <form onSubmit={handleSaveEdit} className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-teal-600" />
                Edit Trip Details
              </h3>
              <button
                type="button"
                onClick={() => setEditingTrip(null)}
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
                className="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                Summary / Notes
              </label>
              <textarea
                rows={3}
                value={editNotes}
                onChange={(e) => setEditNotes(e.target.value)}
                className="w-full px-3.5 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setEditingTrip(null)}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs"
              >
                Save Changes
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
