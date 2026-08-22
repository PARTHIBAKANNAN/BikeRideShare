import React, { useState } from 'react';
import { rideAPI } from '../../api';
import confetti from 'canvas-confetti';
import { MapPin, MessageSquare, Send, CheckCircle2, ShieldCheck, AlertCircle } from 'lucide-react';

export default function JoinRequestModal({
  ride,
  currentUser,
  isOpen,
  onClose,
  onRequestSuccess
}) {
  const [pickupLocation, setPickupLocation] = useState(ride?.ai_pickup_suggestion || ride?.from_location || '');
  const [message, setMessage] = useState('Hi, I am traveling along your route and would like to join your bike pool!');
  const [seatsNeeded, setSeatsNeeded] = useState(1);
  const [isForFriend, setIsForFriend] = useState(false);
  const [friendName, setFriendName] = useState('');
  const [friendPhone, setFriendPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  if (!isOpen || !ride) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (isForFriend && (!friendName.trim() || !friendPhone.trim())) {
      setError('Please provide your friend\'s name and phone number.');
      setLoading(false);
      return;
    }

    try {
      const payload = {
        pickup_location: pickupLocation,
        message: message,
        seats_needed: seatsNeeded,
        is_for_friend: isForFriend,
        friend_name: isForFriend ? friendName.trim() : null,
        friend_phone: isForFriend ? friendPhone.trim() : null
      };
      
      const res = await rideAPI.joinRide(ride.id, payload);
      if (res.data.success) {
        setSuccess(true);
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
        setTimeout(() => {
          if (onRequestSuccess) onRequestSuccess(res.data);
          onClose();
        }, 1800);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || err.response?.data?.message || 'Failed to submit join request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-modal w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl border border-slate-700">
        
        {/* Header */}
        <div className="p-6 pb-4 border-b border-slate-800 bg-slate-900/60 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 w-8 h-8 rounded-full bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center font-bold text-sm"
          >
            ✕
          </button>
          
          <h3 className="text-xl font-bold text-white font-outfit">Request to Join Ride</h3>
          <p className="text-xs text-slate-400 mt-1">
            Rider: <strong className="text-emerald-400">{ride.rider_name || (ride.rider && ride.rider.name)}</strong> • Route: {ride.from_location} ➔ {ride.to_location}
          </p>
        </div>

        {/* Form Body */}
        {success ? (
          <div className="p-8 text-center space-y-3">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/30">
              <CheckCircle2 className="w-8 h-8 animate-bounce" />
            </div>
            <h4 className="text-xl font-bold text-white">Request Sent Successfully!</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              The rider has been notified. Once they accept your request, contact details will be unlocked for pickup coordination.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Ride Snapshot */}
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
              <div>
                <span className="text-slate-400 text-[11px] block">Departure Time</span>
                <span className="font-bold text-white">{ride.departure_time || (ride.timing && ride.timing.departure_time)} ({ride.departure_date || 'Today'})</span>
              </div>
              <div className="text-right">
                <span className="text-slate-400 text-[11px] block">Contribution</span>
                <span className="font-bold text-emerald-400 font-mono text-sm">₹{ride.cost_per_person || 50} / seat</span>
              </div>
            </div>

            {/* Preferred Pickup Location */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-emerald-400" /> Preferred Pickup Point / Junction
              </label>
              <input
                type="text"
                required
                value={pickupLocation}
                onChange={(e) => setPickupLocation(e.target.value)}
                placeholder="e.g. Vadapalani Metro / Signal"
                className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl px-3 py-2.5 focus:border-emerald-500 focus:outline-none"
              />
              <p className="text-[11px] text-slate-400 mt-1">
                Tip: Choose a prominent bus stop or signal along the rider's road path for easy boarding.
              </p>
            </div>

            {/* Book for a Friend Toggle */}
            <div className="p-3 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="book_for_friend"
                  checked={isForFriend}
                  onChange={(e) => setIsForFriend(e.target.checked)}
                  className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 bg-slate-950 border-slate-700"
                />
                <label htmlFor="book_for_friend" className="text-xs font-bold text-slate-200 cursor-pointer">
                  👥 Booking for a friend / colleague
                </label>
              </div>

              {isForFriend && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 mb-1">Friend's Name</label>
                    <input
                      type="text"
                      required={isForFriend}
                      placeholder="e.g. Priya"
                      value={friendName}
                      onChange={(e) => setFriendName(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 text-white text-xs rounded-xl px-3 py-2 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 mb-1">Friend's Mobile Number</label>
                    <input
                      type="tel"
                      required={isForFriend}
                      placeholder="9840112233"
                      value={friendPhone}
                      onChange={(e) => setFriendPhone(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 text-white text-xs rounded-xl px-3 py-2 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Message to Rider */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                <MessageSquare className="w-3.5 h-3.5 text-cyan-400" /> Note to Rider
              </label>
              <textarea
                rows={2}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
                placeholder="Let the rider know your pickup spot or timings..."
              />
            </div>

            {/* Helmet Agreement */}
            <div className="flex items-center gap-2 pt-1 border-t border-slate-800/80">
              <input
                type="checkbox"
                id="passenger_helmet_check"
                required
                defaultChecked
                className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 bg-slate-900 border-slate-700"
              />
              <label htmlFor="passenger_helmet_check" className="text-xs font-semibold text-emerald-300 cursor-pointer">
                ⛑️ I agree to wear a helmet during the commute as per Motor Vehicles Act.
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
              {loading ? 'Sending Request...' : 'Confirm & Send Request'}
            </button>
          </form>
        )}

      </div>
    </div>
  );
}
