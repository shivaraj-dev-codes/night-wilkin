import api from './client'

export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (email, password) => api.post('/auth/login/', { email, password }),
  getProfile: () => api.get('/users/profile/'),
  updateProfile: (data) => api.put('/users/profile/', data),
}

export const walkerAPI = {
  startSession: (data) => api.post('/walk-sessions/', data),
  endSession: (sessionId) => api.post(`/walk-sessions/${sessionId}/end_session/`),
  getActiveSessions: () => api.get('/walk-sessions/?is_active=true'),
  getSessions: () => api.get('/walk-sessions/'),
  getSessionDetail: (sessionId) => api.get(`/walk-sessions/${sessionId}/detail/`),
  updateLocation: (data) => api.post('/location-updates/', data),
  batchUpdateLocations: (sessionId, locations) => 
    api.post('/location-updates/batch_update/', { session: sessionId, locations }),
  triggerFakeCall: (data) => api.post('/fake-calls/trigger_fake_call/', data),
  triggerSOS: (data) => api.post('/sos-alerts/', data),
}

export const guardianAPI = {
  getWalkers: () => api.get('/users/my_walkers/'),
  getWalkerSessions: (walkerId) => api.get(`/walk-sessions/?walker=${walkerId}`),
  acknowledgeSOSAlert: (alertId) => api.post(`/sos-alerts/${alertId}/acknowledge/`),
  getSOSAlerts: () => api.get('/sos-alerts/'),
}

export const safetyAPI = {
  getNearbyLocations: (lat, lng, radius = 5) => 
    api.get(`/safe-locations/nearby/?latitude=${lat}&longitude=${lng}&radius=${radius}`),
  getNearbyDangerZones: (lat, lng, radius = 2) => 
    api.get(`/danger-zones/nearby/?latitude=${lat}&longitude=${lng}&radius=${radius}`),
  reportDanger: (data) => api.post('/danger-zones/report_danger/', data),
  addEmergencyContact: (data) => api.post('/emergency-contacts/', data),
  getEmergencyContacts: () => api.get('/emergency-contacts/'),
  deleteEmergencyContact: (contactId) => api.delete(`/emergency-contacts/${contactId}/`),
}
