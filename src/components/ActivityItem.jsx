import React, { useState } from 'react';
import { 
  Camera, Utensils, Coffee, Bus, Bed, 
  MapPin, Clock, DollarSign, RefreshCw, AlertCircle, Check,
  Accessibility, UtensilsCrossed 
} from 'lucide-react';

const CATEGORY_CONFIG = {
  attraction: { label: 'Attraction', icon: Camera, color: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  dining: { label: 'Dining', icon: Utensils, color: 'bg-amber-50 text-amber-700 border-amber-200' },
  leisure: { label: 'Leisure', icon: Coffee, color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  transport: { label: 'Transit', icon: Bus, color: 'bg-blue-50 text-blue-700 border-blue-200' },
  accommodation: { label: 'Stay', icon: Bed, color: 'bg-purple-50 text-purple-700 border-purple-200' },
};

export default function ActivityItem({ 
  activity, 
  dayNumber, 
  destination, 
  budgetTier, 
  dietaryRestrictions = [],
  mobilityLevel = 'standard',
  onActivitySwapped 
}) {
  const [isSwapping, setIsSwapping] = useState(false);
  const [showSwapModal, setShowSwapModal] = useState(false);
  const [swapReason, setSwapReason] = useState('Prefer an alternative local venue');

  const config = CATEGORY_CONFIG[activity.category] || CATEGORY_CONFIG.attraction;
  const CategoryIcon = config.icon;

  const handleSwap = async () => {
    setIsSwapping(true);
    try {
      await onActivitySwapped({
        trip_id: 'active_trip',
        destination,
        day_number: dayNumber,
        activity_id: activity.id,
        activity_category: activity.category,
        neighborhood: activity.neighborhood,
        reason: swapReason,
        budget_tier: budgetTier,
        dietary_restrictions: dietaryRestrictions,
        mobility_level: mobilityLevel
      });
      setShowSwapModal(false);
    } catch (err) {
      alert(`Swap failed: ${err.message}`);
    } finally {
      setIsSwapping(false);
    }
  };

  return (
    <div className="relative group bg-white rounded-2xl border border-slate-200/90 p-4 transition-all duration-200 hover:shadow-md hover:border-slate-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2.5">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${config.color}`}>
            <CategoryIcon className="w-3 h-3" />
            {config.label}
          </span>
          <span className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
            <Clock className="w-3 h-3 text-slate-400" />
            {activity.time_slot}
          </span>
          {activity.neighborhood && (
            <span className="inline-flex items-center gap-1 text-xs text-slate-600 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-full">
              <MapPin className="w-3 h-3 text-slate-400" />
              {activity.neighborhood}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          {activity.booking_required && (
            <span className="text-[10px] font-bold uppercase tracking-wider bg-rose-50 text-rose-700 border border-rose-200 px-2 py-0.5 rounded-md flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              Booking Advised
            </span>
          )}
          <span className="text-xs font-bold text-slate-700 bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-0.5 rounded-full">
            {activity.estimated_cost_usd > 0 ? `$${activity.estimated_cost_usd}` : 'Free'}
          </span>
        </div>
      </div>

      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1.5 flex-1">
          <h4 className="font-bold text-slate-900 text-sm sm:text-base group-hover:text-teal-700 transition-colors">
            {activity.title}
          </h4>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            {activity.description}
          </p>

          {/* Personalization Badges: Dietary & Accessibility */}
          <div className="flex items-center gap-2 flex-wrap pt-1">
            {activity.dietary_tags && activity.dietary_tags.length > 0 && (
              activity.dietary_tags.map((diet, idx) => (
                <span 
                  key={idx} 
                  className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200"
                >
                  <UtensilsCrossed className="w-2.5 h-2.5 text-amber-600" />
                  {diet}
                </span>
              ))
            )}

            {activity.accessibility_note && (
              <span className="inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-md bg-blue-50 text-blue-800 border border-blue-200">
                <Accessibility className="w-2.5 h-2.5 text-blue-600" />
                {activity.accessibility_note}
              </span>
            )}
          </div>
        </div>

        {/* Swap button */}
        <button
          onClick={() => setShowSwapModal(true)}
          title="Swap this activity for an alternative nearby venue"
          className="shrink-0 p-2 text-slate-400 hover:text-teal-600 hover:bg-teal-50 rounded-xl transition-all"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Swap Modal */}
      {showSwapModal && (
        <div className="mt-4 pt-3 border-t border-slate-100 bg-slate-50 -mx-4 -mb-4 p-4 rounded-b-2xl">
          <p className="text-xs font-bold text-slate-700 mb-2">
            Swap "{activity.title}" with alternative:
          </p>
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={swapReason}
              onChange={(e) => setSwapReason(e.target.value)}
              placeholder="e.g. Prefer outdoor cafe, quieter spot, vegetarian menu"
              className="flex-1 text-xs px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500 bg-white"
            />
            <div className="flex gap-2">
              <button
                disabled={isSwapping}
                onClick={handleSwap}
                className="px-3 py-2 text-xs font-bold bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors flex items-center gap-1 disabled:opacity-60"
              >
                {isSwapping ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                Confirm Swap
              </button>
              <button
                onClick={() => setShowSwapModal(false)}
                className="px-3 py-2 text-xs font-semibold text-slate-500 hover:text-slate-700 bg-white border border-slate-200 rounded-lg"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
