import React, { useState, useEffect } from 'react';
import { rideAPI } from '../../api';
import { Search, MapPin, Calendar, Sparkles, Navigation, Filter, ArrowRight, Zap, RefreshCw } from 'lucide-react';
import ChennaiCommuteMap from '../Map/ChennaiCommuteMap';
import LocationAutocomplete from '../Map/LocationAutocomplete';
import RideCard from './RideCard';
import JoinRequestModal from './JoinRequestModal';
import LiveRideTracker from '../Map/LiveRideTracker';

export default function RideSearch({
  currentUser,
  onOpenAuth,
  onOpenPostRide
}) {
  const [searchParams, setSearchParams] = useState({
    from_location: 'Vadapalani',
    to_location: 'Olympia Tech Park',
    travel_date: new Date().toISOString().split('T')[0],
  });

  const [availableRides, setAvailableRides] = useState([]);
  const [selectedRide, setSelectedRide] = useState(null);
  const [searchRoutePreview, setSearchRoutePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchMessage, setSearchMessage] = useState('');
  
  // Modals
  const [activeJoinRide, setActiveJoinRide] = useState(null);
  const [trackingRide, setTrackingRide] = useState(null);

  // Popular Chennai Commute Corridors
  const POPULAR_CORRIDORS = [
    { title: 'Inner Ring / 100ft Rd', from: 'Maduravoyal', to: 'Olympia Tech Park' },
    { title: 'OMR Tech Corridor', from: 'Tambaram', to: 'Tidel Park' },
    { title: 'Porur IT Corridor', from: 'Porur', to: 'DLF IT Park' },
    { title: 'GST Road Corridor', from: 'Perungalathur', to: 'Guindy' },
  ];

  useEffect(() => {
    handleSearch();
  }, []);

  const handleSearch = async (customParams = null) => {
    const params = customParams || searchParams;
    setLoading(true);
    try {
      // 1. Fetch available matching rides
      const res = await rideAPI.searchRides(params);
      if (res.data && res.data.success) {
        setAvailableRides(res.data.rides || []);
        setSearchMessage(res.data.message || '');
        if (res.data.rides && res.data.rides.length > 0) {
          setSelectedRide(res.data.rides[0]);
        }
      }

      // 2. Fetch road route preview for the searched pair
      if (params.from_location && params.to_location) {
        fetchRoutePreview(params.from_location, params.to_location);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoutePreview = async (fromLoc, toLoc) => {
    if (!fromLoc || !toLoc) return;
    try {
      const previewRes = await rideAPI.getRoutePreview({
        from_location: fromLoc,
        to_location: toLoc
      });
      if (previewRes.data && previewRes.data.success) {
        setSearchRoutePreview(previewRes.data);
      }
    } catch (err) {
      console.error('Route preview error:', err);
    }
  };

  const handleCorridorClick = (corridor) => {
    const updated = {
      ...searchParams,
      from_location: corridor.from,
      to_location: corridor.to,
    };
    setSearchParams(updated);
    handleSearch(updated);
  };

  const handleRequestJoin = (ride) => {
    if (!currentUser) {
      onOpenAuth();
      return;
    }
    setActiveJoinRide(ride);
  };

  const handleStartTracking = (ride) => {
    setTrackingRide(ride);
  };

  // Active route coordinates for map
  const activeCoordinates = selectedRide?.coordinates || 
    selectedRide?.route_coordinates || 
    searchRoutePreview?.coordinates || 
    [];

  const fromCoords = searchRoutePreview?.from_coords || 
    (selectedRide && { lat: 13.0500, lng: 80.2121, name: searchParams.from_location });
    
  const toCoords = searchRoutePreview?.to_coords || 
    (selectedRide && { lat: 13.0135, lng: 80.2030, name: searchParams.to_location });

  return (
    <div className="space-y-6 pb-12">
      
      {/* Hero Header Section */}
      <div className="relative rounded-3xl p-6 sm:p-8 overflow-hidden border border-slate-800/80 bg-gradient-to-r from-slate-900/90 via-slate-900/70 to-emerald-950/40 backdrop-blur-xl shadow-2xl">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> AI & Road Corridor Commute Matcher
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight font-outfit">
            Share Daily Bike Rides Across <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">Chennai Corridors</span>
          </h1>
          <p className="text-sm text-slate-300">
            Connect with verified office commuters along OMR, GST Road, 100ft Road & Tech Parks. Save fuel costs & reduce traffic.
          </p>
        </div>
      </div>

      {/* Search Bar & Filters Card */}
      <div className="glass-panel rounded-3xl p-5 sm:p-6 border border-slate-800 shadow-xl space-y-4 relative z-[200]">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSearch(); }}
          className="grid grid-cols-1 sm:grid-cols-12 gap-3"
        >
          {/* From Location */}
          <div className="sm:col-span-4 relative z-[210]">
            <LocationAutocomplete
              label="Pickup Location"
              iconType="start"
              required={true}
              value={searchParams.from_location}
              onChange={(val) => setSearchParams((prev) => ({ ...prev, from_location: val }))}
              onSelect={(loc) => {
                const updated = { ...searchParams, from_location: loc.name };
                setSearchParams(updated);
                fetchRoutePreview(loc.name, searchParams.to_location);
                handleSearch(updated);
              }}
              placeholder="e.g. Maduravoyal, Vadapalani, Porur, 600095"
            />
          </div>

          {/* To Location */}
          <div className="sm:col-span-4 relative z-[210]">
            <LocationAutocomplete
              label="Drop / Tech Park"
              iconType="destination"
              required={true}
              value={searchParams.to_location}
              onChange={(val) => setSearchParams((prev) => ({ ...prev, to_location: val }))}
              onSelect={(loc) => {
                const updated = { ...searchParams, to_location: loc.name };
                setSearchParams(updated);
                fetchRoutePreview(searchParams.from_location, loc.name);
                handleSearch(updated);
              }}
              placeholder="e.g. Olympia Tech Park, ELCOT SEZ, Tidel Park"
            />
          </div>

          {/* Date Picker */}
          <div className="sm:col-span-2 relative z-10">
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 h-5 mb-2 flex items-center gap-1.5 truncate">
              <Calendar className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span className="truncate">Travel Date</span>
            </label>
            <input
              type="date"
              value={searchParams.travel_date}
              onChange={(e) => setSearchParams({ ...searchParams, travel_date: e.target.value })}
              className="h-11 w-full bg-slate-900/90 border border-slate-700/80 hover:border-slate-600 focus:border-emerald-500 text-white text-xs rounded-xl px-3 focus:outline-none transition-all shadow-inner"
            />
          </div>

          {/* Search Button */}
          <div className="sm:col-span-2 relative z-10">
            <div className="h-5 mb-2 hidden sm:block"></div>
            <button
              type="submit"
              disabled={loading}
              className="h-11 w-full bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              <span>Find Rides</span>
            </button>
          </div>
        </form>

        {/* Quick Tech Park Hubs, Pink Rides & Corridor Filters */}
        <div className="space-y-2 pt-2 border-t border-slate-800">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1 mr-1">
              🏢 Tech Park Hubs:
            </span>
            {[
              { title: 'DLF Cybercity', from: 'Porur', to: 'DLF IT Park' },
              { title: 'Olympia Tech Park', from: 'Maduravoyal', to: 'Olympia Tech Park' },
              { title: 'Tidel & Ramanujan', from: 'Tambaram', to: 'Tidel Park' },
              { title: 'ELCOT SEZ (OMR)', from: 'Medavakkam', to: 'ELCOT SEZ Sholinganallur' },
              { title: 'Siruseri SIPCOT', from: 'Velachery', to: 'Siruseri SIPCOT' },
              { title: 'One IndiaBulls (Ambattur)', from: 'Anna Nagar', to: 'Ambattur IT Park' },
            ].map((hub, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleCorridorClick(hub)}
                className="px-2.5 py-1 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 hover:text-white text-[11px] font-medium transition-all"
              >
                {hub.title}
              </button>
            ))}

            {/* Pink Ride Toggle Button */}
            <button
              type="button"
              onClick={() => {
                const newVal = !searchParams.is_pink_ride;
                const updated = { ...searchParams, is_pink_ride: newVal };
                setSearchParams(updated);
                fetchRides(updated);
              }}
              className={`px-3 py-1 rounded-xl border text-[11px] font-bold transition-all flex items-center gap-1 ml-auto ${
                searchParams.is_pink_ride
                  ? 'bg-pink-500/30 border-pink-500 text-pink-200 shadow-sm'
                  : 'bg-pink-950/20 border-pink-500/30 text-pink-300 hover:bg-pink-900/30'
              }`}
            >
              <span>🌸 Pink Rides (Women Only)</span>
              {searchParams.is_pink_ride && <span>✓ Active</span>}
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] font-bold text-slate-400 flex items-center gap-1 mr-1">
              🛣️ Road Corridors:
            </span>
            {POPULAR_CORRIDORS.map((c, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleCorridorClick(c)}
                className="px-2.5 py-1 rounded-xl bg-slate-800/90 hover:bg-slate-700 border border-slate-700/60 text-slate-300 hover:text-white text-[11px] font-medium transition-colors"
              >
                {c.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Split Grid: Rides List + Interactive Live Leaflet Map */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-0 isolate">
        
        {/* Left Column: Ride Cards */}
        <div className="lg:col-span-6 space-y-4">
          <div className="flex items-center justify-between px-1">
            <h3 className="text-base font-bold text-white font-outfit flex items-center gap-2">
              <span>Available Commute Rides</span>
              <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-0.5 rounded-full font-mono font-bold">
                {availableRides.length}
              </span>
            </h3>
            {searchRoutePreview && (
              <span className="text-xs text-slate-400">
                Route: ~<strong className="text-emerald-400">{searchRoutePreview.distance_km} km</strong> ({searchRoutePreview.duration_minutes} mins)
              </span>
            )}
          </div>

          {searchMessage && (
            <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300">
              💡 {searchMessage}
            </div>
          )}

          {availableRides.length === 0 && !loading ? (
            <div className="p-10 rounded-3xl glass-panel text-center space-y-3 border border-slate-800">
              <div className="w-12 h-12 rounded-2xl bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
                <Navigation className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-white">No Direct Rides Found</h4>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Try searching nearby corridors like "Vadapalani", "Tambaram", or "Porur", or be the first to offer a ride!
              </p>
              <button
                onClick={() => {
                  if (!currentUser) onOpenAuth();
                  else onOpenPostRide();
                }}
                className="mt-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-md transition-all"
              >
                Offer a Ride on this Route
              </button>
            </div>
          ) : (
            availableRides.map((ride) => (
              <RideCard
                key={ride.id}
                ride={ride}
                isSelected={selectedRide?.id === ride.id}
                onSelect={() => setSelectedRide(ride)}
                onRequestJoin={handleRequestJoin}
                onStartTracking={handleStartTracking}
              />
            ))
          )}
        </div>

        {/* Right Column: Live Interactive Chennai Leaflet Map */}
        <div className="lg:col-span-6 space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Navigation className="w-3.5 h-3.5 text-emerald-400" /> Interactive Route Map
            </span>
            <span className="text-[11px] text-slate-400">Click any marker or card to view road details</span>
          </div>

          <ChennaiCommuteMap
            fromCoords={fromCoords}
            toCoords={toCoords}
            pickupCoords={selectedRide?.ai_pickup_suggestion ? { lat: 13.0500, lng: 80.2121, name: selectedRide.ai_pickup_suggestion } : null}
            routeCoordinates={activeCoordinates}
            availableRides={availableRides}
            onSelectRide={(ride) => setSelectedRide(ride)}
            height="520px"
          />

          {/* Quick Route Highlights Card */}
          {selectedRide && (
            <div className="p-4 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between text-xs">
              <div>
                <span className="text-slate-400 block text-[11px]">Selected Rider Route</span>
                <span className="font-bold text-white">{selectedRide.from_location} ➔ {selectedRide.to_location}</span>
              </div>
              <div className="text-right">
                <span className="text-slate-400 block text-[11px]">AI Route Match</span>
                <span className="text-emerald-400 font-bold font-mono text-sm">{selectedRide.ai_match_score || 85}% Compatible</span>
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Booking Request Modal */}
      {activeJoinRide && (
        <JoinRequestModal
          ride={activeJoinRide}
          currentUser={currentUser}
          isOpen={!!activeJoinRide}
          onClose={() => setActiveJoinRide(null)}
          onRequestSuccess={() => {
            handleSearch();
          }}
        />
      )}

      {/* Live Route Tracking Simulator Modal */}
      {trackingRide && (
        <LiveRideTracker
          ride={trackingRide}
          onClose={() => setTrackingRide(null)}
        />
      )}

    </div>
  );
}
