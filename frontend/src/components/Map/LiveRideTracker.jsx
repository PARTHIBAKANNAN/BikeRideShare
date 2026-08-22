import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Navigation, Phone, MessageSquare, ShieldCheck, Zap } from 'lucide-react';
import ChennaiCommuteMap from './ChennaiCommuteMap';

export default function LiveRideTracker({ ride, onClose }) {
  const [progress, setProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [currentCoordIndex, setCurrentCoordIndex] = useState(0);
  const [speedKmh, setSpeedKmh] = useState(36);
  
  const coordinates = ride?.coordinates || ride?.route_coordinates || [];
  const totalPoints = coordinates.length;
  
  useEffect(() => {
    if (!isPlaying || totalPoints < 2) return;
    
    const interval = setInterval(() => {
      setCurrentCoordIndex((prev) => {
        if (prev >= totalPoints - 1) {
          setIsPlaying(false);
          return totalPoints - 1;
        }
        const next = prev + 1;
        setProgress(Math.round((next / (totalPoints - 1)) * 100));
        // Add subtle speed variation
        setSpeedKmh(Math.floor(32 + Math.random() * 12));
        return next;
      });
    }, 350); // Frame step
    
    return () => clearInterval(interval);
  }, [isPlaying, totalPoints]);
  
  const currentPos = coordinates[currentCoordIndex] ? {
    lat: coordinates[currentCoordIndex][0],
    lng: coordinates[currentCoordIndex][1]
  } : null;
  
  const fromCoords = coordinates[0] ? { lat: coordinates[0][0], lng: coordinates[0][1], name: ride.from_location } : null;
  const toCoords = coordinates[totalPoints - 1] ? { lat: coordinates[totalPoints - 1][0], lng: coordinates[totalPoints - 1][1], name: ride.to_location } : null;
  
  const handleRestart = () => {
    setCurrentCoordIndex(0);
    setProgress(0);
    setIsPlaying(true);
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-modal w-full max-w-4xl rounded-3xl overflow-hidden shadow-2xl border border-slate-700">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30 shadow-inner">
              <Navigation className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-white font-outfit">Live Commute Tracker</h3>
                <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-0.5 rounded-full font-semibold flex items-center gap-1 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Live
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {ride.from_location} ➔ {ride.to_location} • {ride.distance_km || 12} km
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition-colors text-sm font-bold"
          >
            ✕
          </button>
        </div>

        {/* Interactive Map with Animated Position */}
        <div className="p-4 bg-slate-950/50">
          <ChennaiCommuteMap
            fromCoords={fromCoords}
            toCoords={toCoords}
            pickupCoords={currentPos ? { ...currentPos, name: 'Live Rider Position' } : null}
            routeCoordinates={coordinates}
            height="360px"
          />
        </div>

        {/* Telemetry & Controls Dashboard */}
        <div className="p-5 bg-slate-900/90 border-t border-slate-800 space-y-4">
          
          {/* Progress & Speed */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Commute Progress</span>
              <div className="text-xl font-bold text-emerald-400 font-mono mt-0.5">{progress}%</div>
            </div>
            
            <div className="bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Current Speed</span>
              <div className="text-xl font-bold text-cyan-400 font-mono mt-0.5 flex items-center gap-1">
                {isPlaying ? speedKmh : 0} <span className="text-xs font-normal text-slate-400">km/h</span>
              </div>
            </div>

            <div className="bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Est. Arrival</span>
              <div className="text-xl font-bold text-amber-400 font-mono mt-0.5">
                {Math.max(1, Math.round((100 - progress) * (ride.duration_minutes || 25) / 100))} <span className="text-xs font-normal text-slate-400">mins left</span>
              </div>
            </div>

            <div className="bg-slate-800/60 p-3 rounded-2xl border border-slate-700/50">
              <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Bike Details</span>
              <div className="text-xs font-semibold text-slate-200 mt-1 truncate">
                {ride.bike_brand || (ride.bike && ride.bike.brand) || 'Royal Enfield'} {ride.bike_model || (ride.bike && ride.bike.model) || 'Hunter 350'}
              </div>
              <div className="text-[10px] text-slate-400 font-mono">
                {ride.bike_number || (ride.bike && ride.bike.bike_number) || 'TN 09 BX 4521'}
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
            <div 
              className="bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-500 h-full rounded-full transition-all duration-300 shadow-lg shadow-emerald-500/50"
              style={{ width: `${progress}%` }}
            ></div>
          </div>

          {/* Rider Contact Card & Simulation Action Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            
            {/* Rider Profile Card */}
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <div className="w-10 h-10 rounded-full bg-emerald-600 font-bold flex items-center justify-center text-white text-sm shadow-md">
                {(ride.rider_name || (ride.rider && ride.rider.name) || 'K')[0]}
              </div>
              <div>
                <div className="text-sm font-semibold text-white flex items-center gap-1.5">
                  {ride.rider_name || (ride.rider && ride.rider.name) || 'Karthik Raja'}
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-xs text-slate-400">
                  ⭐ {ride.rider_rating || (ride.rider && ride.rider.rating) || 4.9} • Verified Commuter
                </div>
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition-colors"
              >
                {isPlaying ? <Pause className="w-4 h-4 text-amber-400" /> : <Play className="w-4 h-4 text-emerald-400" />}
                {isPlaying ? 'Pause' : 'Resume'}
              </button>

              <button
                onClick={handleRestart}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                title="Restart simulation"
              >
                <RotateCcw className="w-4 h-4" />
              </button>

              <a
                href={`tel:${ride.rider_phone || (ride.rider && ride.rider.phone) || '+919840112233'}`}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-600/30 transition-all"
              >
                <Phone className="w-4 h-4" /> Call Rider
              </a>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}
