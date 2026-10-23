import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import {
  FileText,
  Sparkles,
  CheckCircle2,
  Calendar,
  Clock,
  Quote,
  ChevronDown,
  ChevronUp,
  FileSpreadsheet,
  CheckSquare,
  Square,
  ArrowRight,
  Award
} from 'lucide-react';

export default function PostCallReportView() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const bookingId = searchParams.get('booking_id');
  const initialView = searchParams.get('view') || 'report';

  const [bookings, setBookings] = useState([]);
  const [selectedBookingId, setSelectedBookingId] = useState(bookingId || '');
  const [activeTab, setActiveTab] = useState(initialView);
  const [report, setReport] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [expandedInsight, setExpandedInsight] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (selectedBookingId) {
      loadReportAndTranscript(selectedBookingId);
    }
  }, [selectedBookingId]);

  const loadSessions = async () => {
    try {
      const all = await api.getBookings();
      const completed = all.filter((b) => b.status === 'completed');
      setBookings(completed);
      if (!selectedBookingId && completed.length > 0) {
        setSelectedBookingId(completed[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadReportAndTranscript = async (bId) => {
    setLoading(true);
    setError(null);
    try {
      const [repData, trData] = await Promise.all([
        api.getBookingReport(bId).catch(() => null),
        api.getBookingTranscript(bId).catch(() => null),
      ]);
      setReport(repData);
      setTranscript(trData);
      if (!repData) {
        setError('Report not yet generated for this session.');
      }
    } catch (err) {
      setError(err.message || 'Failed to load report.');
    } finally {
      setLoading(false);
    }
  };

  const toggleInsight = (idx) => {
    setExpandedInsight((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const handleToggleActionItem = async (itemId, currentCompleted) => {
    try {
      await api.updateActionItem(itemId, { is_completed: !currentCompleted });
      if (selectedBookingId) {
        loadReportAndTranscript(selectedBookingId);
      }
    } catch (err) {
      console.error('Failed to update action item:', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 lg:px-10 py-12 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-6 border-b border-zinc-200/80">
        <div className="space-y-1">
          <div className="flex items-center space-x-3 mb-1">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800 border border-zinc-200">
              Post-Call Intelligence
            </span>
            <span className="text-xs text-zinc-600 font-medium">Evidence-Linked Analysis</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-zinc-900 tracking-tight">
            Mentorship Report & Decisions
          </h1>
          <p className="text-xs sm:text-sm text-zinc-600">
            Analysis generated directly from call transcripts with verbatim quote citations.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {bookings.length > 1 && (
            <select
              value={selectedBookingId}
              onChange={(e) => setSelectedBookingId(e.target.value)}
              className="px-3.5 py-2 bg-white border border-zinc-300 rounded-xl text-xs font-semibold text-zinc-800 focus:ring-2 focus:ring-zinc-900"
            >
              {bookings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.mentor_name} ({new Date(b.scheduled_at).toLocaleDateString([], { month: 'short', day: 'numeric' })})
                </option>
              ))}
            </select>
          )}

          {/* Toggle Tab */}
          <div className="flex items-center bg-zinc-100 p-1 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setActiveTab('report')}
              className={`px-3.5 py-2 rounded-lg transition ${
                activeTab === 'report' ? 'bg-white text-zinc-900 shadow-xs' : 'text-zinc-600 hover:text-zinc-900'
              }`}
            >
              Structured Report
            </button>
            <button
              onClick={() => setActiveTab('transcript')}
              className={`px-3.5 py-2 rounded-lg transition ${
                activeTab === 'transcript' ? 'bg-white text-zinc-900 shadow-xs' : 'text-zinc-600 hover:text-zinc-900'
              }`}
            >
              Full Transcript
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-zinc-500 text-sm">
          Loading post-call analysis...
        </div>
      ) : error ? (
        <div className="p-10 text-center bg-white rounded-3xl border border-zinc-200/90 space-y-4">
          <p className="text-base font-semibold text-zinc-900">{error}</p>
          <p className="text-xs sm:text-sm text-zinc-500 max-w-sm mx-auto leading-relaxed">
            You can complete a simulated call on the "My Sessions" page to test the AI report extraction immediately.
          </p>
          <button
            onClick={() => navigate('/sessions')}
            className="px-5 py-2.5 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl text-xs font-semibold"
          >
            Go to My Sessions
          </button>
        </div>
      ) : activeTab === 'report' && report ? (
        <div className="space-y-8">
          {/* Executive Summary */}
          <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-4">
            <h2 className="text-base font-heading font-bold text-zinc-900 flex items-center space-x-2">
              <FileText className="w-4 h-4 text-zinc-700" />
              <span>Discussion Summary</span>
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {report.summary_points?.map((pt, idx) => (
                <div key={idx} className="p-4 bg-zinc-50/70 rounded-2xl border border-zinc-200/80 text-xs sm:text-sm text-zinc-700 leading-relaxed">
                  {pt}
                </div>
              ))}
            </div>
          </div>

          {/* Key Insights & Evidence */}
          <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-100">
              <div>
                <h2 className="text-base font-heading font-bold text-zinc-900 flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-emerald-700" />
                  <span>Key Decisions Grounded in Transcript</span>
                </h2>
                <span className="text-xs text-zinc-600">
                  Expand each insight to view supporting verbatim quotes and timestamps.
                </span>
              </div>
            </div>

            <div className="space-y-4">
              {report.key_insights?.map((item, idx) => {
                const isExpanded = expandedInsight[idx] ?? true;
                const evidence = item.evidence;
                return (
                  <div
                    key={idx}
                    className="p-5 rounded-2xl border border-zinc-200/90 bg-zinc-50/50 hover:bg-white transition space-y-3"
                  >
                    <div
                      onClick={() => toggleInsight(idx)}
                      className="flex items-start justify-between cursor-pointer"
                    >
                      <div className="flex items-start space-x-3">
                        <span className="w-6 h-6 rounded-lg bg-zinc-900 text-white font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <p className="text-sm sm:text-base font-semibold text-zinc-900 leading-snug">
                          {item.insight}
                        </p>
                      </div>
                      <button className="text-zinc-400 hover:text-zinc-700 p-1">
                        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                      </button>
                    </div>

                    {isExpanded && evidence && (
                      <div className="mt-3 pl-9 space-y-2.5 border-t border-zinc-200/80 pt-3">
                        <div className="p-4 bg-white rounded-xl border border-zinc-200 text-xs text-zinc-800 space-y-2 shadow-subtle">
                          <div className="flex items-center justify-between text-[11px] font-semibold text-zinc-900">
                            <span className="flex items-center space-x-1.5">
                              <Quote className="w-3.5 h-3.5 text-zinc-500" />
                              <span>Transcript Citation ({evidence.speaker || 'Mentor'}):</span>
                            </span>
                            <span className="text-[10px] font-mono text-zinc-600 bg-zinc-100 px-2 py-0.5 rounded border border-zinc-200">
                              @{Math.floor(evidence.timestamp_seconds / 60)}m {evidence.timestamp_seconds % 60}s
                            </span>
                          </div>
                          <p className="italic text-zinc-700 leading-relaxed font-serif">"{evidence.quote}"</p>
                          {evidence.relevance_note && (
                            <p className="text-[11px] text-zinc-600 pt-1.5 border-t border-zinc-100">
                              <span className="font-semibold text-zinc-700">Strategic Rationale:</span> {evidence.relevance_note}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Items Checklist */}
          <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-100">
              <h2 className="text-base font-heading font-bold text-zinc-900 flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                <span>Action Items & Deliverables</span>
              </h2>
              <span className="text-xs text-zinc-600 font-medium">Synced with Career Roadmap</span>
            </div>

            <div className="space-y-3.5">
              {report.action_items?.map((ai) => (
                <div
                  key={ai.id}
                  className={`flex items-start space-x-3.5 p-4 rounded-2xl border transition ${
                    ai.is_completed ? 'bg-zinc-50/60 border-zinc-200 text-zinc-400' : 'bg-white border-zinc-200/90 shadow-subtle'
                  }`}
                >
                  <button
                    onClick={() => handleToggleActionItem(ai.id, ai.is_completed)}
                    className="mt-0.5 text-zinc-400 hover:text-zinc-900 transition"
                  >
                    {ai.is_completed ? (
                      <CheckSquare className="w-5 h-5 text-emerald-700" />
                    ) : (
                      <Square className="w-5 h-5 text-zinc-300 hover:text-zinc-500" />
                    )}
                  </button>

                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <p className={`text-xs sm:text-sm font-semibold ${ai.is_completed ? 'line-through text-zinc-600' : 'text-zinc-900'}`}>
                        {ai.title}
                      </p>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        ai.priority === 'high' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-zinc-100 text-zinc-700'
                      }`}>
                        {ai.priority}
                      </span>
                    </div>
                    <p className="text-xs text-zinc-600 leading-relaxed">{ai.description}</p>
                    {ai.deliverable && (
                      <p className="text-[11px] text-zinc-600 font-mono pt-0.5">
                        Deliverable: {ai.deliverable}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Next Milestone */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 shadow-card space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Skills & Artifacts to Polish
              </h3>
              <ul className="list-disc list-inside space-y-2 text-xs sm:text-sm text-zinc-700 leading-relaxed">
                {report.what_to_work_on?.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>

            <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 shadow-card space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-emerald-800 flex items-center space-x-1.5">
                <Award className="w-4 h-4 text-emerald-700" />
                <span>Next Milestone Target</span>
              </h3>
              <p className="text-sm sm:text-base font-semibold text-zinc-900 leading-relaxed">
                {report.next_milestone}
              </p>
            </div>
          </div>
        </div>
      ) : activeTab === 'transcript' && transcript ? (
        /* Full Transcript View */
        <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-5">
          <div className="flex items-center justify-between pb-4 border-b border-zinc-100">
            <div>
              <h2 className="text-base font-heading font-bold text-zinc-900">
                Verbatim Transcript ({Math.round(transcript.duration_seconds / 60)} Mins • {transcript.word_count} Words)
              </h2>
              <span className="text-xs text-zinc-600 font-medium">Provider: {transcript.provider}</span>
            </div>
          </div>

          <div className="space-y-4 max-h-[650px] overflow-y-auto p-4 bg-zinc-50/70 rounded-2xl border border-zinc-200/80">
            {transcript.segments && transcript.segments.length > 0 ? (
              transcript.segments.map((s) => (
                <div key={s.id} className="p-3.5 bg-white rounded-xl border border-zinc-200 space-y-1 shadow-subtle">
                  <div className="flex items-center justify-between text-[11px] text-zinc-500 font-semibold">
                    <span className="text-zinc-900 font-bold">{s.speaker}</span>
                    <span className="font-mono">
                      {Math.floor(s.start_time_ms / 60000)}m {Math.floor((s.start_time_ms % 60000) / 1000)}s
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-zinc-800 leading-relaxed font-sans">{s.text}</p>
                </div>
              ))
            ) : (
              <p className="whitespace-pre-wrap text-xs sm:text-sm text-zinc-800 font-sans">{transcript.raw_text}</p>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
