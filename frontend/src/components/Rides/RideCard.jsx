import React from 'react';
import { Bike, ShieldCheck, Clock, Navigation, Sparkles, MapPin, IndianRupee, ArrowRight, UserCheck } from 'lucide-react';

export default function RideCard({
  ride,
  onSelect,
  onRequestJoin,
  onStartTracking,
  isSelected = false
}) {
  const matchScore = ride.ai_match_score ?? 85;
  const isHighMatch = matchScore >= 80;
  
  const riderName = ride.rider_name || (ride.rider && ride.rider.name) || 'Karthik Raja';
  const riderRating = ride.rider_rating || (ride.rider && ride.rider.rating) || 4.9;
  const fare = ride.cost_per_person || (ride.booking && ride.booking.cost_per_person) || 50;
  
  const fromLoc = ride.from_location || (ride.route && ride.route.from_location);
  const toLoc = ride.to_location || (ride.route && ride.route.to_location);
  const depTime = ride.departure_time || (ride.timing && ride.timing.departure_time) || '08:30';
  const depDate = ride.departure_date || (ride.timing && ride.timing.departure_date) || 'Today';
  
  const bikeBrand = ride.bike_brand || (ride.bike && ride.bike.brand) || 'Royal Enfield';
  const bikeModel = ride.bike_model || (ride.bike && ride.bike.model) || 'Hunter 350';
  const bikeNumber = ride.bike_number || (ride.bike && ride.bike.bike_number) || 'TN 09 BX 4521';
  const availableSeats = ride.available_seats || (ride.booking && ride.booking.available_seats) || 1;

  return (
    <div
      onClick={onSelect}
      className={`p-5 rounded-3xl transition-all cursor-pointer border ${
        isSelected
          ? 'glass-panel bg-slate-900/90 border-emerald-500/80 shadow-2xl shadow-emerald-500/10 ring-1 ring-emerald-500'
          : 'glass-panel-light hover:bg-slate-900/80 border-slate-800 hover:border-slate-700 shadow-lg'
      }`}
    >
      {/* Top Header: Rider Info & Match Badge */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white font-bold flex items-center justify-center text-sm shadow-md">
            {riderName[0]}
          </div>
          <div>
            <div className="flex items-center gap-1.5 font-bold text-white text-sm">
              <span>{riderName}</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" title="Verified Rider & DL" />
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
              <span className="text-amber-400 font-semibold">⭐ {riderRating}</span>
              <span>•</span>
              <span className="text-slate-300">{bikeBrand} {bikeModel}</span>
            </div>
          </div>
        </div>

        {/* AI Match Badge */}
        <div className="text-right">
          <div className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-bold border shadow-sm ${
            isHighMatch 
              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-emerald-500/10'
              : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
          }`}>
            <Sparkles className="w-3.5 h-3.5" />
            <span>{matchScore}% Match</span>
          </div>
          <div className="text-emerald-400 font-extrabold text-lg mt-1 font-outfit">
            ₹{fare} <span className="text-[10px] font-normal text-slate-400">/ seat</span>
          </div>
        </div>
      </div>

      {/* Route Journey */}
      <div className="my-4 p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-2">
        <div className="flex items-center gap-2.5 text-xs font-semibold text-slate-200">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 ring-4 ring-emerald-500/20"></div>
          <span className="truncate">{fromLoc}</span>
        </div>
        
        <div className="ml-1 pl-3 border-l-2 border-dashed border-slate-700 text-[11px] text-slate-400 flex items-center justify-between py-0.5">
          <span>🕒 Departure: <strong className="text-slate-300">{depTime}</strong> ({depDate})</span>
          <span className="bg-slate-800 px-2 py-0.5 rounded text-[10px] font-mono text-emerald-400 font-semibold">
            {availableSeats} seat available
          </span>
        </div>

        <div className="flex items-center gap-2.5 text-xs font-semibold text-slate-200">
          <div className="w-2.5 h-2.5 rounded-full bg-rose-400 ring-4 ring-rose-500/20"></div>
          <span className="truncate">{toLoc}</span>
        </div>
      </div>

      {/* AI Reasoning / Pickup Advice */}
      {ride.ai_pickup_suggestion && (
        <div className="p-2.5 mb-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/20 text-[11px] space-y-1">
          <div className="flex items-center justify-between text-emerald-400 font-bold">
            <span className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" /> Suggested Boarding:
            </span>
            <span className="text-slate-300 font-normal">
              Detour: <strong className="text-emerald-300">{ride.ai_detour_time || '0 min'}</strong>
            </span>
          </div>
          <p className="text-slate-300 font-medium">{ride.ai_pickup_suggestion}</p>
          {ride.ai_reasoning && (
            <p className="text-slate-400 text-[10px] italic">"{ride.ai_reasoning}"</p>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center gap-2 pt-1">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onStartTracking(ride);
          }}
          className="flex-1 py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 flex items-center justify-center gap-1.5 transition-colors"
        >
          <Navigation className="w-3.5 h-3.5 text-cyan-400" /> Live Route
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onRequestJoin(ride);
          }}
          className="flex-1 py-2 px-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold shadow-md shadow-emerald-600/20 flex items-center justify-center gap-1.5 transition-all"
        >
          <span>Request Ride</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

    </div>
  );
}
