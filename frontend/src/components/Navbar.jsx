import React, { useState } from 'react';
import { Compass, PlusCircle, LayoutDashboard, Bike, Shield, LogIn, LogOut, User, Bell, ChevronDown } from 'lucide-react';

export default function Navbar({
  currentUser,
  activeTab,
  setActiveTab,
  onOpenAuth,
  onLogout,
  onOpenPostRide,
  unreadNotifications = 0
}) {
  const [userDropdown, setUserDropdown] = useState(false);
  const isAdmin = currentUser?.email?.toLowerCase() === 'admin@gmail.com';

  const handleOfferRideClick = () => {
    if (!currentUser) {
      onOpenAuth();
      return;
    }
    // Check if user has DL verified
    if (!currentUser.license_verified) {
      setActiveTab('bikes');
      return;
    }
    onOpenPostRide();
  };

  return (
    <nav className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/70">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <div 
            onClick={() => setActiveTab('search')}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform">
              <Bike className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-lg text-white font-outfit tracking-tight">SmartRide</span>
                <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/30">
                  Chennai
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-medium">Daily Office Commute Pool</p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-1">
            <button
              onClick={() => setActiveTab('search')}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
                activeTab === 'search'
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Compass className="w-4 h-4" /> Find a Ride
            </button>

            <button
              onClick={handleOfferRideClick}
              className="px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white shadow-md shadow-emerald-600/25 transition-all"
            >
              <PlusCircle className="w-4 h-4" /> Offer a Ride
            </button>

            <button
              onClick={() => {
                if (!currentUser) onOpenAuth();
                else setActiveTab('dashboard');
              }}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all relative ${
                activeTab === 'dashboard'
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" /> Dashboard
              {unreadNotifications > 0 && (
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
              )}
            </button>

            <button
              onClick={() => {
                if (!currentUser) onOpenAuth();
                else setActiveTab('bikes');
              }}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
                activeTab === 'bikes'
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <Bike className="w-4 h-4" /> Bike & DL
            </button>

            {isAdmin && (
              <button
                onClick={() => setActiveTab('admin')}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
                  activeTab === 'admin'
                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30 shadow-sm'
                    : 'text-purple-300 hover:text-purple-200 hover:bg-purple-900/30'
                }`}
              >
                <Shield className="w-4 h-4" /> Admin Portal
              </button>
            )}
          </div>

          {/* User Auth Section */}
          <div className="flex items-center gap-3">
            {currentUser ? (
              <div className="relative">
                <button
                  onClick={() => setUserDropdown(!userDropdown)}
                  className="flex items-center gap-2.5 p-1.5 pl-2.5 rounded-2xl bg-slate-900/80 hover:bg-slate-800/80 border border-slate-700/80 text-left transition-all"
                >
                  <div className="w-8 h-8 rounded-xl bg-emerald-600 font-bold flex items-center justify-center text-white text-xs shadow-md">
                    {currentUser.name ? currentUser.name[0].toUpperCase() : 'U'}
                  </div>
                  <div className="hidden sm:block">
                    <div className="text-xs font-bold text-white leading-tight">{currentUser.name}</div>
                    <div className="text-[10px] text-slate-400">
                      ⭐ {currentUser.rating || 4.9} • {isAdmin ? 'Admin' : 'Commuter'}
                    </div>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {/* Dropdown Menu */}
                {userDropdown && (
                  <div className="absolute right-0 mt-2 w-48 rounded-2xl glass-modal border border-slate-700 shadow-2xl p-1.5 space-y-1 z-50 animate-in fade-in zoom-in-95">
                    <div className="p-2 border-b border-slate-800">
                      <p className="text-xs font-bold text-white">{currentUser.name}</p>
                      <p className="text-[11px] text-slate-400 truncate">{currentUser.email}</p>
                    </div>

                    <button
                      onClick={() => {
                        setActiveTab('dashboard');
                        setUserDropdown(false);
                      }}
                      className="w-full text-left px-3 py-2 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 rounded-xl flex items-center gap-2"
                    >
                      <LayoutDashboard className="w-3.5 h-3.5 text-emerald-400" /> Commute Hub
                    </button>

                    <button
                      onClick={() => {
                        setActiveTab('bikes');
                        setUserDropdown(false);
                      }}
                      className="w-full text-left px-3 py-2 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 rounded-xl flex items-center gap-2"
                    >
                      <Bike className="w-3.5 h-3.5 text-cyan-400" /> Manage Vehicles & DL
                    </button>

                    {isAdmin && (
                      <button
                        onClick={() => {
                          setActiveTab('admin');
                          setUserDropdown(false);
                        }}
                        className="w-full text-left px-3 py-2 text-xs font-semibold text-purple-300 hover:text-purple-200 hover:bg-purple-900/30 rounded-xl flex items-center gap-2"
                      >
                        <Shield className="w-3.5 h-3.5 text-purple-400" /> Admin Approvals
                      </button>
                    )}

                    <div className="border-t border-slate-800 pt-1">
                      <button
                        onClick={() => {
                          setUserDropdown(false);
                          onLogout();
                        }}
                        className="w-full text-left px-3 py-2 text-xs font-semibold text-rose-400 hover:bg-rose-500/15 rounded-xl flex items-center gap-2"
                      >
                        <LogOut className="w-3.5 h-3.5" /> Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={onOpenAuth}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 shadow-md flex items-center gap-1.5 transition-all"
              >
                <LogIn className="w-4 h-4 text-emerald-400" /> Sign In
              </button>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
}
