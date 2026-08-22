import React, { useState, useEffect } from 'react';
import { adminAPI, rideAPI } from '../../api';
import confetti from 'canvas-confetti';
import {
  Shield,
  Users,
  Bike,
  Route,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  Award,
  FileText,
  Eye,
  Calendar,
  Phone,
  Mail,
  UserX,
  UserCheck,
  Clock,
  Sparkles
} from 'lucide-react';

export default function AdminPortal() {
  const [activeTab, setActiveTab] = useState('approvals'); // approvals | users | rides
  const [stats, setStats] = useState(null);
  const [pendingLicenses, setPendingLicenses] = useState([]);
  const [pendingBikes, setPendingBikes] = useState([]);
  const [usersList, setUsersList] = useState([]);
  const [ridesList, setRidesList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [msg, setMsg] = useState('');
  const [previewImage, setPreviewImage] = useState(null);
  const [rejectModal, setRejectModal] = useState({ open: false, type: '', id: null, title: '', reason: '' });

  const REJECTION_PRESETS = [
    "Blurry or unreadable document photograph",
    "Expired document / Less than 30 days future validity",
    "Name on document does not match account name",
    "Vehicle registration number mismatch on RC",
    "Invalid vehicle category (must be a valid two-wheeler)",
    "Expired commercial/third-party insurance policy"
  ];

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      // 1. Dashboard stats
      const dRes = await adminAPI.getDashboard();
      if (dRes.data && dRes.data.success) {
        setStats(dRes.data.stats);
      }

      // 2. Pending license verifications
      const lRes = await adminAPI.getLicenseVerifications();
      if (lRes.data && lRes.data.success) {
        setPendingLicenses(lRes.data.users || lRes.data.pending_verifications || []);
      }

      // 3. Pending bike verifications
      const bRes = await adminAPI.getBikeVerifications();
      if (bRes.data && bRes.data.success) {
        setPendingBikes(bRes.data.pending_bikes || []);
      }

      // 4. Users list
      const uRes = await adminAPI.getUsers({ per_page: 50 });
      if (uRes.data && uRes.data.success) {
        setUsersList(uRes.data.users || []);
      }

      // 5. Rides list
      const rRes = await adminAPI.getAllRides({ per_page: 50 });
      if (rRes.data && rRes.data.success) {
        setRidesList(rRes.data.rides || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyLicense = async (userId, action, reason = '') => {
    setActionLoading(`dl-${userId}`);
    try {
      const res = await adminAPI.verifyLicense(userId, action, reason);
      if (res.data && res.data.success) {
        setMsg(`Driver License ${action === 'approve' ? 'Approved' : 'Rejected'} successfully!`);
        if (action === 'approve') confetti({ particleCount: 60, spread: 70 });
        setRejectModal({ open: false, type: '', id: null, title: '', reason: '' });
        fetchAdminData();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  const handleVerifyBike = async (bikeId, action, reason = '') => {
    setActionLoading(`bike-${bikeId}`);
    try {
      const res = await adminAPI.verifyBike(bikeId, action, reason);
      if (res.data && res.data.success) {
        setMsg(`Two-Wheeler ${action === 'approve' ? 'Approved' : 'Rejected'} successfully!`);
        if (action === 'approve') confetti({ particleCount: 60, spread: 70 });
        setRejectModal({ open: false, type: '', id: null, title: '', reason: '' });
        fetchAdminData();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  const confirmRejection = () => {
    if (!rejectModal.reason) {
      alert('Please specify or select a reason for rejection.');
      return;
    }
    if (rejectModal.type === 'dl') {
      handleVerifyLicense(rejectModal.id, 'reject', rejectModal.reason);
    } else if (rejectModal.type === 'bike') {
      handleVerifyBike(rejectModal.id, 'reject', rejectModal.reason);
    }
  };

  const handleToggleUserFlag = async (userId, isFlagged) => {
    setActionLoading(`user-${userId}`);
    try {
      if (isFlagged) {
        await adminAPI.unflagUser(userId);
        setMsg('User unflagged successfully!');
      } else {
        await adminAPI.flagUser(userId, 'Admin moderation review');
        setMsg('User flagged!');
      }
      fetchAdminData();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  const totalPending = pendingLicenses.length + pendingBikes.length;

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-md bg-purple-500/20 text-purple-300 font-mono text-[10px] font-bold border border-purple-500/30">
              admin@gmail.com
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white font-outfit flex items-center gap-2.5 mt-1">
            <Shield className="w-7 h-7 text-purple-400" />
            <span>Admin Moderation & Approvals</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Approve DLs, verify registered two-wheelers, and monitor Chennai bike pool operations.
          </p>
        </div>

        <button
          onClick={fetchAdminData}
          className="p-2.5 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors self-start sm:self-auto flex items-center gap-2 text-xs font-bold"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {msg && (
        <div className="p-3.5 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{msg}</span>
          </div>
          <button onClick={() => setMsg('')} className="text-xs text-emerald-400 font-bold">✕</button>
        </div>
      )}

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-4 rounded-2xl glass-panel border border-slate-800">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Commuters</span>
          <div className="text-2xl font-extrabold text-white font-outfit mt-1">{usersList.length}</div>
        </div>

        <div className="p-4 rounded-2xl glass-panel border border-slate-800">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Active Rides</span>
          <div className="text-2xl font-extrabold text-cyan-400 font-outfit mt-1">{ridesList.length}</div>
        </div>

        <div className="p-4 rounded-2xl glass-panel border border-purple-500/30 bg-purple-950/20">
          <span className="text-[10px] font-bold text-purple-300 uppercase tracking-wider">Pending DLs</span>
          <div className="text-2xl font-extrabold text-purple-400 font-outfit mt-1">{pendingLicenses.length}</div>
        </div>

        <div className="p-4 rounded-2xl glass-panel border border-emerald-500/30 bg-emerald-950/20">
          <span className="text-[10px] font-bold text-emerald-300 uppercase tracking-wider">Pending Bikes</span>
          <div className="text-2xl font-extrabold text-emerald-400 font-outfit mt-1">{pendingBikes.length}</div>
        </div>
      </div>

      {/* Admin Navigation Tabs */}
      <div className="flex border-b border-slate-800 gap-2">
        <button
          onClick={() => setActiveTab('approvals')}
          className={`pb-3 px-3 text-xs font-bold transition-all relative ${
            activeTab === 'approvals' ? 'text-purple-400 border-b-2 border-purple-500' : 'text-slate-400 hover:text-white'
          }`}
        >
          Pending Approvals {totalPending > 0 && <span className="ml-1.5 px-1.5 py-0.5 rounded-full bg-purple-500 text-white text-[10px]">{totalPending}</span>}
        </button>

        <button
          onClick={() => setActiveTab('users')}
          className={`pb-3 px-3 text-xs font-bold transition-all relative ${
            activeTab === 'users' ? 'text-purple-400 border-b-2 border-purple-500' : 'text-slate-400 hover:text-white'
          }`}
        >
          Commuter Users ({usersList.length})
        </button>

        <button
          onClick={() => setActiveTab('rides')}
          className={`pb-3 px-3 text-xs font-bold transition-all relative ${
            activeTab === 'rides' ? 'text-purple-400 border-b-2 border-purple-500' : 'text-slate-400 hover:text-white'
          }`}
        >
          Active Ride Offers ({ridesList.length})
        </button>
      </div>

      {/* TAB 1: PENDING APPROVALS */}
      {activeTab === 'approvals' && (
        <div className="space-y-6">
          
          {/* A. Pending Driving Licenses */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <Award className="w-4 h-4 text-purple-400" />
              <span>Pending Driver License Submissions ({pendingLicenses.length})</span>
            </h3>

            {pendingLicenses.length === 0 ? (
              <div className="p-6 rounded-2xl glass-panel text-center border border-slate-800/80">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                <p className="text-xs text-slate-300 font-semibold">Zero Pending License Approvals</p>
                <p className="text-[11px] text-slate-500">All submitted licenses are reviewed.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pendingLicenses.map((u) => (
                  <div key={u.id || u.user_id} className="p-4 rounded-2xl glass-panel border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{u.name}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-md bg-purple-500/20 text-purple-300 font-mono">
                          ID: #{u.id || u.user_id}
                        </span>
                      </div>

                      <div className="text-xs text-slate-400 flex flex-wrap items-center gap-3">
                        <span className="flex items-center gap-1"><Phone className="w-3 h-3 text-slate-500" /> {u.phone}</span>
                        <span className="flex items-center gap-1"><Mail className="w-3 h-3 text-slate-500" /> {u.email}</span>
                      </div>

                      <div className="text-xs text-purple-300 font-mono font-bold pt-1 flex items-center gap-2 flex-wrap">
                        <span>DL No: {u.license_number || 'N/A'}</span>
                        {u.license_expiry_date && (
                          <span className="text-slate-400 font-normal"> (Valid till: {u.license_expiry_date})</span>
                        )}
                        {u.is_critical_expiry && (
                          <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px] font-bold">
                            ⚠️ Critical: {u.days_until_expiry <= 0 ? 'Expired' : `Expires in ${u.days_until_expiry}d`}
                          </span>
                        )}
                        {u.is_near_expiry && !u.is_critical_expiry && (
                          <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold">
                            ⚠️ Near Expiry: {u.days_until_expiry}d left
                          </span>
                        )}
                      </div>

                      {u.license_image_url && (
                        <button
                          onClick={() => setPreviewImage({ title: `${u.name}'s Driving License`, url: u.license_image_url })}
                          className="mt-1 text-[11px] text-cyan-400 hover:text-cyan-300 underline inline-flex items-center gap-1"
                        >
                          <Eye className="w-3 h-3" /> View DL Photo Preview
                        </button>
                      )}
                    </div>

                    <div className="flex items-center gap-2 self-end md:self-auto">
                      <button
                        disabled={actionLoading === `dl-${u.id || u.user_id}`}
                        onClick={() => handleVerifyLicense(u.id || u.user_id, 'approve')}
                        className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-md disabled:opacity-50"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" /> Approve DL
                      </button>

                      <button
                        disabled={actionLoading === `dl-${u.id || u.user_id}`}
                        onClick={() => setRejectModal({
                          open: true,
                          type: 'dl',
                          id: u.id || u.user_id,
                          title: `Reject DL for ${u.name}`,
                          reason: REJECTION_PRESETS[0]
                        })}
                        className="px-4 py-2 rounded-xl bg-rose-600/30 hover:bg-rose-600/50 text-rose-300 border border-rose-500/40 text-xs font-bold flex items-center gap-1.5 transition-colors disabled:opacity-50"
                      >
                        <XCircle className="w-3.5 h-3.5" /> Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* B. Pending Two-Wheeler Approvals */}
          <div className="space-y-3 pt-4 border-t border-slate-800">
            <h3 className="text-sm font-bold text-white font-outfit flex items-center gap-2">
              <Bike className="w-4 h-4 text-emerald-400" />
              <span>Pending Two-Wheeler Approvals ({pendingBikes.length})</span>
            </h3>

            {pendingBikes.length === 0 ? (
              <div className="p-6 rounded-2xl glass-panel text-center border border-slate-800/80">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                <p className="text-xs text-slate-300 font-semibold">Zero Pending Vehicle Approvals</p>
                <p className="text-[11px] text-slate-500">All registered bikes and scooters are verified.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pendingBikes.map((b) => (
                  <div key={b.bike_id || b.id} className="p-4 rounded-2xl glass-panel border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white font-outfit">{b.brand} {b.model}</span>
                        <span className="text-xs font-mono font-extrabold text-emerald-400 px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20">
                          {b.bike_number}
                        </span>
                      </div>

                      <div className="text-xs text-slate-400">
                        Owner: <span className="text-slate-200 font-semibold">{b.owner?.name || 'Commuter'}</span> • Phone: <span className="font-mono">{b.owner?.phone || 'N/A'}</span>
                      </div>

                      <div className="text-xs text-slate-400 flex flex-wrap items-center gap-3 pt-0.5">
                        <span>RC No: <strong className="text-slate-200 font-mono">{b.rc_number || 'N/A'}</strong></span>
                        {b.insurance_valid_till && <span>Insurance Till: <strong className="text-slate-200">{b.insurance_valid_till}</strong></span>}
                        {b.is_critical_insurance_expiry && (
                          <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 text-[10px] font-bold">
                            ⚠️ Ins. Critical: {b.days_until_insurance_expiry <= 0 ? 'Expired' : `${b.days_until_insurance_expiry}d left`}
                          </span>
                        )}
                        {b.is_near_insurance_expiry && !b.is_critical_insurance_expiry && (
                          <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold">
                            ⚠️ Ins. Expiring: {b.days_until_insurance_expiry}d
                          </span>
                        )}
                      </div>

                      {b.rc_image_url && (
                        <button
                          onClick={() => setPreviewImage({ title: `${b.brand} ${b.model} RC Document`, url: b.rc_image_url })}
                          className="mt-1 text-[11px] text-cyan-400 hover:text-cyan-300 underline inline-flex items-center gap-1"
                        >
                          <Eye className="w-3 h-3" /> View RC Document Photo
                        </button>
                      )}
                    </div>

                    <div className="flex items-center gap-2 self-end md:self-auto">
                      <button
                        disabled={actionLoading === `bike-${b.bike_id || b.id}`}
                        onClick={() => handleVerifyBike(b.bike_id || b.id, 'approve')}
                        className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-1.5 transition-all shadow-md disabled:opacity-50"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" /> Approve Bike
                      </button>

                      <button
                        disabled={actionLoading === `bike-${b.bike_id || b.id}`}
                        onClick={() => setRejectModal({
                          open: true,
                          type: 'bike',
                          id: b.bike_id || b.id,
                          title: `Reject ${b.brand} ${b.model} (${b.bike_number})`,
                          reason: REJECTION_PRESETS[0]
                        })}
                        className="px-4 py-2 rounded-xl bg-rose-600/30 hover:bg-rose-600/50 text-rose-300 border border-rose-500/40 text-xs font-bold flex items-center gap-1.5 transition-colors disabled:opacity-50"
                      >
                        <XCircle className="w-3.5 h-3.5" /> Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      )}

      {/* TAB 2: COMMUTER USERS */}
      {activeTab === 'users' && (
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-white font-outfit">Platform Commuter Directory</h3>
          <div className="space-y-2">
            {usersList.map((u) => (
              <div key={u.id} className="p-3.5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <div className="font-bold text-white">{u.name}</div>
                  <div className="text-slate-400 mt-0.5">{u.email} • {u.phone}</div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                    u.license_verified ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {u.license_verified ? 'DL Verified' : 'DL Unverified'}
                  </span>

                  <button
                    disabled={actionLoading === `user-${u.id}`}
                    onClick={() => handleToggleUserFlag(u.id, u.is_flagged)}
                    className={`p-1.5 rounded-lg border text-[11px] font-bold ${
                      u.is_flagged
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
                    }`}
                  >
                    {u.is_flagged ? 'Unflag' : 'Flag'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: ACTIVE RIDES */}
      {activeTab === 'rides' && (
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-white font-outfit">All Active Commute Rides</h3>
          {ridesList.length === 0 ? (
            <div className="p-6 rounded-2xl glass-panel text-center text-xs text-slate-500 border border-slate-800">
              No active rides posted yet.
            </div>
          ) : (
            <div className="space-y-2">
              {ridesList.map((r) => (
                <div key={r.id} className="p-3.5 rounded-2xl glass-panel border border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <div className="font-bold text-white">{r.from_location} ➔ {r.to_location}</div>
                    <div className="text-slate-400 mt-0.5">
                      Rider: {r.rider?.name} • ₹{r.price_per_seat} • {r.departure_time}
                    </div>
                  </div>
                  <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 font-bold text-[10px]">
                    {r.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* REJECTION REASON MODAL */}
      {rejectModal.open && (
        <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
          <div className="glass-modal max-w-md w-full rounded-3xl p-6 border border-slate-700 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h4 className="text-sm font-bold text-rose-300 font-outfit flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                <span>{rejectModal.title}</span>
              </h4>
              <button onClick={() => setRejectModal({ open: false, type: '', id: null, title: '', reason: '' })} className="text-slate-400 hover:text-white font-bold">✕</button>
            </div>

            <div className="space-y-3 text-xs">
              <label className="block text-slate-300 font-bold">Select Preset Rejection Reason:</label>
              <select
                value={rejectModal.reason}
                onChange={(e) => setRejectModal((prev) => ({ ...prev, reason: e.target.value }))}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl p-3 focus:outline-none focus:border-rose-500 text-xs"
              >
                {REJECTION_PRESETS.map((p, idx) => (
                  <option key={idx} value={p}>{p}</option>
                ))}
              </select>

              <label className="block text-slate-300 font-bold mt-2">Or Type Custom Admin Note:</label>
              <textarea
                rows={2}
                value={rejectModal.reason}
                onChange={(e) => setRejectModal((prev) => ({ ...prev, reason: e.target.value }))}
                placeholder="Explain why this document was rejected..."
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-xl p-3 focus:outline-none focus:border-rose-500 text-xs"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setRejectModal({ open: false, type: '', id: null, title: '', reason: '' })}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 font-bold text-xs"
              >
                Cancel
              </button>
              <button
                onClick={confirmRejection}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs shadow-lg"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* DOCUMENT PREVIEW MODAL */}
      {previewImage && (
        <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
          <div className="glass-modal max-w-lg w-full rounded-3xl p-5 border border-slate-700 shadow-2xl space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <h4 className="text-sm font-bold text-white font-outfit">{previewImage.title}</h4>
              <button onClick={() => setPreviewImage(null)} className="text-slate-400 hover:text-white font-bold">✕</button>
            </div>
            <div className="max-h-[60vh] overflow-hidden rounded-2xl border border-slate-800 bg-black flex items-center justify-center">
              <img src={previewImage.url} alt="Document" className="w-full h-auto object-contain" />
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
