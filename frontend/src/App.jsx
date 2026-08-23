import React, { useState, useEffect } from 'react';
import { authAPI } from './api';
import Navbar from './components/Navbar';
import RideSearch from './components/Rides/RideSearch';
import CommuteDashboard from './components/Dashboard/CommuteDashboard';
import BikeManager from './components/Dashboard/BikeManager';
import AdminPortal from './components/Admin/AdminPortal';
import AuthModal from './components/Auth/AuthModal';
import PostRideModal from './components/Rides/PostRideModal';
import EditProfileModal from './components/Profile/EditProfileModal';
import { Bike, Shield, Heart, Sparkles, Mail, Cake, Gift } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('search'); // search | dashboard | bikes | admin
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isPostRideOpen, setIsPostRideOpen] = useState(false);
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Read from sessionStorage first (fallback to localStorage)
    const savedUser = sessionStorage.getItem('user') || localStorage.getItem('user');
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    if (savedUser && token) {
      try {
        const parsed = JSON.parse(savedUser);
        setCurrentUser(parsed);
        // Sync to sessionStorage
        sessionStorage.setItem('token', token);
        sessionStorage.setItem('user', JSON.stringify(parsed));

        // Verify with backend
        authAPI.getProfile().then((res) => {
          if (res.data && res.data.user) {
            setCurrentUser(res.data.user);
            sessionStorage.setItem('user', JSON.stringify(res.data.user));
            if (res.data.user.is_birthday_today) {
              confetti({ particleCount: 70, spread: 80, origin: { y: 0.3 } });
            }
          }
        }).catch(() => {
          // Token expired
        });
      } catch (e) {
        console.error(e);
      }
    }
    setLoading(false);
  }, []);

  const handleLogout = () => {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setCurrentUser(null);
    setActiveTab('search');
  };

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
    if (user?.is_birthday_today) {
      confetti({ particleCount: 80, spread: 90, origin: { y: 0.4 } });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-emerald-500 selection:text-white">
      
      {/* Top Navbar */}
      <Navbar
        currentUser={currentUser}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenPostRide={() => setIsPostRideOpen(true)}
        onOpenEditProfile={() => setIsEditProfileOpen(true)}
        onLogout={handleLogout}
      />

      {/* Birthday Celebration Banner if user's birthday is today */}
      {currentUser?.is_birthday_today && (
        <div className="bg-gradient-to-r from-amber-500/20 via-pink-500/20 to-purple-500/20 border-b border-amber-500/30 py-2.5 px-4 text-center">
          <div className="max-w-7xl mx-auto flex items-center justify-center gap-2.5 text-xs text-amber-200">
            <Cake className="w-4 h-4 text-amber-400 animate-bounce" />
            <span>
              <strong>🎉 Happy Birthday, {currentUser.name}!</strong> Special Birthday Commute Offer Activated: Enjoy <strong className="text-white font-bold underline decoration-amber-400">50% OFF</strong> on all rides today!
            </span>
            <Gift className="w-4 h-4 text-pink-400" />
          </div>
        </div>
      )}

      {/* Main Container View */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-12">
        {activeTab === 'search' && (
          <RideSearch
            currentUser={currentUser}
            onOpenAuth={() => setIsAuthOpen(true)}
            onOpenPostRide={() => setIsPostRideOpen(true)}
          />
        )}

        {activeTab === 'dashboard' && (
          <CommuteDashboard
            currentUser={currentUser}
            onOpenPostRide={() => setIsPostRideOpen(true)}
          />
        )}

        {activeTab === 'bikes' && (
          <BikeManager
            currentUser={currentUser}
            onProfileUpdated={() => {
              authAPI.getProfile().then(res => {
                if (res.data?.user) setCurrentUser(res.data.user);
              });
            }}
          />
        )}

        {activeTab === 'admin' && (
          <AdminPortal />
        )}
      </main>

      {/* Footer with Ownership, Copyright & Contact */}
      <footer className="border-t border-slate-800/80 bg-slate-950/90 py-8 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 space-y-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white font-bold">
                <Bike className="w-4 h-4" />
              </div>
              <div className="text-left">
                <span className="font-extrabold text-white font-outfit text-sm">SmartRide Chennai</span>
                <p className="text-[11px] text-slate-500">AI & Road Corridor Commuter Pooling Platform</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Powered by OpenStreetMap & Gemini AI
              </span>
              <span>•</span>
              <span>Neon PostgreSQL</span>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/60 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px]">
            <div className="text-slate-400 text-center sm:text-left">
              <span>© {new Date().getFullYear()} </span>
              <strong className="text-slate-200 tracking-wide">PARTHIBAKANNAN S</strong>
              <span>. All Rights Reserved.</span>
              <span className="block text-[10px] text-slate-500 mt-0.5">
                Designed, Engineered & Owned by <strong className="text-emerald-400">PARTHIBAKANNAN S</strong>
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-slate-500 text-[10px] uppercase font-bold">Inquiries & Support:</span>
              <a
                href="mailto:parthisivaram45@gmail.com"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 hover:border-emerald-500/50 text-slate-200 hover:text-emerald-300 font-mono text-xs transition-colors"
              >
                <Mail className="w-3.5 h-3.5 text-emerald-400" />
                <span>parthisivaram45@gmail.com</span>
              </a>
            </div>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* Post Ride Modal */}
      <PostRideModal
        isOpen={isPostRideOpen}
        onClose={() => setIsPostRideOpen(false)}
        currentUser={currentUser}
        onRidePosted={() => {
          setActiveTab('search');
        }}
      />

      {/* Edit Profile Modal */}
      <EditProfileModal
        isOpen={isEditProfileOpen}
        onClose={() => setIsEditProfileOpen(false)}
        currentUser={currentUser}
        onProfileUpdated={(updatedUser) => {
          setCurrentUser(updatedUser);
        }}
      />

    </div>
  );
}
