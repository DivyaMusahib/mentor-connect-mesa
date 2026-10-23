import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import {
  Calendar,
  Video,
  FileText,
  FileSpreadsheet,
  Clock,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  MoreVertical,
  X
} from 'lucide-react';

export default function MySessions() {
  const navigate = useNavigate();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [simulatingId, setSimulatingId] = useState(null);
  const [rescheduleModal, setRescheduleModal] = useState(null);
  const [newDate, setNewDate] = useState('');
  const [rescheduleReason, setRescheduleReason] = useState('');
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    loadBookings();
  }, []);

  const loadBookings = async () => {
    setLoading(true);
    try {
      const data = await api.getBookings();
      setBookings(data || []);
    } catch (err) {
      console.error('Failed to load bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateCompletion = async (bookingId) => {
    setSimulatingId(bookingId);
    setFeedback(null);
    try {
      await api.simulateCompleteMeeting(bookingId);
      setFeedback({ type: 'success', text: 'Call completed! AI Post-Call Report generated from transcript.' });
      await loadBookings();
      navigate(`/report?booking_id=${bookingId}`);
    } catch (err) {
      setFeedback({ type: 'error', text: err.message || 'Simulation failed' });
    } finally {
      setSimulatingId(null);
    }
  };

  const handleRescheduleSubmit = async (e) => {
    e.preventDefault();
    if (!rescheduleModal || !newDate) return;
    try {
      const isoDatetime = new Date(newDate).toISOString();
      await api.rescheduleBooking(rescheduleModal.id, isoDatetime, rescheduleReason);
      setRescheduleModal(null);
      setFeedback({ type: 'success', text: 'Session rescheduled successfully!' });
      await loadBookings();
    } catch (err) {
      setFeedback({ type: 'error', text: err.message });
    }
  };

  const handleCancel = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this mentorship session?')) return;
    try {
      await api.cancelBooking(bookingId, 'Student requested cancellation.');
      setFeedback({ type: 'success', text: 'Session cancelled.' });
      await loadBookings();
    } catch (err) {
      setFeedback({ type: 'error', text: err.message });
    }
  };

  const upcomingBookings = bookings.filter((b) => b.status === 'confirmed' || b.status === 'rescheduled');
  const pastBookings = bookings.filter((b) => b.status === 'completed' || b.status === 'cancelled');

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-12 space-y-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-200/80">
        <div className="space-y-1">
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-zinc-900 tracking-tight">
            My Mentorship Sessions
          </h1>
          <p className="text-xs sm:text-sm text-zinc-500">
            Access your Google Meet calls, Pre-Call Briefs, and AI-generated Post-Call Reports.
          </p>
        </div>
      </div>

      {feedback && (
        <div className={`p-4 rounded-2xl text-xs sm:text-sm flex items-center justify-between border ${
          feedback.type === 'success' ? 'bg-emerald-50 text-emerald-900 border-emerald-200' : 'bg-red-50 text-red-900 border-red-200'
        }`}>
          <span>{feedback.text}</span>
          <button onClick={() => setFeedback(null)} className="font-semibold underline ml-2">Dismiss</button>
        </div>
      )}

      {/* Upcoming Sessions Section */}
      <div className="space-y-6">
        <div className="flex items-center space-x-2">
          <Calendar className="w-5 h-5 text-zinc-800" />
          <h2 className="text-lg font-heading font-bold text-zinc-900">
            Upcoming Sessions ({upcomingBookings.length})
          </h2>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-zinc-500">Loading sessions...</div>
        ) : upcomingBookings.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-7">
            {upcomingBookings.map((b) => (
              <div
                key={b.id}
                className="bg-white rounded-3xl border border-zinc-200/90 p-7 shadow-card space-y-6 flex flex-col justify-between"
              >
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <h3 className="font-heading font-bold text-lg text-zinc-900">
                        {b.mentor_name}
                      </h3>
                      <p className="text-xs sm:text-sm text-zinc-600 font-medium">
                        {b.mentor_domain} • {b.mentor_company || 'Industry Leader'}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      b.status === 'rescheduled'
                        ? 'bg-amber-50 text-amber-800 border border-amber-200'
                        : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                    }`}>
                      {b.status === 'rescheduled' ? 'Rescheduled' : 'Confirmed'}
                    </span>
                  </div>

                  <div className="flex items-center space-x-4 text-xs sm:text-sm text-zinc-700 bg-zinc-50/80 p-3.5 rounded-2xl border border-zinc-200/70">
                    <span className="flex items-center space-x-2 font-medium">
                      <Clock className="w-4 h-4 text-zinc-500" />
                      <span>{new Date(b.scheduled_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}</span>
                    </span>
                    <span>•</span>
                    <span>45 Minutes</span>
                  </div>
                </div>

                <div className="space-y-3 pt-3 border-t border-zinc-100">
                  <div className="flex flex-wrap items-center gap-2.5">
                    {b.meet_link && (
                      <a
                        href={b.meet_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs sm:text-sm font-semibold flex items-center space-x-2 transition shadow-sm"
                      >
                        <Video className="w-4 h-4" />
                        <span>Join Meet</span>
                      </a>
                    )}

                    <button
                      onClick={() => navigate(`/preparation?booking_id=${b.id}`)}
                      className="px-4 py-2.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 rounded-xl text-xs sm:text-sm font-semibold flex items-center space-x-1.5 transition"
                    >
                      <FileText className="w-4 h-4 text-zinc-500" />
                      <span>Prep Brief</span>
                    </button>

                    <button
                      onClick={() => setRescheduleModal(b)}
                      className="px-3 py-2 text-zinc-500 hover:text-zinc-900 text-xs font-medium"
                    >
                      Reschedule
                    </button>

                    <button
                      onClick={() => handleCancel(b.id)}
                      className="px-3 py-2 text-red-500 hover:text-red-700 text-xs font-medium"
                    >
                      Cancel
                    </button>
                  </div>

                  {/* Clean Sandbox Action */}
                  <div className="pt-2 flex items-center justify-between text-xs text-zinc-500 border-t border-dashed border-zinc-200">
                    <span className="text-[11px]">Testing & Evaluation:</span>
                    <button
                      onClick={() => handleSimulateCompletion(b.id)}
                      disabled={simulatingId === b.id}
                      className="px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 text-white rounded-lg font-medium text-xs flex items-center space-x-1.5 transition shadow-xs"
                    >
                      <RefreshCw className={`w-3 h-3 ${simulatingId === b.id ? 'animate-spin' : ''}`} />
                      <span>{simulatingId === b.id ? 'Analyzing...' : 'Simulate Call Completion'}</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-12 text-center bg-white rounded-3xl border border-zinc-200/80 p-8 space-y-2">
            <p className="text-sm font-semibold text-zinc-800">No upcoming sessions</p>
            <p className="text-xs text-zinc-500">Book your next mentorship call after taking the AI diagnosis.</p>
          </div>
        )}
      </div>

      {/* Historical Sessions Section */}
      <div className="space-y-6 pt-4 border-t border-zinc-200/80">
        <div className="flex items-center space-x-2">
          <CheckCircle2 className="w-5 h-5 text-zinc-700" />
          <h2 className="text-lg font-heading font-bold text-zinc-900">
            Past & Completed Sessions ({pastBookings.length})
          </h2>
        </div>

        {pastBookings.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-7">
            {pastBookings.map((b) => (
              <div
                key={b.id}
                className="bg-white rounded-3xl border border-zinc-200/90 p-7 shadow-card space-y-5"
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h3 className="font-heading font-bold text-base text-zinc-900">
                      {b.mentor_name}
                    </h3>
                    <p className="text-xs sm:text-sm text-zinc-600 font-medium">
                      {b.mentor_domain}
                    </p>
                    <span className="text-xs text-zinc-600 block pt-0.5">
                      Conducted on {new Date(b.scheduled_at).toLocaleDateString([], { dateStyle: 'medium' })}
                    </span>
                  </div>

                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    b.status === 'completed'
                      ? 'bg-zinc-100 text-zinc-800 border border-zinc-200'
                      : 'bg-red-50 text-red-800 border border-red-200'
                  }`}>
                    {b.status === 'completed' ? 'Completed' : 'Cancelled'}
                  </span>
                </div>

                {b.status === 'completed' && (
                  <div className="pt-3 border-t border-zinc-100 flex items-center space-x-3">
                    <button
                      onClick={() => navigate(`/report?booking_id=${b.id}`)}
                      className="px-4 py-2.5 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl text-xs sm:text-sm font-semibold flex items-center space-x-2 transition shadow-sm"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                      <span>View AI Report</span>
                    </button>
                    <button
                      onClick={() => navigate(`/report?booking_id=${b.id}&view=transcript`)}
                      className="px-4 py-2.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 rounded-xl text-xs sm:text-sm font-semibold flex items-center space-x-1.5 transition"
                    >
                      <FileSpreadsheet className="w-4 h-4 text-zinc-500" />
                      <span>Transcript</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-zinc-600">
            No completed mentorship calls recorded yet.
          </div>
        )}
      </div>

      {/* Reschedule Modal */}
      {rescheduleModal && (
        <div className="fixed inset-0 z-50 bg-zinc-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-zinc-200 shadow-2xl max-w-md w-full p-7 space-y-5 animate-in fade-in duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-100">
              <h3 className="font-heading font-bold text-base text-zinc-900">
                Reschedule Session with {rescheduleModal.mentor_name}
              </h3>
              <button onClick={() => setRescheduleModal(null)} className="p-1 text-zinc-400 hover:text-zinc-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleRescheduleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-zinc-800 mb-1.5">New Date & Time</label>
                <input
                  type="datetime-local"
                  required
                  value={newDate}
                  onChange={(e) => setNewDate(e.target.value)}
                  className="w-full px-3.5 py-2.5 border border-zinc-300 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900"
                />
              </div>

              <div>
                <label className="block font-semibold text-zinc-800 mb-1.5">Reason for Rescheduling</label>
                <input
                  type="text"
                  placeholder="e.g. Prior interview commitment"
                  value={rescheduleReason}
                  onChange={(e) => setRescheduleReason(e.target.value)}
                  className="w-full px-3.5 py-2.5 border border-zinc-300 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-zinc-100">
                <button
                  type="button"
                  onClick={() => setRescheduleModal(null)}
                  className="px-4 py-2 border border-zinc-300 rounded-xl text-zinc-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl font-semibold shadow-sm"
                >
                  Confirm Reschedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
