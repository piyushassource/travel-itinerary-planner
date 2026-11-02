import React from 'react';
import { DollarSign, Users, ShieldCheck, Printer, CheckCircle2 } from 'lucide-react';

export default function CostSummary({ itinerary }) {
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      {/* Budget Breakdown Card */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm">
        <h3 className="font-extrabold text-slate-900 text-base mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-emerald-600" />
          Financial & Budget Overview
        </h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-100">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Est. Total Trip Cost
            </span>
            <span className="font-extrabold text-lg text-slate-900">
              ${itinerary.estimated_total_cost_usd}
            </span>
          </div>

          <div className="flex items-center justify-between p-3.5 rounded-2xl bg-teal-50/70 border border-teal-100">
            <div>
              <span className="text-xs font-semibold text-teal-800 uppercase tracking-wider block">
                Cost Per Person
              </span>
              <span className="text-[11px] text-teal-600">
                {itinerary.party_size} traveler{itinerary.party_size > 1 ? 's' : ''} ({itinerary.party_type})
              </span>
            </div>
            <span className="font-extrabold text-lg text-teal-900">
              ${itinerary.cost_per_person_usd}
            </span>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-400">Excludes flights & major lodging</span>
          <button
            onClick={handlePrint}
            className="px-3.5 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-xs font-bold text-slate-700 flex items-center gap-1.5 transition-colors"
          >
            <Printer className="w-3.5 h-3.5 text-slate-500" />
            Print Itinerary
          </button>
        </div>
      </div>

      {/* Logistics & Transit Tips */}
      {itinerary.packing_and_logistics_tips && itinerary.packing_and_logistics_tips.length > 0 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm">
          <h3 className="font-extrabold text-slate-900 text-base mb-4 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-teal-600" />
            AI Logistics & Transit Intel
          </h3>

          <ul className="space-y-3">
            {itinerary.packing_and_logistics_tips.map((tip, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-600 leading-relaxed">
                <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
