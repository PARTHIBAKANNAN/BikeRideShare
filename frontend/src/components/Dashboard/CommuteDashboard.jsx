import React, { useState, useEffect } from 'react';
import { rideAPI, dashboardAPI } from '../../api';
import confetti from 'canvas-confetti';
import { LayoutDashboard, Bike, ShieldCheck, CheckCircle2, XCircle, Phone, MessageSquare, Clock, MapPin, Sparkles, RefreshCw } from 'lucide-react';

export default function CommuteDashboard({ currentUser, onOpenPostRide }) {
  const [activeTab, setActiveTab] = useState('requests'); // requests | offered | booked
  const [pendingRequests, setPendingRequests] = useState([]);
  const [offeredRides, setOfferedRides] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  
  // AI Shift Auto-Pool State
  const [shiftRoutine, setShiftRoutine] = useState({
    home: currentUser?.home_location || 'Tambaram',
    work: currentUser?.work_location || 'DLF Cybercity',
    time: '08:30'
  });
  const [autoPoolMatches, setAutoPoolMatches] = useState([]);
  const [autoPoolLoading, setAutoPoolLoading] = useState(false);

  // Leaderboard State
  const [leaderboard, setLeaderboard] = useState([]);

  // Rating Modal State
  const [rateModal, setRateModal] = useState({
    open: false,
    requestId: null,
    name: '',
    rating: 5,
    feedback: '',
    badges: ['helmet_provided']
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // 1. Fetch user rides
      const ridesRes = await rideAPI.getMyRides('all');
      if (ridesRes.data && ridesRes.data.success) {
        setOfferedRides(ridesRes.data.rides || []);
      }

      // 2. Fetch my bookings
      const reqRes = await rideAPI.getMyRequests();
      if (reqRes.data && reqRes.data.success) {
        setMyBookings(reqRes.data.requests || []);
      }

      // 3. Fetch pending requests for user's offered rides
      if (ridesRes.data?.rides) {
        let allPending = [];
        for (const r of ridesRes.data.rides) {
          try {
            const rReq = await rideAPI.getRideRequests(r.id);
            if (rReq.data?.success && rReq.data?.requests) {
              const pendingOnly = rReq.data.requests.filter(req => req.status === 'pending');
              allPending = allPending.concat(pendingOnly.map(req => ({ ...req, ride_info: r })));
            }
          } catch (e) {
            // Ignore if no access
          }
        }
        setPendingRequests(allPending);
      }

      // 4. Quick stats
      const statsRes = await dashboardAPI.getQuickStats();
      if (statsRes.data && statsRes.data.success) {
        setStats(statsRes.data.stats);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchAutoPool = async () => {
    setAutoPoolLoading(true);
    try {
      const res = await rideAPI.getAutoPoolMatches({
        home_location: shiftRoutine.home,
        work_location: shiftRoutine.work,
        shift_time: shiftRoutine.time
      });
      if (res.data && res.data.success) {
        setAutoPoolMatches(res.data.auto_matches || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAutoPoolLoading(false);
    }
  };

  const handleFetchLeaderboard = async () => {
    try {
      const res = await rideAPI.getGreenLeaderboard();
      if (res.data && res.data.success) {
        setLeaderboard(res.data.leaderboard || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmitRating = async () => {
    if (!rateModal.requestId) return;
    try {
      const res = await rideAPI.rateRide(rateModal.requestId, {
        rating: rateModal.rating,
        feedback: rateModal.feedback,
        badges: rateModal.badges
      });
      if (res.data && res.data.success) {
        confetti({ particleCount: 60, spread: 60 });
        alert(res.data.message || 'Rating submitted successfully!');
        setRateModal({ open: false, requestId: null, name: '', rating: 5, feedback: '', badges: [] });
      }
    } catch (e) {
      console.error(e);
      alert('Failed to submit rating.');
    }
  };

  const handleRespondRequest = async (requestId, response) => {
    setActionLoading(requestId);
    try {
      const res = await rideAPI.respondToRequest(requestId, response);
      if (res.data && res.data.success) {
        if (response === 'accepted') {
          confetti({ particleCount: 70, spread: 60 });
        }
        fetchDashboardData();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header & Stats Cards */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white font-outfit flex items-center gap-2.5">
            <span>Commute Dashboard</span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">Manage your active Chennai rides, incoming requests, and travel bookings</p>
        </div>

        <button
          onClick={onOpenPostRide}
          className="py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold shadow-lg shadow-emerald-600/25 transition-all"
        >
          ➕ Post New Ride
        </button>
      </div>

      {/* Stats KPI Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-2xl glass-panel border border-slate-800">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Rides Offered</span>
          <div className="text-2xl font-extrabold text-white font-outfit mt-1">
            {stats?.rides_offered ?? currentUser?.total_rides_offered ?? 0}
          </div>
        </div>

        <div className="p-4 rounded-2xl glass-panel border border-slate-800">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Rides Taken</span>
          <div className="text-2xl font-extrabold text-cyan-400 font-outfit mt-1">
            {stats?.rides_taken ?? currentUser?.total_rides_taken ?? 0}
          </div>
        </div>

        <div className="p-4 rounded-2xl glass-panel border border-slate-800">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Commuter Rating</span>
          <div className="text-2xl font-extrabold text-amber-400 font-outfit mt-1 flex items-center gap-1">
            ⭐ {currentUser?.rating || 4.9}
          </div>
        </div>

        <div className="p-4 rounded-2xl glass-panel border border-slate-800">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Verification Status</span>
          <div className="text-sm font-bold text-emerald-400 mt-2 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4" />
            <span>{currentUser?.license_verified ? 'DL Verified' : 'Phone Verified'}</span>
          </div>
        </div>
      </div>

      {/* GREEN COMMUTER & PETROL SAVINGS STATS */}
      {(() => {
        const totalRides = (offeredRides.length * 2) + (myBookings.filter(b => b.status === 'accepted').length * 2) + 4;
        const petrolSaved = totalRides * 95; // avg ₹95 per single commute saved
        const co2Saved = (totalRides * 1.8).toFixed(1); // 1.8kg CO2 per trip
        return (
          <div className="p-5 rounded-3xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-teal-950/40 border border-emerald-500/30 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-lg">
                ₹
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400">Petrol Money Saved</span>
                <div className="text-xl font-extrabold text-emerald-400 font-mono">₹{petrolSaved.toLocaleString('en-IN')}</div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-teal-500/20 text-teal-400 flex items-center justify-center font-bold text-lg">
                🌱
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400">CO₂ Emissions Prevented</span>
                <div className="text-xl font-extrabold text-teal-300 font-mono">{co2Saved} kg CO₂</div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-lg">
                ⏱️
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400">Traffic Congestion Saved</span>
                <div className="text-xl font-extrabold text-cyan-300 font-mono">{(totalRides * 0.45).toFixed(1)} hours</div>
              </div>
            </div>
          </div>
        );
      })()}

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('requests')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all relative ${
            activeTab === 'requests'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Incoming Join Requests
          {pendingRequests.length > 0 && (
            <span className="ml-2 bg-emerald-500 text-slate-950 font-mono font-extrabold px-1.5 py-0.2 rounded-full text-[10px]">
              {pendingRequests.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('offered')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'offered'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          My Offered Rides ({offeredRides.length})
        </button>

        <button
          onClick={() => setActiveTab('booked')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'booked'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          My Booked Requests ({myBookings.length})
        </button>

        <button
          onClick={() => {
            setActiveTab('autopool');
            handleFetchAutoPool();
          }}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            activeTab === 'autopool'
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-extrabold'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" /> AI Daily Shift Auto-Pool
        </button>

        <button
          onClick={() => {
            setActiveTab('leaderboard');
            handleFetchLeaderboard();
          }}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            activeTab === 'leaderboard'
              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30 font-extrabold'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          🏆 Tech Park Green Leaderboard
        </button>
      </div>

      {/* Tab 1: Incoming Join Requests */}
      {activeTab === 'requests' && (
        <div className="space-y-3">
          {pendingRequests.length === 0 ? (
            <div className="p-10 rounded-3xl glass-panel text-center space-y-2 border border-slate-800">
              <div className="w-12 h-12 rounded-2xl bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              </div>
              <h4 className="text-sm font-bold text-white">All Caught Up!</h4>
              <p className="text-xs text-slate-400">No pending join requests for your offered rides right now.</p>
            </div>
          ) : (
            pendingRequests.map((req) => (
              <div key={req.id} className="p-5 rounded-3xl glass-panel border border-slate-800 shadow-lg space-y-3">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-cyan-600 font-bold flex items-center justify-center text-white text-sm">
                      {(req.passenger_name || 'P')[0]}
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white flex items-center gap-1.5">
                        {req.passenger_name || 'Passenger'}
                        <span className="text-xs text-amber-400">⭐ {req.passenger_rating || 5.0}</span>
                      </div>
                      <div className="text-xs text-slate-400">
                        Requested {req.seats_needed || 1} seat • {req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Today'}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 w-full sm:w-auto">
                    <button
                      disabled={actionLoading === req.id}
                      onClick={() => handleRespondRequest(req.id, 'accepted')}
                      className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center gap-1.5 shadow-md transition-all disabled:opacity-50"
                    >
                      <CheckCircle2 className="w-4 h-4" /> Accept Request
                    </button>

                    <button
                      disabled={actionLoading === req.id}
                      onClick={() => handleRespondRequest(req.id, 'rejected')}
                      className="flex-1 sm:flex-none px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-rose-400 text-xs font-bold flex items-center justify-center gap-1.5 transition-colors disabled:opacity-50"
                    >
                      <XCircle className="w-4 h-4" /> Reject
                    </button>
                  </div>
                </div>

                <div className="p-3 rounded-2xl bg-slate-950/60 border border-slate-800 text-xs space-y-1">
                  <div className="text-slate-300">
                    <strong className="text-emerald-400">Boarding Point:</strong> {req.pickup_location || 'Main Road Junction'}
                  </div>
                  {req.message && (
                    <div className="text-slate-400 italic">"{req.message}"</div>
                  )}
                  {req.passenger_phone && (
                    <div className="pt-1 text-slate-300 flex items-center gap-2 font-mono">
                      <Phone className="w-3.5 h-3.5 text-emerald-400" /> {req.passenger_phone}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: My Offered Rides */}
      {activeTab === 'offered' && (
        <div className="space-y-3">
          {offeredRides.length === 0 ? (
            <div className="p-10 rounded-3xl glass-panel text-center space-y-2 border border-slate-800">
              <p className="text-xs text-slate-400">You haven't posted any rides yet.</p>
              <button
                onClick={onOpenPostRide}
                className="mt-2 px-4 py-2 bg-emerald-600 text-white text-xs font-bold rounded-xl"
              >
                Offer Your First Ride
              </button>
            </div>
          ) : (
            offeredRides.map((ride) => (
              <div key={ride.id} className="p-4 rounded-2xl glass-panel border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-bold text-white flex items-center gap-2">
                    <span>{ride.from_location} ➔ {ride.to_location}</span>
                    <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full font-bold">
                      {ride.status || 'Active'}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    🕒 {ride.departure_time} ({ride.departure_date}) • ₹{ride.cost_per_person} • {ride.available_seats} seats left
                  </div>
                </div>

                <div className="text-right flex items-center gap-2">
                  <span className="text-xs font-bold text-emerald-400 font-mono">
                    {ride.current_passengers || 0} / {ride.available_seats || 1} Passengers
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 3: My Booked Requests */}
      {activeTab === 'booked' && (
        <div className="space-y-3">
          {myBookings.length === 0 ? (
            <div className="p-10 rounded-3xl glass-panel text-center space-y-2 border border-slate-800">
              <p className="text-xs text-slate-400">You haven't requested any rides yet.</p>
            </div>
          ) : (
            myBookings.map((req) => {
              const isConfirmed = req.status === 'accepted' || req.status === 'in_progress';
              return (
                <div key={req.id} className="p-5 rounded-3xl glass-panel border border-slate-800 space-y-3">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div>
                      <div className="text-sm font-bold text-white flex items-center gap-2">
                        <span>Pickup: {req.pickup_location || 'Requested Spot'}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                          isConfirmed ? 'bg-emerald-500/20 text-emerald-300' :
                          req.status === 'rejected' ? 'bg-rose-500/20 text-rose-300' :
                          'bg-amber-500/20 text-amber-300'
                        }`}>
                          {req.status ? req.status.toUpperCase() : 'PENDING'}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        Requested on {req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Today'}
                      </div>
                    </div>

                    {isConfirmed && (
                      <div className="p-3 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center gap-3">
                        <div>
                          <span className="text-[10px] text-emerald-300 uppercase font-bold block">Boarding OTP</span>
                          <span className="text-xl font-extrabold text-white font-mono tracking-widest">
                            {req.start_otp || '4821'}
                          </span>
                        </div>
                        <span className="text-[11px] text-emerald-200/90 leading-tight">
                          Share this 4-digit code with your rider upon arrival
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Safety & Action Controls for Confirmed Commute */}
                  {isConfirmed && (
                    <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {/* Share on WhatsApp */}
                        <a
                          href={`https://wa.me/?text=${encodeURIComponent(`Hi! I am taking a SmartRide Chennai bike pool. Pickup: ${req.pickup_location || 'Pickup spot'}. OTP: ${req.start_otp || '4821'}.`)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3 py-1.5 rounded-xl bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/40 text-xs font-bold flex items-center gap-1.5 transition-colors"
                        >
                          <span>💬 Share Live Trip on WhatsApp</span>
                        </a>

                        {/* Emergency SOS Button */}
                        <button
                          onClick={() => {
                            if (window.confirm("🚨 EMERGENCY SOS TRIGGER\n\nThis will initiate an emergency call to Chennai Police / Helpline 112. Do you want to proceed?")) {
                              window.open('tel:112');
                            }
                          }}
                          className="px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-rose-600/30 transition-colors animate-pulse"
                        >
                          <span>🚨 Emergency SOS (112)</span>
                        </button>

                        {/* Rate Rider Button */}
                        <button
                          onClick={() => setRateModal({ open: true, requestId: req.id, name: req.rider_name || 'Rider', rating: 5, feedback: '', badges: ['helmet_provided'] })}
                          className="px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-bold flex items-center gap-1 transition-colors"
                        >
                          <span>⭐ Rate & Review</span>
                        </button>
                      </div>

                      <span className="text-[11px] text-slate-400">⛑️ Please wear a safety helmet during the ride.</span>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Tab 4: AI Daily Shift Auto-Pool Matcher */}
      {activeTab === 'autopool' && (
        <div className="space-y-4">
          <div className="p-6 rounded-3xl glass-panel border border-cyan-500/30 bg-cyan-950/20 space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div>
                <h3 className="text-base font-bold text-white font-outfit flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-cyan-400" />
                  <span>AI Daily Shift Routine Matcher</span>
                </h3>
                <p className="text-xs text-slate-300 mt-0.5">
                  Set your daily Chennai office corridor routine. AI automatically pairs you with regular co-commuters.
                </p>
              </div>

              <button
                onClick={handleFetchAutoPool}
                disabled={autoPoolLoading}
                className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold flex items-center gap-1.5 shadow-md disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${autoPoolLoading ? 'animate-spin' : ''}`} />
                <span>Refresh Shift Matches</span>
              </button>
            </div>

            {/* Shift Form */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-400 mb-1">Home Origin Landmark</label>
                <input
                  type="text"
                  value={shiftRoutine.home}
                  onChange={(e) => setShiftRoutine({ ...shiftRoutine, home: e.target.value })}
                  placeholder="e.g. Tambaram / Vadapalani"
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-400 mb-1">Office / Tech Park Destination</label>
                <input
                  type="text"
                  value={shiftRoutine.work}
                  onChange={(e) => setShiftRoutine({ ...shiftRoutine, work: e.target.value })}
                  placeholder="e.g. DLF Cybercity / OMR Tidel"
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-400 mb-1">Morning Shift Timing</label>
                <input
                  type="time"
                  value={shiftRoutine.time}
                  onChange={(e) => setShiftRoutine({ ...shiftRoutine, time: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-cyan-500 focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Matches List */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Recommended Daily Corridor Co-Commuters ({autoPoolMatches.length})
            </h4>

            {autoPoolMatches.length === 0 ? (
              <div className="p-8 rounded-3xl glass-panel text-center text-xs text-slate-400 border border-slate-800">
                No active recurring commuters found along this route yet. Try updating your shift landmarks.
              </div>
            ) : (
              autoPoolMatches.map((m) => (
                <div key={m.id} className="p-4 rounded-2xl glass-panel border border-slate-800 hover:border-cyan-500/40 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white font-outfit">{m.from_location} ➔ {m.to_location}</span>
                      <span className="px-2 py-0.5 rounded-md bg-cyan-500/20 text-cyan-300 text-[10px] font-bold font-mono">
                        {m.match_score || 90}% Match
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Rider: <strong className="text-slate-200">{m.rider_name || 'Verified Rider'}</strong> • 🕒 {m.departure_time} • ₹{m.cost_per_person} / seat
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      if (window.confirm(`Request daily shift commute with ${m.rider_name || 'Rider'}?`)) {
                        rideAPI.joinRide(m.id, { pickup_location: m.from_location, message: 'Hi! Let us share our daily office commute regularly.' });
                        alert('Join request sent to daily shift rider!');
                      }
                    }}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-teal-500 text-white font-bold text-xs shadow-md hover:brightness-110"
                  >
                    Connect Shift Partner ➔
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab 5: Tech Park Green Leaderboard */}
      {activeTab === 'leaderboard' && (
        <div className="space-y-4">
          <div className="p-6 rounded-3xl glass-panel border border-amber-500/30 bg-amber-950/20 space-y-2">
            <h3 className="text-lg font-extrabold text-white font-outfit flex items-center gap-2">
              <span>🏆 Chennai Tech Park Green Commuter Leaderboard</span>
            </h3>
            <p className="text-xs text-slate-300">
              Ranking corporate technology corridors based on cumulative $CO_2$ prevented and shared commute adoption.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {leaderboard.map((item, idx) => (
              <div key={item.hub_id || idx} className="p-5 rounded-3xl glass-panel border border-slate-800 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs text-amber-400 font-bold block">{item.badge}</span>
                    <h4 className="text-base font-extrabold text-white font-outfit mt-0.5">{item.name}</h4>
                    <span className="text-[11px] text-slate-400">{item.corridor}</span>
                  </div>

                  <span className="w-8 h-8 rounded-full bg-slate-800 text-white font-extrabold flex items-center justify-center text-sm border border-slate-700">
                    #{idx + 1}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">CO₂ Prevented</span>
                    <span className="text-emerald-400 font-bold font-mono">{item.co2_saved_kg} kg</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">Petrol Saved</span>
                    <span className="text-teal-300 font-bold font-mono">₹{item.petrol_saved_inr.toLocaleString('en-IN')}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* RATING & COMPLIMENT MODAL */}
      {rateModal.open && (
        <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
          <div className="glass-modal max-w-md w-full rounded-3xl p-6 border border-slate-700 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h4 className="text-sm font-bold text-white font-outfit">Rate Commuter ({rateModal.name})</h4>
              <button onClick={() => setRateModal({ open: false, requestId: null, name: '', rating: 5, feedback: '', badges: [] })} className="text-slate-400 hover:text-white font-bold">✕</button>
            </div>

            {/* Star Rating */}
            <div className="flex items-center justify-center gap-2 py-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRateModal((prev) => ({ ...prev, rating: star }))}
                  className="text-2xl hover:scale-125 transition-transform"
                >
                  {star <= rateModal.rating ? '⭐' : '☆'}
                </button>
              ))}
            </div>

            {/* Compliment Badges */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-slate-300">Award Safety & Courtesy Badges:</label>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {[
                  { id: 'helmet_provided', label: '⛑️ Clean ISI Helmet' },
                  { id: 'punctual', label: '⏰ Punctual & On Time' },
                  { id: 'safe_rider', label: '🏍️ Smooth & Safe Rider' },
                  { id: 'friendly', label: '🤝 Courteous & Friendly' }
                ].map((b) => {
                  const isSelected = rateModal.badges.includes(b.id);
                  return (
                    <button
                      key={b.id}
                      type="button"
                      onClick={() => {
                        setRateModal((prev) => ({
                          ...prev,
                          badges: isSelected ? prev.badges.filter(x => x !== b.id) : [...prev.badges, b.id]
                        }));
                      }}
                      className={`p-2 rounded-xl text-left border text-[11px] font-bold transition-all ${
                        isSelected ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300' : 'bg-slate-900 border-slate-800 text-slate-400'
                      }`}
                    >
                      {b.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <textarea
              rows={2}
              value={rateModal.feedback}
              onChange={(e) => setRateModal((prev) => ({ ...prev, feedback: e.target.value }))}
              placeholder="Leave a short compliment note..."
              className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl p-3 text-xs focus:outline-none focus:border-amber-400"
            />

            <button
              onClick={handleSubmitRating}
              className="w-full py-3 bg-gradient-to-r from-amber-500 to-emerald-500 text-slate-950 font-extrabold text-xs rounded-xl shadow-lg hover:brightness-110"
            >
              Submit Rating & Badges
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
