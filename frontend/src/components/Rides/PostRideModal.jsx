import React, { useState, useEffect } from 'react';
import { rideAPI, bikeAPI } from '../../api';
import confetti from 'canvas-confetti';
import { MapPin, Clock, Calendar, Bike, IndianRupee, Sparkles, CheckCircle2, AlertCircle, Plus } from 'lucide-react';
import ChennaiCommuteMap from '../Map/ChennaiCommuteMap';
import LocationAutocomplete from '../Map/LocationAutocomplete';

export default function PostRideModal({
  isOpen,
  onClose,
  currentUser,
  onRidePosted
}) {
  const [formData, setFormData] = useState({
    from_location: 'Maduravoyal',
    to_location: 'Olympia Tech Park',
    departure_date: new Date(Date.now() + 86400000).toISOString().split('T')[0], // Tomorrow
    departure_time: '08:30',
    available_seats: 1,
    description: 'Daily office commute. Helmet provided.',
    is_recurring: false,
    recurring_days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
  });

  const [routePreview, setRoutePreview] = useState(null);
  const [userBikes, setUserBikes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [calculatingRoute, setCalculatingRoute] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchUserBikes();
      fetchPreview(formData.from_location, formData.to_location, formData.departure_time);
    }
  }, [isOpen]);

  const fetchUserBikes = async () => {
    try {
      const res = await bikeAPI.getMyBikes();
      if (res.data && res.data.bikes) {
        setUserBikes(res.data.bikes);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchPreview = async (from, to, time) => {
    if (!from || !to) return;
    setCalculatingRoute(true);
    try {
      const res = await rideAPI.getRoutePreview({
        from_location: from,
        to_location: to,
        departure_time: time
      });
      if (res.data && res.data.success) {
        setRoutePreview(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setCalculatingRoute(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newVal = type === 'checkbox' ? checked : value;
    const updated = { ...formData, [name]: newVal };
    setFormData(updated);
    setError('');

    if (name === 'from_location' || name === 'to_location' || name === 'departure_time') {
      fetchPreview(updated.from_location, updated.to_location, updated.departure_time);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = {
        from_location: formData.from_location,
        to_location: formData.to_location,
        departure_date: formData.departure_date,
        departure_time: formData.departure_time,
        available_seats: parseInt(formData.available_seats),
        description: formData.description,
        is_recurring: formData.is_recurring,
        recurring_days: formData.is_recurring ? formData.recurring_days : []
      };

      const res = await rideAPI.postRide(payload);
      if (res.data && res.data.success) {
        setSuccess(true);
        confetti({
          particleCount: 100,
          spread: 80,
          origin: { y: 0.6 }
        });
        setTimeout(() => {
          if (onRidePosted) onRidePosted(res.data.ride);
          onClose();
        }, 1800);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || err.response?.data?.message || 'Failed to post ride offer.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="glass-modal w-full max-w-2xl rounded-3xl overflow-hidden shadow-2xl border border-slate-700 my-8">
        
        {/* Modal Header */}
        <div className="p-6 pb-4 border-b border-slate-800 bg-slate-900/60 relative flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white font-outfit flex items-center gap-2">
              <span>Offer a Bike Ride</span>
              <span className="text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/30">
                Chennai Commute
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Share your daily bike ride & split fuel costs with co-workers</p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center font-bold text-sm"
          >
            ✕
          </button>
        </div>

        {success ? (
          <div className="p-10 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/30">
              <CheckCircle2 className="w-8 h-8 animate-bounce" />
            </div>
            <h4 className="text-2xl font-bold text-white font-outfit">Ride Posted Successfully!</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Your ride is now active on the Chennai commuter grid. Co-commuters along your road corridor will be able to search and request seats.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Active Bike Widget & Verification Status */}
            {(() => {
              const verifiedBikes = userBikes.filter((b) => b.is_verified);
              const activeBike = userBikes.find((b) => b.is_active) || (verifiedBikes.length === 1 ? verifiedBikes[0] : null);

              if (!currentUser?.license_verified || verifiedBikes.length === 0) {
                return (
                  <div className="p-3.5 rounded-2xl bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs space-y-1">
                    <div className="font-bold flex items-center gap-1.5 text-amber-200">
                      <AlertCircle className="w-4 h-4 text-amber-400" />
                      <span>Ride Offering Requires Active & Verified Vehicle</span>
                    </div>
                    <p className="text-[11px] text-amber-300/80">
                      To offer rides in Chennai, you must have an Admin-approved Driving License (DL) and at least one active verified two-wheeler. Please check your status in the <strong>Vehicles & DL</strong> section.
                    </p>
                  </div>
                );
              }

              if (verifiedBikes.length > 1) {
                return (
                  <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-700 space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                        <Bike className="w-4 h-4 text-emerald-400" />
                        <span>Select Active Bike for this Commute:</span>
                      </label>
                      <span className="text-[10px] text-emerald-400 font-mono font-bold">
                        1 Active Vehicle Only
                      </span>
                    </div>
                    <select
                      value={activeBike?.id || ''}
                      onChange={async (e) => {
                        const bikeId = parseInt(e.target.value);
                        try {
                          await bikeAPI.setActiveBike(bikeId);
                          fetchUserBikes();
                        } catch (err) {
                          console.error(err);
                        }
                      }}
                      className="w-full bg-slate-950 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                    >
                      {verifiedBikes.map((b) => (
                        <option key={b.id} value={b.id}>
                          {b.brand} {b.model} ({b.bike_number}) {b.is_active ? '⭐ [Active Vehicle]' : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                );
              }

              if (activeBike) {
                return (
                  <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <Bike className="w-4 h-4 text-emerald-400" />
                      <span className="text-slate-300">
                        Active Ride Vehicle: <strong className="text-white">{activeBike.brand} {activeBike.model}</strong> ({activeBike.bike_number})
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 text-[10px] font-bold border border-emerald-500/30">
                      ✓ Active Vehicle
                    </span>
                  </div>
                );
              }

              return null;
            })()}

            {error && (
              <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* From / To Locations */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 relative z-[300]">
              <div className="relative z-[310]">
                <LocationAutocomplete
                  label="Start / Pickup Location"
                  iconType="start"
                  required={true}
                  value={formData.from_location}
                  onChange={(val) => {
                    setFormData((prev) => ({ ...prev, from_location: val }));
                    fetchPreview(val, formData.to_location, formData.departure_time);
                  }}
                  onSelect={(loc) => {
                    setFormData((prev) => ({ ...prev, from_location: loc.name }));
                    fetchPreview(loc.name, formData.to_location, formData.departure_time);
                  }}
                  placeholder="e.g. Maduravoyal, Vadapalani, 600095"
                />
              </div>

              <div className="relative z-[310]">
                <LocationAutocomplete
                  label="Destination / Office / Tech Park"
                  iconType="destination"
                  required={true}
                  value={formData.to_location}
                  onChange={(val) => {
                    setFormData((prev) => ({ ...prev, to_location: val }));
                    fetchPreview(formData.from_location, val, formData.departure_time);
                  }}
                  onSelect={(loc) => {
                    setFormData((prev) => ({ ...prev, to_location: loc.name }));
                    fetchPreview(formData.from_location, loc.name, formData.departure_time);
                  }}
                  placeholder="e.g. Olympia Tech Park, ELCOT SEZ, Tidel Park"
                />
              </div>
            </div>

            {/* Live Route Preview Map Widget */}
            {routePreview && (
              <div className="rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 p-2 space-y-2 relative z-0 isolate">
                <ChennaiCommuteMap
                  fromCoords={routePreview.from_coords}
                  toCoords={routePreview.to_coords}
                  routeCoordinates={routePreview.coordinates}
                  height="180px"
                />
                <div className="flex items-center justify-between px-2 py-1 text-xs">
                  <div className="flex items-center gap-3">
                    <span className="text-slate-400">Road Distance: <strong className="text-white">{routePreview.distance_km} km</strong></span>
                    <span className="text-slate-400">Est. Time: <strong className="text-white">{routePreview.duration_minutes} mins</strong></span>
                  </div>
                  {routePreview.fare && (
                    <div className="text-emerald-400 font-bold font-mono">
                      Suggested Fare: ₹{routePreview.fare.final_fare}
                      {routePreview.fare.is_peak_time && (
                        <span className="ml-1.5 text-[10px] text-amber-400 font-sans font-semibold">(Peak Hour)</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Date, Time & Seats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-cyan-400" /> Date
                </label>
                <input
                  type="date"
                  name="departure_date"
                  required
                  value={formData.departure_date}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl px-3 py-2.5 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-amber-400" /> Departure Time
                </label>
                <input
                  type="time"
                  name="departure_time"
                  required
                  value={formData.departure_time}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl px-3 py-2.5 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Available Seats</label>
                <select
                  name="available_seats"
                  value={formData.available_seats}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl px-3 py-2.5 focus:border-emerald-500 focus:outline-none"
                >
                  <option value={1}>1 Passenger (Recommended)</option>
                  <option value={2}>2 Passengers</option>
                </select>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Commute Details / Pickup Route Note</label>
              <textarea
                rows={2}
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="e.g. Traveling via Koyambedu & Vadapalani. Clean ISI helmet provided."
                className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
              />
            </div>

            {/* Recurring & Safety Helmet Checkboxes */}
            <div className="space-y-2 pt-1 border-t border-slate-800/80">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_recurring"
                  name="is_recurring"
                  checked={formData.is_recurring}
                  onChange={handleChange}
                  className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 bg-slate-900 border-slate-700"
                />
                <label htmlFor="is_recurring" className="text-xs font-semibold text-slate-300 cursor-pointer">
                  Recurring Daily Commute (Monday to Friday office pool)
                </label>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="helmet_check"
                  required
                  defaultChecked
                  className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 bg-slate-900 border-slate-700"
                />
                <label htmlFor="helmet_check" className="text-xs font-semibold text-emerald-300 cursor-pointer">
                  ⛑️ I confirm I will carry a clean ISI safety helmet for the passenger.
                </label>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 px-4 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              {loading ? 'Posting Ride...' : 'Publish Commute Offer'}
            </button>
          </form>
        )}

      </div>
    </div>
  );
}
