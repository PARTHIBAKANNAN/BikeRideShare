import axios from 'axios';

// Use backend base URL from env or fallback to localhost:5000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token automatically from sessionStorage
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token') || localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Auth API Methods
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  getProfile: () => api.get('/api/auth/profile'),
  updateProfile: (data) => api.put('/api/auth/profile/update', data),
  submitLicense: (data) => api.post('/api/auth/license/submit', data),
  getVerificationStatus: () => api.get('/api/auth/verification-status'),
};

// Ride API Methods
export const rideAPI = {
  searchRides: (criteria) => api.post('/api/rides/search', criteria),
  postRide: (rideData) => api.post('/api/rides/post', rideData),
  getRoutePreview: (params) => api.post('/api/rides/route-preview', params),
  getChennaiLocations: (q = '') => api.get(`/api/rides/chennai-locations?q=${encodeURIComponent(q)}`),
  reverseGeocode: (lat, lng) => api.get(`/api/rides/reverse-geocode?lat=${lat}&lng=${lng}`),
  getMyRides: (type = 'all') => api.get(`/api/rides/my-rides?type=${type}`),
  getRideDetails: (rideId) => api.get(`/api/rides/${rideId}`),
  joinRide: (rideId, data) => api.post(`/api/rides/${rideId}/join`, data),
  getRideRequests: (rideId) => api.get(`/api/rides/${rideId}/requests`),
  respondToRequest: (requestId, response) => api.post(`/api/rides/requests/${requestId}/respond`, { response }),
  cancelRide: (rideId, reason) => api.post(`/api/rides/${rideId}/cancel`, { reason }),
  getPopularRoutes: () => api.get('/api/rides/popular-routes'),
  getMyRequests: () => api.get('/api/rides/my-requests'),
  verifyRideOtp: (requestId, otp) => api.post(`/api/rides/requests/${requestId}/verify-otp`, { otp }),
  rateRide: (requestId, data) => api.post(`/api/rides/requests/${requestId}/rate`, data),
  getAutoPoolMatches: (routine) => api.post('/api/rides/auto-pool-match', routine),
  getGreenLeaderboard: () => api.get('/api/rides/green-leaderboard'),
  reportIncident: (data) => api.post('/api/rides/report', data),
};

// Bike API Methods
export const bikeAPI = {
  getMyBikes: () => api.get('/api/bikes/'),
  registerBike: (bikeData) => api.post('/api/bikes/register', bikeData),
  updateBike: (bikeId, bikeData) => api.put(`/api/bikes/${bikeId}`, bikeData),
  setActiveBike: (bikeId) => api.post('/api/bikes/set-active', { bike_id: bikeId }),
  deactivateBike: (bikeId) => api.post('/api/bikes/deactivate', { bike_id: bikeId }),
};

// Dashboard API Methods
export const dashboardAPI = {
  getOverview: () => api.get('/api/dashboard/overview'),
  getQuickStats: () => api.get('/api/dashboard/quick-stats'),
  getNotifications: () => api.get('/api/notifications'),
  markNotificationRead: (id) => api.post(`/api/notifications/${id}/read`),
};

// Admin API Methods (for admin@gmail.com)
export const adminAPI = {
  checkAccess: () => api.get('/api/admin/check-access'),
  getDashboard: () => api.get('/api/admin/dashboard'),
  getPlatformStats: () => api.get('/api/admin/platform-stats'),
  getLicenseVerifications: () => api.get('/api/admin/license-verifications'),
  verifyLicense: (userId, action, rejectionReason = '') => 
    api.post('/api/admin/license-verifications/verify', { user_id: userId, action, rejection_reason: rejectionReason }),
  getBikeVerifications: () => api.get('/api/admin/bike-verifications'),
  verifyBike: (bikeId, action, rejectionReason = '') => 
    api.post('/api/admin/bike-verifications/verify', { bike_id: bikeId, action, rejection_reason: rejectionReason }),
  getUsers: (params) => api.get('/api/admin/users', { params }),
  flagUser: (userId, reason) => api.post('/api/admin/users/flag', { user_id: userId, reason }),
  unflagUser: (userId) => api.post('/api/admin/users/unflag', { user_id: userId }),
  getAllRides: (params) => api.get('/api/admin/rides', { params }),
  
  // Incident Reports & Blacklisting
  getIncidentReports: (status) => api.get('/api/admin/incident-reports', { params: { status } }),
  actionIncidentReport: (reportId, action, notes) => 
    api.post(`/api/admin/incident-reports/${reportId}/action`, { action, notes }),
  getBikesDirectory: () => api.get('/api/admin/bikes-directory'),
  blacklistUser: (userId, reason) => api.post(`/api/admin/users/${userId}/blacklist`, { reason }),
  unblacklistUser: (userId) => api.post(`/api/admin/users/${userId}/unblacklist`),
  blacklistBike: (bikeId, reason) => api.post(`/api/admin/bikes/${bikeId}/blacklist`, { reason }),
};

export const systemAPI = {
  getStatus: () => api.get('/api/status'),
};

export default api;
