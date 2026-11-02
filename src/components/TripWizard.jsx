import React, { useState } from 'react';
import { 
  MapPin, Calendar, Users, DollarSign, Gauge, 
  Sparkles, Check, ChevronDown, ChevronUp, Loader2,
  UtensilsCrossed, Accessibility, ShieldAlert
} from 'lucide-react';

const INTEREST_OPTIONS = [
  'Sightseeing', 'Food & Dining', 'Art & Museums', 
  'Historic Culture', 'Nightlife', 'Nature & Parks', 
  'Shopping', 'Hidden Gems', 'Romantic Vistas'
];

const DIETARY_OPTIONS = [
  'Vegetarian', 'Vegan', 'Halal', 'Kosher', 'Gluten-Free', 'Dairy-Free', 'Nut-Free'
];

const MOBILITY_OPTIONS = [
  { id: 'standard', label: 'Standard Mobility', desc: 'Typical pedestrian & metro steps' },
  { id: 'low_walking', label: 'Low Walking', desc: 'Short distances & minimal stairs' },
  { id: 'wheelchair_step_free', label: 'Step-Free / Accessible', desc: 'Ramps, elevators & flat paths' }
];

export default function TripWizard({ onGenerate, isLoading, initialValues }) {
  const [isOpen, setIsOpen] = useState(true);
  const [formData, setFormData] = useState(initialValues || {
    destination: 'Tokyo, Japan',
    days: 3,
    travel_dates: 'Upcoming Weekend',
    party_type: 'solo',
    party_size: 1,
    budget_tier: 'budget',
    pacing: 'fast_paced',
    dietary_restrictions: [],
    mobility_level: 'standard',
    interests: ['Sightseeing', 'Food & Dining'],
    accommodation_area: 'Shinjuku',
    custom_notes: ''
  });

  // Sync if initialValues changes (e.g. from preset click)
  React.useEffect(() => {
    if (initialValues) {
      setFormData(initialValues);
    }
  }, [initialValues]);

  const toggleInterest = (interest) => {
    setFormData((prev) => {
      const exists = prev.interests.includes(interest);
      return {
        ...prev,
        interests: exists 
          ? prev.interests.filter((i) => i !== interest)
          : [...prev.interests, interest]
      };
    });
  };

  const toggleDietary = (diet) => {
    setFormData((prev) => {
      const current = prev.dietary_restrictions || [];
      const exists = current.includes(diet);
      return {
        ...prev,
        dietary_restrictions: exists
          ? current.filter((d) => d !== diet)
          : [...current, diet]
      };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onGenerate(formData);
  };

  return (
    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden mb-8">
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="px-6 py-5 flex items-center justify-between cursor-pointer border-b border-slate-100 hover:bg-slate-50/60 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center font-bold">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900">AI Prompt & Personalization Architect</h3>
            <p className="text-xs text-slate-500">Fine-tune dynamic prompt parameters: pacing, party dynamics, dietary needs & mobility</p>
          </div>
        </div>

        <button className="text-slate-400 hover:text-slate-600">
          {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {isOpen && (
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          
          {/* Row 1: Destination, Duration, Travel Dates */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                Destination City
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
                <input
                  type="text"
                  required
                  value={formData.destination}
                  onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                  placeholder="e.g. Tokyo, Paris, Rome, New York"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium text-slate-800"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                Duration (Days: {formData.days})
              </label>
              <div className="relative flex items-center gap-3">
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={formData.days}
                  onChange={(e) => setFormData({ ...formData, days: parseInt(e.target.value) })}
                  className="w-full accent-teal-600 h-2 bg-slate-100 rounded-lg cursor-pointer"
                />
                <span className="w-10 text-center font-bold text-sm text-teal-700 bg-teal-50 py-1 rounded-md border border-teal-200">
                  {formData.days}d
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                Travel Dates / Window (Optional)
              </label>
              <div className="relative">
                <Calendar className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
                <input
                  type="text"
                  value={formData.travel_dates || ''}
                  onChange={(e) => setFormData({ ...formData, travel_dates: e.target.value })}
                  placeholder="e.g. Nov 12 - Nov 15 / Weekend Getaway"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-slate-800"
                />
              </div>
            </div>
          </div>

          {/* Row 2: Travel Party, Budget Tier, Pacing */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2 border-t border-slate-100">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                Travel Party
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: 'solo', label: 'Solo' },
                  { id: 'couple', label: 'Couple' },
                  { id: 'group', label: 'Group' }
                ].map((pt) => (
                  <button
                    type="button"
                    key={pt.id}
                    onClick={() => setFormData({ 
                      ...formData, 
                      party_type: pt.id,
                      party_size: pt.id === 'solo' ? 1 : (pt.id === 'couple' ? 2 : Math.max(3, formData.party_size || 4))
                    })}
                    className={`py-2 px-3 text-xs font-semibold rounded-xl border transition-all ${
                      formData.party_type === pt.id
                        ? 'bg-teal-600 text-white border-teal-600 shadow-sm'
                        : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    {pt.label}
                  </button>
                ))}
              </div>

              {formData.party_type === 'group' && (
                <div className="mt-3 flex items-center justify-between bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-600 font-medium">Group Members:</span>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, party_size: Math.max(2, (formData.party_size || 4) - 1) })}
                      className="w-6 h-6 rounded-md bg-white border border-slate-200 flex items-center justify-center font-bold text-slate-700 hover:bg-slate-100"
                    >-</button>
                    <span className="text-xs font-bold text-slate-900 w-5 text-center">{formData.party_size || 4}</span>
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, party_size: Math.min(20, (formData.party_size || 4) + 1) })}
                      className="w-6 h-6 rounded-md bg-white border border-slate-200 flex items-center justify-center font-bold text-slate-700 hover:bg-slate-100"
                    >+</button>
                  </div>
                </div>
              )}
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                Budget Tier
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: 'budget', label: 'Budget ($)' },
                  { id: 'moderate', label: 'Moderate ($$)' },
                  { id: 'luxury', label: 'Luxury ($$$)' }
                ].map((b) => (
                  <button
                    type="button"
                    key={b.id}
                    onClick={() => setFormData({ ...formData, budget_tier: b.id })}
                    className={`py-2 px-2 text-xs font-semibold rounded-xl border transition-all ${
                      formData.budget_tier === b.id
                        ? 'bg-teal-600 text-white border-teal-600 shadow-sm'
                        : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    {b.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                Activity Pacing
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: 'relaxed', label: 'Relaxed (2-3 stops)' },
                  { id: 'moderate', label: 'Balanced (3-4 stops)' },
                  { id: 'fast_paced', label: 'Fast (5-6 stops)' }
                ].map((p) => (
                  <button
                    type="button"
                    key={p.id}
                    onClick={() => setFormData({ ...formData, pacing: p.id })}
                    className={`py-2 px-1.5 text-[11px] font-semibold rounded-xl border transition-all ${
                      formData.pacing === p.id
                        ? 'bg-teal-600 text-white border-teal-600 shadow-sm'
                        : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Row 3: Dietary Restrictions & Mobility Constraints */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 border-t border-slate-100">
            {/* Dietary */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2 flex items-center gap-1.5">
                <UtensilsCrossed className="w-3.5 h-3.5 text-amber-600" />
                Dietary Restrictions
              </label>
              <div className="flex flex-wrap gap-1.5">
                {DIETARY_OPTIONS.map((diet) => {
                  const selected = (formData.dietary_restrictions || []).includes(diet);
                  return (
                    <button
                      type="button"
                      key={diet}
                      onClick={() => toggleDietary(diet)}
                      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1 ${
                        selected
                          ? 'bg-amber-100 border border-amber-300 text-amber-900 font-bold'
                          : 'bg-slate-50 border border-slate-200 text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      {selected && <Check className="w-3 h-3 text-amber-600" />}
                      {diet}
                    </button>
                  );
                })}
              </div>
              <p className="text-[11px] text-slate-400 mt-1.5">AI will exclusively recommend restaurants offering verified options.</p>
            </div>

            {/* Mobility */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2 flex items-center gap-1.5">
                <Accessibility className="w-3.5 h-3.5 text-blue-600" />
                Mobility & Accessibility Level
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {MOBILITY_OPTIONS.map((m) => {
                  const selected = (formData.mobility_level || 'standard') === m.id;
                  return (
                    <button
                      type="button"
                      key={m.id}
                      onClick={() => setFormData({ ...formData, mobility_level: m.id })}
                      className={`p-2 rounded-xl text-left border transition-all ${
                        selected
                          ? 'bg-blue-50 border-blue-400 text-blue-900 shadow-sm'
                          : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      <div className="font-bold text-[11px]">{m.label}</div>
                      <div className="text-[10px] text-slate-500 leading-tight mt-0.5">{m.desc}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Row 4: Interests */}
          <div className="pt-2 border-t border-slate-100">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
              Primary Interests & Exploration Themes
            </label>
            <div className="flex flex-wrap gap-2">
              {INTEREST_OPTIONS.map((interest) => {
                const selected = (formData.interests || []).includes(interest);
                return (
                  <button
                    type="button"
                    key={interest}
                    onClick={() => toggleInterest(interest)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1.5 ${
                      selected
                        ? 'bg-teal-50 border border-teal-300 text-teal-800 font-semibold'
                        : 'bg-slate-50 border border-slate-200 text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    {selected && <Check className="w-3 h-3 text-teal-600" />}
                    {interest}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Action Button */}
          <div className="pt-4 flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white font-bold text-sm shadow-lg shadow-teal-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Synthesizing AI Itinerary...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Generate Personalized Itinerary</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
