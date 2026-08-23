import React, { useState } from 'react';
import { authAPI } from '../../api';
import { 
  LogIn, UserPlus, Shield, X, Eye, EyeOff, CheckCircle2, AlertCircle, 
  Sparkles, Key, ShieldCheck, Calendar, User, Phone, Mail, MapPin, Briefcase, Heart 
} from 'lucide-react';
import confetti from 'canvas-confetti';

const AVATARS = [
  { id: 'avatar-1', label: 'Urban Rider', icon: '🏍️' },
  { id: 'avatar-2', label: 'Tech Pro', icon: '💻' },
  { id: 'avatar-3', label: 'Eco Commuter', icon: '🌿' },
  { id: 'avatar-4', label: 'IT Executive', icon: '💼' },
  { id: 'avatar-5', label: 'Pink Champion', icon: '🌸' },
  { id: 'avatar-6', label: 'Speedster', icon: '⚡' },
  { id: 'avatar-7', label: 'Night Cruiser', icon: '🌙' },
  { id: 'avatar-8', label: 'Chennai Star', icon: '🌟' },
];

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register' | 'admin'
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Login form
  const [loginIdentifier, setLoginIdentifier] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form
  const [regForm, setRegForm] = useState({
    name: '',
    phone: '',
    email: '',
    password: '',
    aadhaar_number: '',
    date_of_birth: '',
    avatar: 'avatar-1',
    gender: 'female',
    home_location: '',
    work_location: ''
  });

  if (!isOpen) return null;

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await authAPI.login({
        phone_or_email: loginIdentifier.trim(),
        password: loginPassword
      });

      if (res.data && res.data.token) {
        sessionStorage.setItem('token', res.data.token);
        sessionStorage.setItem('user', JSON.stringify(res.data.user));
        localStorage.setItem('token', res.data.token); // legacy fallback
        localStorage.setItem('user', JSON.stringify(res.data.user));

        confetti({ particleCount: 60, spread: 70, origin: { y: 0.6 } });
        if (onAuthSuccess) onAuthSuccess(res.data.user);
        onClose();
      }
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Client-side validation checks
    const cleanAadhaar = regForm.aadhaar_number.replace(/\D/g, '');
    if (cleanAadhaar.length !== 12) {
      setError('Aadhaar number must be exactly 12 numeric digits.');
      setLoading(false);
      return;
    }

    if (!regForm.date_of_birth) {
      setError('Please provide your Date of Birth.');
      setLoading(false);
      return;
    }

    try {
      const payload = {
        ...regForm,
        aadhaar_number: cleanAadhaar,
        phone: regForm.phone.trim(),
        email: regForm.email.trim()
      };

      const res = await authAPI.register(payload);
      if (res.data && res.data.user) {
        // Auto-login after registration
        const loginRes = await authAPI.login({
          phone_or_email: payload.email || payload.phone,
          password: payload.password
        });
        
        if (loginRes.data?.token) {
          sessionStorage.setItem('token', loginRes.data.token);
          sessionStorage.setItem('user', JSON.stringify(loginRes.data.user));
          localStorage.setItem('token', loginRes.data.token);
          localStorage.setItem('user', JSON.stringify(loginRes.data.user));

          confetti({ particleCount: 80, spread: 80, origin: { y: 0.6 } });
          if (onAuthSuccess) onAuthSuccess(loginRes.data.user);
          onClose();
        }
      }
    } catch (err) {
      const errList = err.response?.data?.errors;
      if (Array.isArray(errList)) {
        setError(errList.join(' • '));
      } else {
        setError(err.response?.data?.error || err.response?.data?.message || 'Registration failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md overflow-y-auto">
      <div className="glass-modal w-full max-w-lg rounded-3xl overflow-hidden shadow-2xl border border-slate-700/80 my-6">
        
        {/* Modal Header */}
        <div className="p-6 pb-4 text-center border-b border-slate-800 relative bg-slate-900/60">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-emerald-500/20">
            {authMode === 'admin' ? (
              <Shield className="w-6 h-6 text-white" />
            ) : (
              <Sparkles className="w-6 h-6 text-white" />
            )}
          </div>

          <h2 className="text-xl font-extrabold text-white font-outfit">
            {authMode === 'login' && 'Welcome to SmartRide Chennai'}
            {authMode === 'register' && 'Create Commuter Account'}
            {authMode === 'admin' && 'Admin Moderation Portal'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {authMode === 'admin' 
              ? 'Platform moderation, DL verifications & incident triage' 
              : authMode === 'register'
              ? 'Register with 12-digit Aadhaar to start safe bike pooling'
              : 'Sign in to search, request, or offer bike pooling rides'}
          </p>

          {/* Mode Switcher Tabs */}
          <div className="flex bg-slate-950/70 p-1 rounded-xl mt-4 border border-slate-800">
            <button
              type="button"
              onClick={() => { setAuthMode('login'); setError(''); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                authMode === 'login'
                  ? 'bg-slate-800 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => { setAuthMode('register'); setError(''); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                authMode === 'register'
                  ? 'bg-emerald-500 text-slate-950 shadow font-extrabold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Register
            </button>
            <button
              type="button"
              onClick={() => { setAuthMode('admin'); setError(''); }}
              className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                authMode === 'admin'
                  ? 'bg-purple-600 text-white shadow'
                  : 'text-purple-400 hover:text-purple-300'
              }`}
            >
              <Shield className="w-3.5 h-3.5" /> Admin
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 max-h-[75vh] overflow-y-auto custom-scrollbar">
          
          {/* Error Alert */}
          {error && (
            <div className="p-3.5 mb-4 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* LOGIN & ADMIN FORM */}
          {(authMode === 'login' || authMode === 'admin') && (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1.5">
                  {authMode === 'admin' ? 'Admin Email' : 'Email or Phone Number'}
                </label>
                <input
                  type="text"
                  required
                  placeholder={authMode === 'admin' ? 'admin@gmail.com' : 'e.g. yourname@gmail.com / 9840112233'}
                  value={loginIdentifier}
                  onChange={(e) => setLoginIdentifier(e.target.value)}
                  className="w-full bg-slate-900/80 border border-slate-700/80 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none transition-all placeholder:text-slate-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1.5">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    placeholder="Enter your password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    className="w-full bg-slate-900/80 border border-slate-700/80 text-white text-xs rounded-xl p-3 pr-10 focus:border-emerald-500 focus:outline-none transition-all placeholder:text-slate-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className={`w-full py-3 text-white text-xs font-extrabold rounded-xl shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2 ${
                  authMode === 'admin'
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 shadow-purple-600/25'
                    : 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold hover:brightness-110 shadow-emerald-500/20'
                }`}
              >
                {loading ? 'Authenticating...' : authMode === 'admin' ? 'Access Admin Portal' : 'Sign In'}
              </button>
            </form>
          )}

          {/* REGISTER FORM */}
          {authMode === 'register' && (
            <form onSubmit={handleRegisterSubmit} className="space-y-4">
              
              {/* Avatar Selector */}
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1.5">Choose Avatar</label>
                <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
                  {AVATARS.map((av) => (
                    <button
                      key={av.id}
                      type="button"
                      onClick={() => setRegForm({ ...regForm, avatar: av.id })}
                      className={`p-2 rounded-xl flex flex-col items-center gap-0.5 transition-all ${
                        regForm.avatar === av.id
                          ? 'bg-slate-800 border-2 border-emerald-400 shadow-md scale-105'
                          : 'bg-slate-900/60 border border-slate-800 hover:bg-slate-800/80'
                      }`}
                    >
                      <span className="text-lg">{av.icon}</span>
                      <span className="text-[8px] font-semibold text-slate-400 truncate w-full text-center">{av.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Name & Phone */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Full Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Nivetha S"
                    value={regForm.name}
                    onChange={(e) => setRegForm({ ...regForm, name: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Phone Number</label>
                  <input
                    type="tel"
                    required
                    placeholder="e.g. 9840112233"
                    value={regForm.phone}
                    onChange={(e) => setRegForm({ ...regForm, phone: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none font-mono"
                  />
                </div>
              </div>

              {/* Email & Password */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Email Address</label>
                  <input
                    type="email"
                    required
                    placeholder="e.g. niveda@gmail.com"
                    value={regForm.email}
                    onChange={(e) => setRegForm({ ...regForm, email: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Password</label>
                  <input
                    type="password"
                    required
                    placeholder="Min 6 characters"
                    value={regForm.password}
                    onChange={(e) => setRegForm({ ...regForm, password: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Aadhaar Number (12 Digits, Non-editable later) */}
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1 flex items-center justify-between">
                  <span className="flex items-center gap-1.5 text-emerald-400">
                    <ShieldCheck className="w-3.5 h-3.5" /> Aadhaar Card Number (12 Digits)
                  </span>
                  <span className="text-[10px] text-slate-500 font-normal">🔒 Permanent / Non-editable later</span>
                </label>
                <input
                  type="text"
                  required
                  maxLength={12}
                  placeholder="Enter 12-digit Aadhaar (e.g. 548912345678)"
                  value={regForm.aadhaar_number}
                  onChange={(e) => {
                    const numericOnly = e.target.value.replace(/\D/g, '').slice(0, 12);
                    setRegForm({ ...regForm, aadhaar_number: numericOnly });
                  }}
                  className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none font-mono tracking-wider"
                />
                <p className="text-[10px] text-slate-500 mt-1">
                  Required for identity verification and safety across Chennai commute corridors. Cannot be modified later.
                </p>
              </div>

              {/* Date of Birth (DOB, Non-editable later) */}
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1 flex items-center justify-between">
                  <span className="flex items-center gap-1.5 text-amber-400">
                    <Calendar className="w-3.5 h-3.5" /> Date of Birth (DOB)
                  </span>
                  <span className="text-[10px] text-amber-300/80 font-normal">🎂 Birthday Offers Unlocked</span>
                </label>
                <input
                  type="date"
                  required
                  max={new Date().toISOString().split('T')[0]}
                  value={regForm.date_of_birth}
                  onChange={(e) => setRegForm({ ...regForm, date_of_birth: e.target.value })}
                  className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                />
                <p className="text-[10px] text-slate-500 mt-1">
                  Used for birthday special discount perks! Cannot be modified later.
                </p>
              </div>

              {/* Home Area & Work Location */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Home / Pickup Area</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Koyembedu / Tambaram"
                    value={regForm.home_location}
                    onChange={(e) => setRegForm({ ...regForm, home_location: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Work / Office Tech Park</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Tidel Park, Taramani"
                    value={regForm.work_location}
                    onChange={(e) => setRegForm({ ...regForm, work_location: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Gender Selection & Pink Ride Flexibility */}
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">
                  Gender Preference
                </label>
                <select
                  value={regForm.gender}
                  onChange={(e) => setRegForm({ ...regForm, gender: e.target.value })}
                  className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-pink-500 focus:outline-none"
                >
                  <option value="female">Female 🌸 (Can filter/offer Pink Rides when desired)</option>
                  <option value="male">Male 🏍️</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
                {regForm.gender === 'female' ? (
                  <p className="text-[11px] text-pink-300/90 mt-1.5 flex items-start gap-1.5 bg-pink-500/10 p-2 rounded-xl border border-pink-500/20">
                    <span className="shrink-0">🌸</span> 
                    <span>
                      <strong>Pink Mode flexibility:</strong> You can join any regular ride, and choose Pink Mode (women-only pooling) whenever you require.
                    </span>
                  </p>
                ) : (
                  <p className="text-[10px] text-slate-500 mt-1">
                    Select gender for commute preferences and safety badge recommendations.
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-xs rounded-xl shadow-lg hover:brightness-110 transition-all disabled:opacity-50 mt-3"
              >
                {loading ? 'Creating Verified Account...' : 'Complete Registration & Start Commuting'}
              </button>
            </form>
          )}

        </div>

      </div>
    </div>
  );
}
