import React, { useState, useEffect } from 'react';
import { authAPI } from './api';
import Navbar from './components/Navbar';
import RideSearch from './components/Rides/RideSearch';
import CommuteDashboard from './components/Dashboard/CommuteDashboard';
import BikeManager from './components/Dashboard/BikeManager';
import AdminPortal from './components/Admin/AdminPortal';
import AuthModal from './components/Auth/AuthModal';
import PostRideModal from './components/Rides/PostRideModal';
import { Bike, Shield, Heart, Sparkles } from 'lucide-react';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('search'); // search | dashboard | bikes | admin
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isPostRideOpen, setIsPostRideOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    if (savedUser && token) {
      try {
        setCurrentUser(JSON.parse(savedUser));
        // Verify with backend
        authAPI.getProfile().then((res) => {
          if (res.data && res.data.user) {
            setCurrentUser(res.data.user);
            localStorage.setItem('user', JSON.stringify(res.data.user));
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
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setCurrentUser(null);
    setActiveTab('search');
  };

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
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
        onLogout={handleLogout}
      />

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

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-300 font-outfit">SmartRide Chennai</span>
            <span>•</span>
            <span>AI & Road Corridor Commuter Pooling</span>
          </div>

          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-emerald-400" /> Powered by OpenStreetMap & Gemini AI
            </span>
            <span>•</span>
            <span>Neon PostgreSQL</span>
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

    </div>
  );
}
