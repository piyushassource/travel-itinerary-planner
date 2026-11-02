import React, { useState } from 'react';
import { 
  Sparkles, Calendar, MapPin, DollarSign, 
  RefreshCw, Check, X, Compass 
} from 'lucide-react';
import ActivityItem from './ActivityItem';

export default function DayCard({ 
  day, 
  destination, 
  budgetTier, 
  partyType, 
  dietaryRestrictions = [],
  mobilityLevel = 'standard',
  onRegenerateDay, 
  onActivitySwapped 
}) {
  const [showRegenModal, setShowRegenModal] = useState(false);
  const [regenVibe, setRegenVibe] = useState('');
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleRegenerate = async (e) => {
    e.preventDefault();
    if (!regenVibe.trim()) return;
    setIsRegenerating(true);
    try {
      await onRegenerateDay(day.day_number, day.theme, regenVibe);
      setShowRegenModal(false);
      setRegenVibe('');
    } catch (err) {
      alert(`Regeneration failed: ${err.message}`);
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="bg-slate-50/70 rounded-3xl border border-slate-200/80 p-5 sm:p-6 mb-6 shadow-sm">
      {/* Day Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-200">
        <div className="flex items-start gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-teal-600 text-white flex flex-col items-center justify-center font-extrabold shadow-md shadow-teal-600/20 shrink-0">
            <span className="text-[10px] uppercase font-semibold leading-none">DAY</span>
            <span className="text-lg leading-tight">{day.day_number}</span>
          </div>

          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-extrabold text-slate-900 text-base sm:text-lg">
                {day.theme}
              </h3>
            </div>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              <span className="inline-flex items-center gap-1 text-xs font-semibold text-teal-800 bg-teal-50 border border-teal-200 px-2.5 py-0.5 rounded-full">
                <Compass className="w-3 h-3 text-teal-600" />
                Cluster: {day.area_focus}
              </span>
              <span className="inline-flex items-center gap-1 text-xs font-bold text-slate-700 bg-white border border-slate-200 px-2.5 py-0.5 rounded-full">
                Day Cost: ${day.day_estimated_cost_usd}
              </span>
            </div>
          </div>
        </div>

        <button
          onClick={() => setShowRegenModal(true)}
          className="self-start sm:self-auto px-4 py-2 rounded-xl bg-white hover:bg-teal-50 border border-slate-200 hover:border-teal-300 text-slate-700 hover:text-teal-700 text-xs font-bold shadow-sm transition-all flex items-center gap-1.5"
        >
          <Sparkles className="w-3.5 h-3.5 text-teal-600" />
          <span>Regenerate Day {day.day_number}</span>
        </button>
      </div>

      {/* Regenerate Modal / Accordion */}
      {showRegenModal && (
        <form onSubmit={handleRegenerate} className="mt-4 p-4 rounded-2xl bg-white border border-teal-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold uppercase tracking-wider text-teal-900 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-teal-600" />
              Customize Vibe for Day {day.day_number}
            </h4>
            <button 
              type="button" 
              onClick={() => setShowRegenModal(false)}
              className="text-slate-400 hover:text-slate-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <p className="text-xs text-slate-500">
            Tell the AI how to re-orchestrate Day {day.day_number} without changing your other days.
          </p>

          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              required
              value={regenVibe}
              onChange={(e) => setRegenVibe(e.target.value)}
              placeholder="e.g. Romantic sunset wine tour, vintage thrift crawl, or museum-heavy day"
              className="flex-1 text-xs px-3.5 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
            />
            <button
              type="submit"
              disabled={isRegenerating}
              className="px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-colors disabled:opacity-60"
            >
              {isRegenerating ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
              Re-Roll Day
            </button>
          </div>
        </form>
      )}

      {/* Activity Timeline */}
      <div className="mt-5 space-y-3">
        {day.activities.map((act) => (
          <ActivityItem
            key={act.id}
            activity={act}
            dayNumber={day.day_number}
            destination={destination}
            budgetTier={budgetTier}
            dietaryRestrictions={dietaryRestrictions}
            mobilityLevel={mobilityLevel}
            onActivitySwapped={onActivitySwapped}
          />
        ))}
      </div>
    </div>
  );
}
