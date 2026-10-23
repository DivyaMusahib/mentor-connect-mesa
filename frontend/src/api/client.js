/**
 * API Client for Mentor Connect.
 * Uses native fetch with credentials: 'include' for HttpOnly session cookies.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '') + '/api/v1';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const config = {
    ...options,
    headers,
    credentials: 'include', // Important for session cookies
  };

  if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
  }

  const response = await fetch(url, config);

  if (response.status === 401) {
    // Session expired or unauthenticated
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(errorData.detail || 'Authentication required');
    error.status = 401;
    throw error;
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(errorData.detail || `Request failed with status ${response.status}`);
    error.status = response.status;
    error.data = errorData;
    throw error;
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  // Auth
  getMe: () => request('/auth/me'),
  logout: () => request('/auth/logout', { method: 'POST' }),
  demoLogin: (role = 'student', name = null, email = null) =>
    request('/auth/demo', {
      method: 'POST',
      body: { role, full_name: name, email },
    }),

  // Mentors
  getMentors: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val) query.append(key, val);
    });
    const qs = query.toString();
    return request(`/mentors${qs ? `?${qs}` : ''}`);
  },
  getMentor: (id) => request(`/mentors/${id}`),

  // Chat & Diagnostic
  createChatSession: (title, candidateMentorId = null) =>
    request('/chat/sessions', {
      method: 'POST',
      body: { title, candidate_mentor_id: candidateMentorId },
    }),
  getChatSessions: () => request('/chat/sessions'),
  getChatSession: (id) => request(`/chat/sessions/${id}`),
  sendChatMessage: (sessionId, content) =>
    request(`/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: { content },
    }),

  // Bookings & Availability
  getBookings: () => request('/bookings'),
  getBooking: (id) => request(`/bookings/${id}`),
  getAvailability: (mentorId, date, timezone = null) => {
    const tz = timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata';
    return request(`/bookings/availability/${mentorId}?date=${date}&timezone=${encodeURIComponent(tz)}`);
  },
  createBooking: (data) =>
    request('/bookings', {
      method: 'POST',
      body: data,
    }),
  rescheduleBooking: (id, newScheduledAt, reason = null) =>
    request(`/bookings/${id}/reschedule`, {
      method: 'PATCH',
      body: { new_scheduled_at: newScheduledAt, reason },
    }),
  cancelBooking: (id, reason = null) =>
    request(`/bookings/${id}/cancel`, {
      method: 'POST',
      body: { reason },
    }),
  getBookingBrief: (id) => request(`/bookings/${id}/brief`),

  // Transcripts & Reports
  getBookingTranscript: (id) => request(`/bookings/${id}/transcript`),
  getBookingReport: (id) => request(`/bookings/${id}/report`),
  getActionItems: () => request('/action-items'),
  updateActionItem: (id, data) =>
    request(`/action-items/${id}`, {
      method: 'PATCH',
      body: data,
    }),

  // Career
  getCareerRoadmap: () => request('/career/roadmap'),
  updateCareerGoal: (data) =>
    request('/career/roadmap/goal', {
      method: 'PATCH',
      body: data,
    }),
  updateRoadmapStep: (id, data) =>
    request(`/career/roadmap/steps/${id}`, {
      method: 'PATCH',
      body: data,
    }),
  getCareerTimeline: () => request('/career/timeline'),

  // Integrations & Admin
  getIntegrationHealth: () => request('/integrations/health'),
  getAdminOverview: () => request('/admin/overview'),
  getSupplyGaps: () => request('/admin/supply-gaps'),
  getEmailLogs: () => request('/admin/email-logs'),
  getAutomationEvents: () => request('/admin/automation-events'),
  retryAutomation: (eventId) =>
    request(`/admin/retry-automation/${eventId}`, { method: 'POST' }),

  // Demo Simulation
  seedDemo: () => request('/demo/seed', { method: 'POST' }),
  simulateCompleteMeeting: (bookingId) =>
    request(`/demo/simulate/complete-meeting/${bookingId}`, { method: 'POST' }),
  simulateRescheduleConflict: (bookingId) =>
    request(`/demo/simulate/reschedule-conflict/${bookingId}`, { method: 'POST' }),
  simulateTranscriptionFailure: (bookingId) =>
    request(`/demo/simulate/transcription-failure/${bookingId}`, { method: 'POST' }),
  resetDemo: () => request('/demo/reset', { method: 'POST' }),
};
