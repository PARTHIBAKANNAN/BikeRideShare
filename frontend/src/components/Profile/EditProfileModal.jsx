import React, { useState, useEffect } from 'react';
import { 
  X, User, Phone, Mail, MapPin, Briefcase, Calendar, ShieldCheck, 
  Lock, Sparkles, Check, AlertCircle, Cake, Heart 
} from 'lucide-react';
import { authAPI } from '../../api';
import confetti from 'canvas-confetti';

const AVATARS = [
  { id: 'avatar-1', label: 'Urban Rider', icon: '🏍️', bg: 'from-emerald-500 to-teal-500' },
  { id: 'avatar-2', label: 'Tech Pro', icon: '💻', bg: 'from-blue-500 to-cyan-500' },
  { id: 'avatar-3', label: 'Eco Commuter', icon: '🌿', bg: 'from-lime-500 to-emerald-500' },
  { id: 'avatar-4', label: 'IT Executive', icon: '💼', bg: 'from-amber-500 to-orange-500' },
  { id: 'avatar-5', label: 'Pink Champion', icon: '🌸', bg: 'from-pink-500 to-rose-500' },
  { id: 'avatar-6', label: 'Speedster', icon: '⚡', bg: 'from-purple-500 to-indigo-500' },
  { id: 'avatar-7', label: 'Night Cruiser', icon: '🌙', bg: 'from-indigo-500 to-slate-700' },
  { id: 'avatar-8', label: 'Chennai Star', icon: '🌟', bg: 'from-yellow-500 to-amber-600' },
];

export default function EditProfileModal({ isOpen, onClose, currentUser, onProfileUpdated }) {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    avatar: 'avatar-1',
    gender: 'prefer_not_to_say',
    home_location: '',
    work_location: '',
    preferred_departure_time: '08:30'
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    if (currentUser) {
      setFormData({
        name: currentUser.name || '',
        phone: currentUser.phone || '',
        email: currentUser.email || '',
        avatar: currentUser.avatar || 'avatar-1',
        gender: currentUser.gender || 'prefer_not_to_say',
        home_location: currentUser.home_location || '',
        work_location: currentUser.work_location || '',
        preferred_departure_time: currentUser.preferred_departure_time || '08:30'
      });
      setError('');
      setSuccessMsg('');
    }
  }, [currentUser, isOpen]);

  if (!isOpen || !currentUser) return null;

  const currentAvatarObj = AVATARS.find(a => a.id === formData.avatar) || AVATARS[0];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMsg('');

    try {
      const res = await authAPI.updateProfile(formData);
      if (res.data && res.data.user) {
        const updatedUser = res.data.user;
        sessionStorage.setItem('user', JSON.stringify(updatedUser));
        localStorage.setItem('user', JSON.stringify(updatedUser)); // fallback
        setSuccessMsg('Profile updated successfully!');
        confetti({ particleCount: 60, spread: 60, origin: { y: 0.6 } });
        if (onProfileUpdated) {
          onProfileUpdated(updatedUser);
        }
        setTimeout(() => {
          onClose();
        }, 1200);
      }
    } catch (err) {
      const errList = err.response?.data?.errors;
      if (Array.isArray(errList)) {
        setError(errList.join(' • '));
      } else {
        setError(err.response?.data?.error || err.response?.data?.message || 'Failed to update profile.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Format Aadhaar display with mask
  const formatAadhaar = (aadhaar) => {
    if (!aadhaar) return 'Not Provided';
    const clean = String(aadhaar).replace(/\D/g, '');
    if (clean.length === 12) {
      return `XXXX-XXXX-${clean.slice(8)}`;
    }
    return clean;
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="glass-modal w-full max-w-xl rounded-3xl overflow-hidden shadow-2xl border border-slate-700/80 my-8">
        
        {/* Modal Header */}
        <div className="p-6 pb-4 border-b border-slate-800 relative bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950">
          <button
            onClick={onClose}
            className="absolute top-5 right-5 p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-2xl bg-gradient-to-tr ${currentAvatarObj.bg} flex items-center justify-center text-2xl shadow-lg`}>
              {currentAvatarObj.icon}
            </div>
            <div>
              <h2 className="text-lg font-bold text-white font-outfit flex items-center gap-2">
                Edit Commuter Profile
                {currentUser.is_birthday_today && (
                  <span className="text-xs bg-amber-500/20 text-amber-300 border border-amber-500/40 px-2 py-0.5 rounded-full flex items-center gap-1 font-sans">
                    <Cake className="w-3 h-3 text-amber-400" /> Birthday Today!
                  </span>
                )}
              </h2>
              <p className="text-xs text-slate-400">Manage your persona, contact details, and commute corridors</p>
            </div>
          </div>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5 max-h-[78vh] overflow-y-auto custom-scrollbar">
          
          {/* Alerts */}
          {error && (
            <div className="p-3.5 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3.5 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <Check className="w-4 h-4 shrink-0 text-emerald-400" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Birthday Banner if applicable */}
          {currentUser.is_birthday_today && (
            <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/20 via-pink-500/20 to-purple-500/20 border border-amber-500/30 text-amber-200 text-xs flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/30 flex items-center justify-center text-xl shrink-0">
                🎂
              </div>
              <div>
                <p className="font-bold text-white">🎉 Happy Birthday, {currentUser.name}!</p>
                <p className="text-[11px] text-amber-200/80">You've unlocked a 50% discount bonus on all Chennai bike ride pooling today!</p>
              </div>
            </div>
          )}

          {/* Avatar Selection Picker */}
          <div>
            <label className="block text-xs font-bold text-slate-300 mb-2">
              Choose Avatar Persona
            </label>
            <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
              {AVATARS.map((av) => (
                <button
                  key={av.id}
                  type="button"
                  onClick={() => setFormData({ ...formData, avatar: av.id })}
                  className={`p-2.5 rounded-2xl flex flex-col items-center gap-1 transition-all ${
                    formData.avatar === av.id
                      ? 'bg-slate-800 border-2 border-emerald-400 shadow-lg shadow-emerald-500/20 scale-105'
                      : 'bg-slate-900/60 border border-slate-800 hover:bg-slate-800/80'
                  }`}
                >
                  <span className="text-xl">{av.icon}</span>
                  <span className="text-[9px] font-semibold text-slate-400 truncate w-full text-center">{av.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Core Info Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-emerald-400" /> Full Name
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700/80 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Phone className="w-3.5 h-3.5 text-emerald-400" /> Phone Number
              </label>
              <input
                type="tel"
                required
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700/80 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-emerald-400" /> Email Address
              </label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700/80 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Heart className="w-3.5 h-3.5 text-pink-400" /> Gender Preference
              </label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700/80 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
              >
                <option value="female">Female 🌸 (Can offer & filter Pink Rides)</option>
                <option value="male">Male 🏍️</option>
                <option value="other">Other</option>
                <option value="prefer_not_to_say">Prefer not to say</option>
              </select>
            </div>
          </div>

          {/* Commute Corridors */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2 border-t border-slate-800/80">
            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-emerald-400" /> Home / Pickup Area
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Koyembedu / Tambaram / Anna Nagar"
                value={formData.home_location}
                onChange={(e) => setFormData({ ...formData, home_location: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700/80 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5 text-emerald-400" /> Work / Office Tech Park
              </label>
              <input
                type="text"
                required
                placeholder="e.g. DLF Cybercity / Tidel Park / OMR"
                value={formData.work_location}
                onChange={(e) => setFormData({ ...formData, work_location: e.target.value })}
                className="w-full bg-slate-900/80 border border-slate-700/80 text-white text-xs rounded-xl p-3 focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Non-Editable Identity Cards */}
          <div className="pt-2 border-t border-slate-800/80 space-y-2.5">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
              Verified Government Identity & DOB (Non-Editable)
            </span>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {/* Aadhaar Card (Locked) */}
              <div className="p-3.5 rounded-2xl bg-slate-900/50 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block font-medium">Aadhaar Card</span>
                    <span className="text-xs font-mono font-bold text-slate-200">
                      {formatAadhaar(currentUser.aadhaar_number)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-[10px] font-semibold text-slate-500 bg-slate-800/60 px-2 py-1 rounded-lg">
                  <Lock className="w-3 h-3" /> Locked
                </div>
              </div>

              {/* DOB (Locked) */}
              <div className="p-3.5 rounded-2xl bg-slate-900/50 border border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
                    <Calendar className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block font-medium">Date of Birth</span>
                    <span className="text-xs font-mono font-bold text-slate-200">
                      {currentUser.date_of_birth || 'Not Recorded'}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1 text-[10px] font-semibold text-slate-500 bg-slate-800/60 px-2 py-1 rounded-lg">
                  <Lock className="w-3 h-3" /> Locked
                </div>
              </div>
            </div>
            <p className="text-[10px] text-slate-500">
              * Government identity numbers and date of birth are permanently bound to your account for commuter safety and cannot be altered.
            </p>
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:brightness-110 text-slate-950 text-xs font-extrabold shadow-lg shadow-emerald-500/20 disabled:opacity-50 transition-all flex items-center gap-2"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              ) : (
                <Check className="w-4 h-4" />
              )}
              <span>Save Profile Changes</span>
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}
