import React from 'react';
import { User, Heart, Users, Sparkles, ArrowRight } from 'lucide-react';

export const SCENARIOS = [
  {
    id: 'solo-weekend',
    badge: 'Scenario 1',
    title: 'Solo Weekend Getaway',
    subtitle: 'Tokyo • 3 Days • High Mobility',
    icon: User,
    color: 'from-blue-500 to-indigo-600',
    borderColor: 'hover:border-blue-300',
    data: {
      destination: 'Tokyo, Japan',
      days: 3,
      party_type: 'solo',
      party_size: 1,
      budget_tier: 'budget',
      pacing: 'fast_paced',
      interests: ['food', 'sightseeing', 'culture'],
      accommodation_area: 'Shinjuku',
      custom_notes: 'Optimize travel routes, suggest vibrant street food and solo-friendly dining.'
    }
  },
  {
    id: 'couple-vacation',
    badge: 'Scenario 2',
    title: 'Romantic Couple Vacation',
    subtitle: 'Paris • 4 Days • Relaxed Pacing',
    icon: Heart,
    color: 'from-rose-500 to-pink-600',
    borderColor: 'hover:border-pink-300',
    data: {
      destination: 'Paris, France',
      days: 4,
      party_type: 'couple',
      party_size: 2,
      budget_tier: 'moderate',
      pacing: 'relaxed',
      interests: ['romance', 'scenic', 'dining', 'art'],
      accommodation_area: 'Saint-Germain-des-Prés',
      custom_notes: 'Scenic viewpoints, romantic sunset spots, intimate bistros, unhurried mornings.'
    }
  },
  {
    id: 'group-coordination',
    badge: 'Scenario 3',
    title: 'Small Group Multi-Day Trip',
    subtitle: 'New York • 5 Days • 4 Friends',
    icon: Users,
    color: 'from-amber-500 to-orange-600',
    borderColor: 'hover:border-amber-300',
    data: {
      destination: 'New York, USA',
      days: 5,
      party_type: 'group',
      party_size: 4,
      budget_tier: 'moderate',
      pacing: 'moderate',
      interests: ['adventure', 'culture', 'nightlife', 'food'],
      accommodation_area: 'Midtown Manhattan',
      custom_notes: 'Coordinated logistics for 4 friends, group-friendly dining, clear meeting points.'
    }
  }
];

export default function ScenarioPresets({ onSelectPreset, isLoading }) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="w-4 h-4 text-teal-600" />
        <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-500">
          Instant Test Scenarios
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {SCENARIOS.map((sc) => {
          const Icon = sc.icon;
          return (
            <button
              key={sc.id}
              disabled={isLoading}
              onClick={() => onSelectPreset(sc.data)}
              className={`text-left p-4 rounded-2xl bg-white border border-slate-200/80 shadow-sm transition-all duration-200 hover:shadow-md ${sc.borderColor} group relative overflow-hidden disabled:opacity-60 disabled:cursor-not-allowed`}
            >
              <div className="flex items-start justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                  {sc.badge}
                </span>
                <div className={`w-8 h-8 rounded-xl bg-gradient-to-tr ${sc.color} flex items-center justify-center text-white shadow-sm`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>

              <div className="mt-3">
                <h3 className="font-bold text-slate-900 group-hover:text-teal-600 transition-colors">
                  {sc.title}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">{sc.subtitle}</p>
              </div>

              <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-teal-700">
                <span>Load & Generate</span>
                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
