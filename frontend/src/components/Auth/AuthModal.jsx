import React, { useState } from 'react';
import { authAPI } from '../../api';
import { LogIn, UserPlus, Shield, X, Eye, EyeOff, CheckCircle2, AlertCircle, Sparkles, Key } from 'lucide-react';
import confetti from 'canvas-confetti';

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
    home_location: 'Maduravoyal',
    work_location: 'Olympia Tech Park'
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
        localStorage.setItem('token', res.data.token);
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
    try {
      const res = await authAPI.register(regForm);
      if (res.data && res.data.user) {
        // Auto-login after registration
        const loginRes = await authAPI.login({
          phone_or_email: regForm.email,
          password: regForm.password
        });
        
        if (loginRes.data?.token) {
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
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-modal w-full max-w-md rounded-3xl overflow-hidden shadow-2xl border border-slate-700/80">
        
        {/* Modal Header */}
        <div className="p-6 pb-4 text-center border-b border-slate-800 relative bg-slate-900/50">
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
            {authMode === 'login' && 'Welcome Back'}
            {authMode === 'register' && 'Join SmartRide Chennai'}
            {authMode === 'admin' && 'Admin Portal Login'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {authMode === 'admin' 
              ? 'Platform moderation, DL approvals & ride metrics' 
              : 'Log in to search, request, or offer bike pooling rides'}
          </p>

          {/* Mode Switcher Tabs */}
          <div className="flex bg-slate-950/70 p-1 rounded-xl mt-4 border border-slate-800">
            <button
              onClick={() => { setAuthMode('login'); setError(''); }}
              className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${
                authMode === 'login' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setAuthMode('register'); setError(''); }}
              className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all ${
                authMode === 'register' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              Register
            </button>
            <button
              onClick={() => { setAuthMode('admin'); setError(''); }}
              className={`flex-1 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1 ${
                authMode === 'admin' ? 'bg-purple-600 text-white shadow-md' : 'text-purple-400 hover:text-purple-300'
              }`}
            >
              <Shield className="w-3.5 h-3.5" /> Admin
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto">
          {error && (
            <div className="p-3 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* LOGIN & ADMIN FORM */}
          {(authMode === 'login' || authMode === 'admin') && (
            <form onSubmit={handleLoginSubmit} className="space-y-3.5">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1.5">
                  {authMode === 'admin' ? 'Admin Email' : 'Email or Phone Number'}
                </label>
                <input
                  type="text"
                  required
                  placeholder={authMode === 'admin' ? 'Enter admin email address' : 'e.g. yourname@gmail.com / 9840112233'}
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
            <form onSubmit={handleRegisterSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Arun Kumar"
                  value={regForm.name}
                  onChange={(e) => setRegForm({ ...regForm, name: e.target.value })}
                  className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Phone Number</label>
                  <input
                    type="tel"
                    required
                    placeholder="9840112233"
                    value={regForm.phone}
                    onChange={(e) => setRegForm({ ...regForm, phone: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Email</label>
                  <input
                    type="email"
                    required
                    placeholder="arun@gmail.com"
                    value={regForm.email}
                    onChange={(e) => setRegForm({ ...regForm, email: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  placeholder="Create a strong password"
                  value={regForm.password}
                  onChange={(e) => setRegForm({ ...regForm, password: e.target.value })}
                  className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Home Area</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Maduravoyal"
                    value={regForm.home_location}
                    onChange={(e) => setRegForm({ ...regForm, home_location: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Work / Office</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Olympia Tech Park"
                    value={regForm.work_location}
                    onChange={(e) => setRegForm({ ...regForm, work_location: e.target.value })}
                    className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              {/* Gender Selection for Pink Ride Mode */}
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">
                  Gender <span className="text-pink-400 font-medium">(For Women-Only Pink Rides)</span>
                </label>
                <select
                  value={regForm.gender || 'prefer_not_to_say'}
                  onChange={(e) => setRegForm({ ...regForm, gender: e.target.value })}
                  className="w-full bg-slate-900/80 border border-slate-700 text-white text-xs rounded-xl p-2.5 focus:border-pink-500 focus:outline-none"
                >
                  <option value="female">Female 🌸 (Recommend Women-Only Pink Ride Mode)</option>
                  <option value="male">Male</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
                {regForm.gender === 'female' && (
                  <p className="text-[11px] text-pink-300/90 mt-1 flex items-center gap-1">
                    <span>🌸</span> Women-Only Pink Ride mode enabled! You can offer and book female-only rides.
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-xs rounded-xl shadow-lg hover:brightness-110 transition-all disabled:opacity-50 mt-2"
              >
                {loading ? 'Creating Account...' : 'Register & Start Commuting'}
              </button>
            </form>
          )}

        </div>

      </div>
    </div>
  );
}
