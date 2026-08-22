import React, { useState, useEffect } from 'react';
import { bikeAPI, authAPI } from '../../api';
import { INDIAN_BIKE_CATALOG } from '../../constants/bikeCatalog';
import confetti from 'canvas-confetti';
import {
  Bike,
  Award,
  CheckCircle2,
  AlertCircle,
  Clock,
  Plus,
  Trash2,
  FileText,
  ShieldCheck,
  Zap,
  Image as ImageIcon,
  Sparkles,
  Camera,
  Calendar,
  Layers
} from 'lucide-react';

export default function BikeManager({ currentUser, onProfileUpdated }) {
  const [bikes, setBikes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showAddBike, setShowAddBike] = useState(false);
  const [showDLModal, setShowDLModal] = useState(false);
  const [msg, setMsg] = useState({ type: '', text: '' });

  // DL Form State
  const [licenseNumber, setLicenseNumber] = useState(currentUser?.license_number || '');
  const [licenseExpiryDate, setLicenseExpiryDate] = useState(currentUser?.license_expiry_date || '');
  const [licenseImageUrl, setLicenseImageUrl] = useState(currentUser?.license_image_url || '');

  // Bike Form State
  const [selectedBrand, setSelectedBrand] = useState('Royal Enfield');
  const [selectedModel, setSelectedModel] = useState('Hunter 350');
  const [bikeForm, setBikeForm] = useState({
    bike_number: '',
    bike_type: 'motorcycle',
    brand: 'Royal Enfield',
    model: 'Hunter 350',
    color: 'Dapper Grey',
    manufacture_year: new Date().getFullYear(),
    rc_number: '',
    rc_image_url: '',
    insurance_number: '',
    insurance_valid_till: ''
  });

  useEffect(() => {
    fetchBikes();
  }, []);

  const fetchBikes = async () => {
    setLoading(true);
    try {
      const res = await bikeAPI.getMyBikes();
      if (res.data && res.data.bikes) {
        setBikes(res.data.bikes);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleBrandChange = (brandName) => {
    setSelectedBrand(brandName);
    const brandObj = INDIAN_BIKE_CATALOG.find((b) => b.brand === brandName);
    const defaultModel = brandObj && brandObj.models.length > 0 ? brandObj.models[0] : '';
    setSelectedModel(defaultModel);
    
    let inferredType = 'motorcycle';
    if (brandObj?.type === 'scooter') inferredType = 'scooter';
    
    setBikeForm({
      ...bikeForm,
      brand: brandName,
      model: defaultModel,
      bike_type: inferredType
    });
  };

  const handleModelChange = (modelName) => {
    setSelectedModel(modelName);
    setBikeForm({
      ...bikeForm,
      model: modelName
    });
  };

  const handleAddBike = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    setMsg({ type: '', text: '' });
    try {
      const res = await bikeAPI.registerBike(bikeForm);
      if (res.data && res.data.success) {
        confetti({ particleCount: 70, spread: 60 });
        setMsg({ type: 'success', text: 'Vehicle registered! Submitted to Admin for approval.' });
        setShowAddBike(false);
        setBikeForm({
          bike_number: '',
          bike_type: 'motorcycle',
          brand: selectedBrand,
          model: selectedModel,
          color: 'Black',
          manufacture_year: new Date().getFullYear(),
          rc_number: '',
          rc_image_url: '',
          insurance_number: '',
          insurance_valid_till: ''
        });
        fetchBikes();
        if (onProfileUpdated) onProfileUpdated();
      }
    } catch (err) {
      const errList = err.response?.data?.errors;
      const errMsg = Array.isArray(errList) ? errList.join(', ') : (err.response?.data?.error || err.message);
      setMsg({ type: 'error', text: errMsg });
    } finally {
      setActionLoading(false);
    }
  };

  const handleSubmitDL = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    setMsg({ type: '', text: '' });
    try {
      const res = await authAPI.submitLicense({
        license_number: licenseNumber.trim(),
        license_expiry_date: licenseExpiryDate,
        license_image_url: licenseImageUrl.trim()
      });
      if (res.data && res.data.success) {
        confetti({ particleCount: 60, spread: 70 });
        setMsg({ type: 'success', text: 'Driver License submitted to Admin for approval!' });
        setShowDLModal(false);
        if (onProfileUpdated) onProfileUpdated();
      }
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.error || 'Failed to submit DL.' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleSetActiveBike = async (bikeId) => {
    try {
      const res = await bikeAPI.setActiveBike(bikeId);
      if (res.data && res.data.success) {
        setMsg({ type: 'success', text: 'Active commute bike updated!' });
        fetchBikes();
        if (onProfileUpdated) onProfileUpdated();
      }
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.error || 'Failed to activate bike.' });
    }
  };

  // DL Status Helpers
  const isDLApproved = currentUser?.license_verified === true;
  const isDLPending = currentUser?.license_verification_status === 'pending' && currentUser?.license_number;
  const isDLRejected = currentUser?.license_verification_status === 'rejected';

  // Bike Status Helpers
  const verifiedBikes = bikes.filter((b) => b.is_verified);
  const activeBike = bikes.find((b) => b.is_active);

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white font-outfit flex items-center gap-2.5">
            <Bike className="w-7 h-7 text-emerald-400" />
            <span>Vehicles & Driver License</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Register your two-wheeler & submit your Driving License to offer office commute rides.
          </p>
        </div>

        <button
          onClick={() => setShowAddBike(true)}
          className="px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-xs rounded-2xl shadow-lg hover:brightness-110 flex items-center gap-2 transition-all shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Two-Wheeler</span>
        </button>
      </div>

      {/* Global Alert Messages */}
      {msg.text && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center gap-3 animate-fadeIn ${
            msg.type === 'success'
              ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
              : 'bg-rose-500/15 border-rose-500/30 text-rose-300'
          }`}
        >
          {msg.type === 'success' ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <AlertCircle className="w-5 h-5 shrink-0" />}
          <span>{msg.text}</span>
        </div>
      )}

      {/* RENEWAL ALERT WARNING (If DL or Insurance expires in < 30 days) */}
      {(() => {
        const today = new Date();
        let dlDaysLeft = null;
        if (currentUser?.license_expiry_date) {
          const exp = new Date(currentUser.license_expiry_date);
          dlDaysLeft = Math.ceil((exp - today) / (1000 * 60 * 60 * 24));
        }

        const nearExpiryBikes = bikes.filter((b) => {
          if (!b.insurance_valid_till) return false;
          const exp = new Date(b.insurance_valid_till);
          const days = Math.ceil((exp - today) / (1000 * 60 * 60 * 24));
          return days <= 30;
        });

        if ((dlDaysLeft !== null && dlDaysLeft <= 30) || nearExpiryBikes.length > 0) {
          return (
            <div className="p-4 rounded-2xl bg-amber-500/15 border border-amber-500/40 text-amber-200 text-xs space-y-2">
              <div className="flex items-center gap-2 font-bold text-amber-300 text-sm">
                <AlertCircle className="w-4 h-4 text-amber-400" />
                <span>⚠️ Action Required: Document Renewal Alert</span>
              </div>
              <ul className="list-disc list-inside space-y-1 text-[11px] text-amber-200/90 pl-1">
                {dlDaysLeft !== null && dlDaysLeft <= 30 && (
                  <li>
                    Your Driving License {dlDaysLeft <= 0 ? 'has expired' : `expires in ${dlDaysLeft} days`} ({currentUser.license_expiry_date}). Please submit your renewed license to continue offering rides.
                  </li>
                )}
                {nearExpiryBikes.map((b) => (
                  <li key={b.id}>
                    Vehicle insurance for <strong>{b.bike_number}</strong> expires on {b.insurance_valid_till}. Please update insurance details.
                  </li>
                ))}
              </ul>
            </div>
          );
        }
        return null;
      })()}

      {/* RIDER VERIFICATION PROGRESS STEPPER */}
      <div className="p-5 sm:p-6 rounded-3xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="text-sm font-bold text-white font-outfit uppercase tracking-wider">
              Ride Provider (Rider) Verification Checklist
            </h3>
          </div>
          <span className="text-[11px] text-slate-400">Admin Approval Required (&gt;30 Days Validity)</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* 1. Driver License Card */}
          <div className={`p-4 rounded-2xl border transition-all ${
            isDLApproved 
              ? 'bg-emerald-950/20 border-emerald-500/40' 
              : isDLRejected
                ? 'bg-rose-950/20 border-rose-500/40'
                : isDLPending 
                  ? 'bg-amber-950/20 border-amber-500/40'
                  : 'bg-slate-900/60 border-slate-800'
          }`}>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2.5">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                  isDLApproved ? 'bg-emerald-500/20 text-emerald-400' : isDLRejected ? 'bg-rose-500/20 text-rose-400' : isDLPending ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-400'
                }`}>
                  <Award className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white">1. Driving License (DL)</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {currentUser?.license_number ? `No: ${currentUser.license_number}` : 'Not submitted yet'}
                  </p>
                </div>
              </div>

              {isDLApproved && (
                <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 text-[10px] font-bold border border-emerald-500/40 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Approved
                </span>
              )}
              {isDLRejected && (
                <span className="px-2.5 py-1 rounded-lg bg-rose-500/20 text-rose-300 text-[10px] font-bold border border-rose-500/40 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> Rejected
                </span>
              )}
              {isDLPending && (
                <span className="px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/40 flex items-center gap-1">
                  <Clock className="w-3 h-3 animate-spin" /> Pending Admin Review
                </span>
              )}
              {!currentUser?.license_number && !isDLRejected && (
                <span className="px-2.5 py-1 rounded-lg bg-rose-500/20 text-rose-300 text-[10px] font-bold border border-rose-500/40">
                  Required
                </span>
              )}
            </div>

            {isDLRejected && currentUser?.license_rejection_reason && (
              <div className="mt-2.5 p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-[11px] text-rose-300">
                <strong>Rejection Reason:</strong> {currentUser.license_rejection_reason}
              </div>
            )}

            <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-[11px] text-slate-400">
                {currentUser?.license_expiry_date ? `Valid till: ${currentUser.license_expiry_date}` : 'Must be valid >30 days'}
              </span>
              <button
                onClick={() => setShowDLModal(true)}
                className="text-xs font-bold text-emerald-400 hover:text-emerald-300 underline"
              >
                {currentUser?.license_number ? 'Update / Resubmit DL' : 'Submit DL for Approval ➔'}
              </button>
            </div>
          </div>

          {/* 2. Bike Registration Card */}
          <div className={`p-4 rounded-2xl border transition-all ${
            verifiedBikes.length > 0
              ? 'bg-emerald-950/20 border-emerald-500/40' 
              : bikes.length > 0 
                ? 'bg-amber-950/20 border-amber-500/40'
                : 'bg-slate-900/60 border-slate-800'
          }`}>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2.5">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                  verifiedBikes.length > 0 ? 'bg-emerald-500/20 text-emerald-400' : bikes.length > 0 ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-400'
                }`}>
                  <Bike className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white">2. Vehicle RC & Insurance</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    {bikes.length} registered ({verifiedBikes.length} verified)
                  </p>
                </div>
              </div>

              {verifiedBikes.length > 0 && (
                <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 text-[10px] font-bold border border-emerald-500/40 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Ready
                </span>
              )}
              {bikes.length > 0 && verifiedBikes.length === 0 && (
                <span className="px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/40 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> Pending Admin Review
                </span>
              )}
              {bikes.length === 0 && (
                <span className="px-2.5 py-1 rounded-lg bg-rose-500/20 text-rose-300 text-[10px] font-bold border border-rose-500/40">
                  Required
                </span>
              )}
            </div>

            <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-[11px] text-slate-400">
                {activeBike ? `Active: ${activeBike.brand} ${activeBike.model}` : 'Select active bike below'}
              </span>
              <button
                onClick={() => setShowAddBike(true)}
                className="text-xs font-bold text-emerald-400 hover:text-emerald-300 underline"
              >
                + Register Vehicle ➔
              </button>
            </div>
          </div>

        </div>
      </div>

      {/* REGISTERED VEHICLES LIST */}
      <div className="space-y-3">
        <h3 className="text-base font-bold text-white font-outfit flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>My Registered Two-Wheelers ({bikes.length})</span>
        </h3>

        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading registered vehicles...</div>
        ) : bikes.length === 0 ? (
          <div className="p-8 rounded-3xl glass-panel text-center space-y-2 border border-slate-800">
            <Bike className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-300 font-semibold">No two-wheelers registered yet.</p>
            <p className="text-[11px] text-slate-500">Add your bike or scooter to start offering carpooling rides to Chennai commuters.</p>
            <button
              onClick={() => setShowAddBike(true)}
              className="mt-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl transition-all inline-flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" /> Add Vehicle
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {bikes.map((b) => (
              <div
                key={b.id}
                className={`p-5 rounded-3xl glass-panel border transition-all ${
                  b.is_active ? 'border-emerald-500 shadow-lg shadow-emerald-500/10' : 'border-slate-800'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-700 flex items-center justify-center text-emerald-400">
                      <Bike className="w-6 h-6" />
                    </div>
                    <div>
                      <div className="text-base font-bold text-white font-outfit">
                        {b.brand} {b.model}
                      </div>
                      <div className="text-xs font-mono font-extrabold text-emerald-400 tracking-wider">
                        {b.bike_number}
                      </div>
                    </div>
                  </div>

                  {b.is_verified ? (
                    <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 text-[10px] font-bold border border-emerald-500/30 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Verified
                    </span>
                  ) : b.verification_status === 'rejected' ? (
                    <span className="px-2.5 py-1 rounded-lg bg-rose-500/20 text-rose-300 text-[10px] font-bold border border-rose-500/30 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> Rejected
                    </span>
                  ) : (
                    <span className="px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/30 flex items-center gap-1">
                      <Clock className="w-3 h-3" /> Pending Approval
                    </span>
                  )}
                </div>

                {b.verification_status === 'rejected' && b.rejection_reason && (
                  <div className="mt-2.5 p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-[11px] text-rose-300">
                    <strong>Admin Note:</strong> {b.rejection_reason}
                  </div>
                )}

                <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-xs text-slate-400">
                  <div>
                    <span className="text-[10px] text-slate-500 block">Type & Color:</span>
                    <span className="text-slate-200 capitalize font-medium">{b.bike_type} • {b.color || 'Standard'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Insurance Expiry:</span>
                    <span className="text-slate-200 font-mono">{b.insurance_valid_till || 'Not Provided'}</span>
                  </div>
                </div>

                {/* Active Switcher */}
                <div className="mt-4 flex items-center justify-between pt-2 border-t border-slate-800/50">
                  {b.is_active ? (
                    <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" /> Active Ride Vehicle
                    </span>
                  ) : b.is_verified ? (
                    <button
                      onClick={() => handleSetActiveBike(b.id)}
                      className="text-xs font-bold text-emerald-400 hover:text-emerald-300 underline"
                    >
                      Set as Active Bike
                    </button>
                  ) : (
                    <span className="text-[11px] text-slate-500 italic">
                      {b.verification_status === 'rejected' ? 'Action: Re-register with valid documents' : 'Awaiting Admin Verification'}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* REGISTER TWO-WHEELER MODAL */}
      {showAddBike && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
          <div className="glass-modal w-full max-w-xl rounded-3xl p-6 border border-slate-700 shadow-2xl space-y-4 my-8">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Bike className="w-5 h-5 text-emerald-400" />
                <h3 className="text-lg font-bold text-white font-outfit">Register Two-Wheeler</h3>
              </div>
              <button
                onClick={() => setShowAddBike(false)}
                className="text-slate-400 hover:text-white font-bold text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAddBike} className="space-y-4">
              {/* Popular Indian Brand Selector */}
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Select Bike Manufacturer / Brand</span>
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {INDIAN_BIKE_CATALOG.map((b) => (
                    <button
                      key={b.brand}
                      type="button"
                      onClick={() => handleBrandChange(b.brand)}
                      className={`p-2 rounded-xl text-left border transition-all text-xs flex flex-col justify-between ${
                        selectedBrand === b.brand
                          ? 'bg-emerald-500/20 border-emerald-500 text-white font-bold shadow-md shadow-emerald-500/10'
                          : 'bg-slate-900/80 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                      }`}
                    >
                      <span className="truncate">{b.brand}</span>
                      <span className="text-[10px] text-slate-500 capitalize">{b.type}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Model Dropdown from Catalog */}
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">
                  Select {selectedBrand} Model
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => handleModelChange(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
                >
                  {INDIAN_BIKE_CATALOG.find((b) => b.brand === selectedBrand)?.models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>

              {/* Vehicle Number & Type */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Vehicle Plate Number</label>
                  <input
                    type="text"
                    required
                    placeholder="TN09AB1234"
                    value={bikeForm.bike_number}
                    onChange={(e) => setBikeForm({ ...bikeForm, bike_number: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none font-mono uppercase"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Vehicle Category</label>
                  <select
                    value={bikeForm.bike_type}
                    onChange={(e) => setBikeForm({ ...bikeForm, bike_type: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none capitalize"
                  >
                    <option value="motorcycle">Motorcycle / Standard Bike</option>
                    <option value="scooter">Scooter (Activa, Jupiter, etc.)</option>
                    <option value="ev">Electric Scooter / EV (Ather, Ola, Chetak)</option>
                  </select>
                </div>
              </div>

              {/* RC Number & Document Image */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">RC Book Number</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. RC-TN09-2023-8899"
                    value={bikeForm.rc_number}
                    onChange={(e) => setBikeForm({ ...bikeForm, rc_number: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">RC Document Photo / URL</label>
                  <input
                    type="url"
                    placeholder="https://.../rc_photo.jpg"
                    value={bikeForm.rc_image_url}
                    onChange={(e) => setBikeForm({ ...bikeForm, rc_image_url: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Insurance Number & Valid Till */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Insurance Policy Number</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. POL-88992211"
                    value={bikeForm.insurance_number}
                    onChange={(e) => setBikeForm({ ...bikeForm, insurance_number: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">
                    Insurance Expiry Date <span className="text-amber-400 text-[10px]">(Must be &gt;30 days)</span>
                  </label>
                  <input
                    type="date"
                    required
                    min={(() => {
                      const d = new Date();
                      d.setDate(d.getDate() + 31);
                      return d.toISOString().split('T')[0];
                    })()}
                    value={bikeForm.insurance_valid_till}
                    onChange={(e) => setBikeForm({ ...bikeForm, insurance_valid_till: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                <span>Strict Safety Rule: Vehicle insurance policy must have a minimum of 30 days remaining validity.</span>
              </div>

              <button
                type="submit"
                disabled={actionLoading}
                className="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-xs rounded-xl shadow-lg hover:brightness-110 transition-all disabled:opacity-50 mt-2"
              >
                {actionLoading ? 'Submitting...' : 'Register Vehicle & Submit to Admin'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* SUBMIT DRIVER LICENSE MODAL */}
      {showDLModal && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
          <div className="glass-modal w-full max-w-md rounded-3xl p-6 border border-slate-700 shadow-2xl space-y-4 my-8">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Award className="w-5 h-5 text-emerald-400" />
                <h3 className="text-lg font-bold text-white font-outfit">Submit Driver License</h3>
              </div>
              <button
                onClick={() => setShowDLModal(false)}
                className="text-slate-400 hover:text-white font-bold text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitDL} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">
                  Indian / Tamil Nadu DL Number
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. TN-09-2022-0012345"
                  value={licenseNumber}
                  onChange={(e) => setLicenseNumber(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none font-mono uppercase"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">
                  License Expiry Date <span className="text-amber-400 text-[10px]">(Must be &gt;30 days)</span>
                </label>
                <input
                  type="date"
                  required
                  min={(() => {
                    const d = new Date();
                    d.setDate(d.getDate() + 31);
                    return d.toISOString().split('T')[0];
                  })()}
                  value={licenseExpiryDate}
                  onChange={(e) => setLicenseExpiryDate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">License Card Photo / URL</label>
                <input
                  type="url"
                  placeholder="https://.../dl_photo.jpg"
                  value={licenseImageUrl}
                  onChange={(e) => setLicenseImageUrl(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                <span>Driving license must have at least 30 days of future validity. Admin will review before approving.</span>
              </div>

              <button
                type="submit"
                disabled={actionLoading}
                className="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-extrabold text-xs rounded-xl shadow-lg hover:brightness-110 transition-all disabled:opacity-50"
              >
                {actionLoading ? 'Submitting DL...' : 'Submit DL for Approval'}
              </button>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
