import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import {
  Sparkles,
  Send,
  Calendar,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Clock,
  ShieldAlert,
  Building,
  Info,
  X,
  ArrowRight,
  RotateCcw
} from 'lucide-react';

export default function AiAdvisor() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const candidateMentorId = searchParams.get('candidate_mentor_id');

  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [bookingModalMentor, setBookingModalMentor] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0]);
  const [slots, setSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [bookingInProgress, setBookingInProgress] = useState(false);
  const [bookingError, setBookingError] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    initChatSession();
  }, [candidateMentorId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const startNewSession = async () => {
    setLoading(true);
    try {
      const data = await api.createChatSession(
        candidateMentorId ? `Fit Assessment: Mentor ${candidateMentorId}` : 'Career Diagnosis Session',
        candidateMentorId
      );
      setSession(data);
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to start chat session:', err);
    } finally {
      setLoading(false);
    }
  };

  const initChatSession = async () => {
    setLoading(true);
    try {
      if (!candidateMentorId) {
        const existingSessions = await api.getChatSessions();
        const active = Array.isArray(existingSessions)
          ? existingSessions.find((s) => s.status !== 'matched' && !s.candidate_mentor_id)
          : null;
        if (active && active.id) {
          const fullSession = await api.getChatSession(active.id);
          setSession(fullSession);
          setMessages(fullSession.messages || []);
          return;
        }
      }
      await startNewSession();
    } catch (err) {
      console.error('Failed to initialize chat:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!inputText.trim() || sending || !session) return;

    const userText = inputText.trim();
    setInputText('');
    setSending(true);

    const tempUserMsg = {
      id: `temp_${Date.now()}`,
      sender: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const updatedSession = await api.sendChatMessage(session.id, userText);
      setSession(updatedSession);
      setMessages(updatedSession.messages || []);
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setSending(false);
    }
  };

  const handleOpenBookingModal = async (mentorMatch) => {
    setBookingModalMentor(mentorMatch);
    setBookingError(null);
    setSelectedSlot(null);
    setLoadingSlots(true);

    try {
      const avail = await api.getAvailability(mentorMatch.mentor_id, selectedDate);
      setSlots(avail.slots || []);
      if (avail.slots && avail.slots.length > 0) {
        setSelectedSlot(avail.slots[0].start_time);
      }
    } catch (err) {
      setBookingError('Unable to load calendar availability.');
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleDateChange = async (newDate) => {
    setSelectedDate(newDate);
    if (!bookingModalMentor) return;
    setLoadingSlots(true);
    setSelectedSlot(null);
    try {
      const avail = await api.getAvailability(bookingModalMentor.mentor_id, newDate);
      setSlots(avail.slots || []);
      if (avail.slots && avail.slots.length > 0) {
        setSelectedSlot(avail.slots[0].start_time);
      }
    } catch (err) {
      setBookingError('Unable to fetch slots for this date.');
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleConfirmBooking = async () => {
    if (!selectedSlot || !bookingModalMentor || !session) return;
    setBookingInProgress(true);
    setBookingError(null);

    try {
      const bookingData = {
        mentor_id: bookingModalMentor.mentor_id,
        diagnostic_id: session.diagnostic_result?.id || null,
        scheduled_at: selectedSlot,
        duration_minutes: 45,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Kolkata',
        idempotency_key: `client_book_${Date.now()}_${bookingModalMentor.mentor_id}`,
      };

      const result = await api.createBooking(bookingData);
      setBookingModalMentor(null);
      navigate(`/preparation?booking_id=${result.id}`);
    } catch (err) {
      setBookingError(err.message || 'Booking creation failed. Please try again.');
    } finally {
      setBookingInProgress(false);
    }
  };

  const getStageBadge = (stage) => {
    switch (stage) {
      case 'matched':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
            <span>Diagnosis Complete • Booking Unlocked</span>
          </span>
        );
      case 'no_exact_match':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-900 border border-amber-200">
            <AlertCircle className="w-3.5 h-3.5 text-amber-700" />
            <span>Logged for Mesa Supply Recruitment</span>
          </span>
        );
      case 'out_of_scope':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-700 border border-zinc-200">
            <ShieldAlert className="w-3.5 h-3.5 text-zinc-600" />
            <span>Out of Scope Challenge</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800 border border-zinc-200">
            <HelpCircle className="w-3.5 h-3.5 text-zinc-600" />
            <span>Clarifying Challenge</span>
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-12 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-zinc-200">
        <div className="space-y-1">
          <div className="flex items-center space-x-3 mb-1">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800 border border-zinc-200">
              AI Diagnostic Advisor
            </span>
            {session && getStageBadge(session.status)}
          </div>
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-zinc-900 tracking-tight">
            Career Problem Diagnosis & Mentor Matching
          </h1>
          <p className="text-xs sm:text-sm text-zinc-500">
            Explain your hurdle to unlock verified mentors matched against our 50-executive catalogue.
          </p>
        </div>
        <button
          onClick={startNewSession}
          disabled={loading || sending}
          className="inline-flex items-center space-x-2 px-4 py-2 border border-zinc-200 rounded-xl text-xs font-semibold text-zinc-700 bg-white hover:bg-zinc-50 shadow-xs transition-colors self-start sm:self-center"
        >
          <RotateCcw className="w-3.5 h-3.5 text-zinc-500" />
          <span>New Diagnosis</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Chat Conversation (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-zinc-200/90 shadow-card flex flex-col h-[700px] overflow-hidden">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 sm:p-7 space-y-5">
            {messages.map((m) => {
              const isAssistant = m.sender === 'assistant';
              return (
                <div
                  key={m.id}
                  className={`flex items-start space-x-3 ${isAssistant ? '' : 'flex-row-reverse space-x-reverse'}`}
                >
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                      isAssistant
                        ? 'bg-zinc-900 text-white shadow-xs'
                        : 'bg-zinc-100 text-zinc-800 border border-zinc-200'
                    }`}
                  >
                    {isAssistant ? <Sparkles className="w-4 h-4 text-emerald-400" /> : 'You'}
                  </div>

                  <div
                    className={`p-4 sm:p-5 rounded-2xl text-xs sm:text-sm leading-relaxed max-w-[85%] ${
                      isAssistant
                        ? 'bg-zinc-50/80 border border-zinc-200/80 text-zinc-800'
                        : 'bg-zinc-900 text-white'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  </div>
                </div>
              );
            })}

            {sending && (
              <div className="flex items-center space-x-3 text-zinc-400 text-xs">
                <div className="w-9 h-9 rounded-xl bg-zinc-900 text-white flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-emerald-400 animate-pulse" />
                </div>
                <div className="p-3.5 bg-zinc-50 rounded-2xl border border-zinc-200 inline-flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce" />
                  <span className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce [animation-delay:0.2s]" />
                  <span className="w-2 h-2 rounded-full bg-zinc-500 animate-bounce [animation-delay:0.4s]" />
                  <span className="text-xs text-zinc-600 font-medium ml-1">Assessing verified mentor catalogue...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-4 sm:p-5 border-t border-zinc-200/80 bg-zinc-50/50">
            <div className="flex items-center space-x-2.5">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Describe your current blocker, goal, or target industry..."
                disabled={sending}
                className="flex-1 px-4 py-3 bg-white border border-zinc-300 hover:border-zinc-400 rounded-2xl text-xs sm:text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-900 shadow-subtle"
              />
              <button
                type="submit"
                disabled={!inputText.trim() || sending}
                className="px-5 py-3 bg-zinc-900 hover:bg-zinc-800 disabled:bg-zinc-300 text-white rounded-2xl text-xs sm:text-sm font-semibold transition flex items-center space-x-1.5 shadow-sm"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Verified Matches (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-3xl border border-zinc-200/90 p-6 sm:p-7 shadow-card space-y-5">
            <div className="flex items-center justify-between pb-4 border-b border-zinc-100">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-emerald-700" />
                <h2 className="text-sm sm:text-base font-heading font-bold text-zinc-900">
                  Verified Mentor Matches
                </h2>
              </div>
              <span className="text-[11px] text-zinc-600 font-medium">50-Mentor Catalogue</span>
            </div>

            {session?.diagnostic_result?.recommended_mentors && session.diagnostic_result.recommended_mentors.length > 0 ? (
              <div className="space-y-4">
                {session.diagnostic_result.recommended_mentors.map((match) => (
                  <div
                    key={match.mentor_id}
                    className="p-5 rounded-2xl border border-zinc-200 bg-zinc-50/50 hover:bg-white hover:border-zinc-300 transition space-y-3.5 shadow-subtle"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-heading font-bold text-base text-zinc-900">
                            {match.mentor_name}
                          </h3>
                          <span className="text-[10px] font-mono text-zinc-500 bg-zinc-200/70 px-2 py-0.5 rounded">
                            {match.mentor_id}
                          </span>
                        </div>
                        <p className="text-xs sm:text-sm text-zinc-600 mt-0.5">
                          {match.domain} • {match.company || 'Confidential'}
                        </p>
                      </div>

                      <div className="text-right">
                        <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200/80">
                          {Math.round(match.fit_score * 100)}% Fit
                        </span>
                      </div>
                    </div>

                    {/* Why matched */}
                    <div className="text-xs text-zinc-700 bg-white p-3.5 rounded-xl border border-zinc-200/70 space-y-1">
                      <p className="font-semibold text-zinc-900 text-[11px] flex items-center space-x-1">
                        <Info className="w-3 h-3 text-zinc-500" />
                        <span>Why this mentor was matched:</span>
                      </p>
                      <p className="leading-relaxed text-zinc-600">{match.why_matched}</p>
                    </div>

                    {/* Booking Action */}
                    <div className="pt-2 flex items-center justify-between border-t border-zinc-200/80">
                      <span className="text-xs text-zinc-500 font-medium">45-Minute Mentorship Call</span>
                      <button
                        onClick={() => handleOpenBookingModal(match)}
                        className="px-4 py-2 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl text-xs font-semibold transition flex items-center space-x-1.5 shadow-sm"
                      >
                        <Calendar className="w-3.5 h-3.5" />
                        <span>Book Session</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-14 text-center text-xs text-zinc-500 space-y-2">
                <p className="font-semibold text-zinc-800 text-sm">No matches unlocked yet</p>
                <p className="max-w-xs mx-auto leading-relaxed">
                  Type your career hurdle in the chat. The advisor diagnoses fit and unlocks verified mentors once your blocker is clarified.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Booking Modal */}
      {bookingModalMentor && (
        <div className="fixed inset-0 z-50 bg-zinc-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-zinc-200 shadow-2xl max-w-lg w-full p-7 space-y-6 animate-in fade-in duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-zinc-100">
              <div>
                <h3 className="font-heading font-bold text-lg text-zinc-900">
                  Book Mentorship Session
                </h3>
                <p className="text-xs text-zinc-500">
                  With {bookingModalMentor.mentor_name} ({bookingModalMentor.mentor_id})
                </p>
              </div>
              <button
                onClick={() => setBookingModalMentor(null)}
                className="p-1.5 text-zinc-400 hover:text-zinc-700 rounded-xl hover:bg-zinc-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {bookingError && (
              <div className="p-3 bg-red-50 text-red-800 border border-red-200 text-xs rounded-xl">
                {bookingError}
              </div>
            )}

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-zinc-800 mb-1.5">Select Session Date</label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => handleDateChange(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-4 py-2.5 border border-zinc-300 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900 focus:outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-zinc-800 mb-1.5">
                  Available Calendar Slots (45 Minutes)
                </label>
                {loadingSlots ? (
                  <div className="py-6 text-center text-zinc-500">Querying calendar availability via n8n...</div>
                ) : slots.length > 0 ? (
                  <div className="grid grid-cols-2 gap-2.5">
                    {slots.map((s) => {
                      const isSel = selectedSlot === s.start_time;
                      return (
                        <button
                          key={s.start_time}
                          type="button"
                          onClick={() => setSelectedSlot(s.start_time)}
                          className={`p-3 rounded-xl border text-center transition font-semibold ${
                            isSel
                              ? 'bg-zinc-900 text-white border-zinc-900'
                              : 'bg-zinc-50 border-zinc-200 text-zinc-800 hover:bg-zinc-100'
                          }`}
                        >
                          {new Date(s.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div className="py-4 text-zinc-500 text-center bg-zinc-50 rounded-xl">
                    No open slots found for this date.
                  </div>
                )}
              </div>

              <div className="p-4 bg-zinc-50 rounded-2xl border border-zinc-200 text-zinc-600 space-y-1">
                <p className="font-semibold text-zinc-900">What happens next:</p>
                <p className="leading-relaxed">
                  n8n creates the Google Calendar event and Google Meet link, and Gemini compiles your Pre-Call Preparation Brief.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-4 border-t border-zinc-100">
              <button
                type="button"
                onClick={() => setBookingModalMentor(null)}
                className="px-5 py-2.5 border border-zinc-300 rounded-xl text-xs font-semibold text-zinc-700 hover:bg-zinc-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmBooking}
                disabled={!selectedSlot || bookingInProgress}
                className="px-6 py-2.5 bg-zinc-900 hover:bg-zinc-800 disabled:bg-zinc-300 text-white rounded-xl text-xs font-semibold transition shadow-sm"
              >
                <span>{bookingInProgress ? 'Orchestrating via n8n...' : 'Confirm & Generate Brief'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
