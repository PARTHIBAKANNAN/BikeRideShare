import React, { useState, useEffect, useRef } from 'react';
import { rideAPI } from '../../api';
import {
  MapPin,
  Building,
  Train,
  Crosshair,
  Search,
  X,
  Clock,
  Sparkles,
  Navigation,
  Check
} from 'lucide-react';

export default function LocationAutocomplete({
  value = '',
  onChange,
  onSelect,
  placeholder = 'Search street, building, landmark or pincode...',
  label = 'Location',
  iconType = 'start', // 'start' | 'destination' | 'tech_park'
  required = false
}) {
  const [query, setQuery] = useState(value);
  const [suggestions, setSuggestions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [locatingUser, setLocatingUser] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    setQuery(value);
  }, [value]);

  // Click outside listener
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced live search
  useEffect(() => {
    if (!isOpen) return;
    
    const handler = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await rideAPI.getChennaiLocations(query || '');
        if (res.data && res.data.locations) {
          setSuggestions(res.data.locations);
        }
      } catch (err) {
        console.error('Location search failed:', err);
      } finally {
        setLoading(false);
      }
    }, 180);

    return () => clearTimeout(handler);
  }, [query, isOpen]);

  const handleInputChange = (e) => {
    const text = e.target.value;
    setQuery(text);
    if (onChange) onChange(text);
    setIsOpen(true);
  };

  const handleSelectLocation = (loc) => {
    const displayName = loc.name;
    setQuery(displayName);
    setIsOpen(false);
    if (onChange) onChange(displayName);
    if (onSelect) onSelect(loc);
  };

  // GPS Current Location Detection (Browser Geolocation)
  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }

    setLocatingUser(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        
        try {
          // Reverse geocode via robust backend service (with OSM + Chennai Hubs fallback)
          const res = await rideAPI.reverseGeocode(lat, lng);
          if (res.data && res.data.success) {
            const locObj = {
              name: res.data.name,
              address: res.data.address,
              pincode: res.data.pincode,
              lat: res.data.lat,
              lng: res.data.lng,
              area: res.data.area,
              type: 'gps'
            };
            handleSelectLocation(locObj);
            setLocatingUser(false);
            return;
          }
        } catch (e) {
          console.error('Reverse geocode failed:', e);
        }

        // Exact Coordinate Fallback
        handleSelectLocation({
          name: `Chennai (${lat.toFixed(4)}, ${lng.toFixed(4)})`,
          address: `GPS Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`,
          lat: lat,
          lng: lng,
          type: 'gps'
        });
        setLocatingUser(false);
      },
      (error) => {
        console.error(error);
        alert('Could not access device GPS. Please grant browser location permissions or type your area.');
        setLocatingUser(false);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  const getIcon = (type) => {
    if (type === 'it_park') return <Building className="w-4 h-4 text-cyan-400" />;
    if (type === 'transit') return <Train className="w-4 h-4 text-purple-400" />;
    if (type === 'gps') return <Crosshair className="w-4 h-4 text-emerald-400 animate-pulse" />;
    return <MapPin className="w-4 h-4 text-emerald-400" />;
  };

  return (
    <div className="relative w-full" ref={dropdownRef}>
      {label && (
        <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-400 h-5 mb-2 flex items-center justify-between truncate">
          <span className="flex items-center gap-1.5 truncate">
            {iconType === 'start' ? (
              <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            ) : iconType === 'destination' ? (
              <MapPin className="w-3.5 h-3.5 text-rose-400 shrink-0" />
            ) : (
              <Building className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            )}
            <span className="truncate">{label}</span>
          </span>
        </label>
      )}

      {/* Input Box */}
      <div className="relative">
        <input
          type="text"
          required={required}
          value={query}
          onFocus={() => setIsOpen(true)}
          onChange={handleInputChange}
          placeholder={placeholder}
          className="h-11 w-full bg-slate-900/90 border border-slate-700/80 hover:border-slate-600 focus:border-emerald-500 text-white text-xs rounded-xl px-3.5 pr-16 focus:outline-none transition-all placeholder:text-slate-500 shadow-inner"
        />

        <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                if (onChange) onChange('');
              }}
              className="p-1 text-slate-400 hover:text-white rounded-md transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}

          <button
            type="button"
            title="Detect GPS Current Location"
            onClick={handleUseCurrentLocation}
            disabled={locatingUser}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-emerald-500/20 text-emerald-400 hover:text-emerald-300 border border-slate-700/60 transition-all disabled:opacity-50"
          >
            <Crosshair className={`w-3.5 h-3.5 ${locatingUser ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Rapido / Zomato Style Suggestions Dropdown */}
      {isOpen && (
        <div className="absolute left-0 right-0 top-full mt-2 z-[9999] rounded-2xl bg-slate-900/98 backdrop-blur-2xl border border-slate-700 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 max-h-80 overflow-y-auto ring-1 ring-white/10">
          
          {/* GPS Location Option */}
          <button
            type="button"
            onClick={handleUseCurrentLocation}
            className="w-full p-3 text-left hover:bg-emerald-500/15 border-b border-slate-800 flex items-center gap-3 transition-colors text-xs text-emerald-300 font-bold group"
          >
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform">
              <Crosshair className="w-4 h-4" />
            </div>
            <div>
              <div className="font-extrabold flex items-center gap-1.5">
                <span>Use Current GPS Location</span>
                <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.2 rounded font-mono">GPS</span>
              </div>
              <div className="text-[11px] text-slate-400 font-normal">Detect current street & building in Chennai</div>
            </div>
          </button>

          {/* Loading Indicator */}
          {loading && (
            <div className="p-3 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
              <div className="w-3.5 h-3.5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
              <span>Searching Chennai roads, SEZs & pincodes...</span>
            </div>
          )}

          {/* List of Suggestions */}
          {!loading && suggestions.length === 0 && query && (
            <div className="p-4 text-center text-xs text-slate-400 space-y-1">
              <p>No exact match found for "{query}".</p>
              <p className="text-[11px] text-slate-500">We'll use live geocoding when you search or post.</p>
            </div>
          )}

          {!loading &&
            suggestions.map((loc, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectLocation(loc)}
                className="w-full p-3 text-left hover:bg-slate-800/80 border-b border-slate-800/50 flex items-start gap-3 transition-all text-xs group"
              >
                <div className="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0 mt-0.5 group-hover:border-emerald-500/40 transition-colors">
                  {getIcon(loc.type)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold text-white group-hover:text-emerald-400 transition-colors truncate">
                      {loc.name}
                    </span>
                    {loc.pincode && (
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px] shrink-0 border border-slate-700">
                        PIN: {loc.pincode}
                      </span>
                    )}
                  </div>

                  <div className="text-[11px] text-slate-400 truncate mt-0.5">
                    {loc.address || `${loc.area}, Chennai`}
                  </div>
                </div>
              </button>
            ))}

        </div>
      )}
    </div>
  );
}
