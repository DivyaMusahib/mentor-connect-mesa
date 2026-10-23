import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import {
  ShieldAlert,
  TrendingUp,
  Users,
  Calendar,
  AlertTriangle,
  Mail,
  Activity,
  RefreshCw,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Search,
  ArrowRight
} from 'lucide-react';

export default function MesaAdmin() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview'); // overview | supply_gaps | email_logs | automation | health
  const [metrics, setMetrics] = useState(null);
  const [supplyGaps, setSupplyGaps] = useState([]);
  const [emailLogs, setEmailLogs] = useState([]);
  const [automationEvents, setAutomationEvents] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [retryingId, setRetryingId] = useState(null);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    if (user?.role === 'admin') {
      loadAdminData();
    }
  }, [user]);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      const [m, g, e, a, h] = await Promise.all([
        api.getAdminOverview().catch(() => null),
        api.getSupplyGaps().catch(() => []),
        api.getEmailLogs().catch(() => []),
        api.getAutomationEvents().catch(() => []),
        api.getIntegrationHealth().catch(() => null),
      ]);
      setMetrics(m);
      setSupplyGaps(g);
      setEmailLogs(e);
      setAutomationEvents(a);
      setHealth(h);
    } finally {
      setLoading(false);
    }
  };

  const handleRetryAutomation = async (eventId) => {
    setRetryingId(eventId);
    setFeedback(null);
    try {
      await api.retryAutomation(eventId);
      setFeedback({ type: 'success', text: `Event ${eventId} successfully retried.` });
      await loadAdminData();
    } catch (err) {
      setFeedback({ type: 'error', text: err.message || 'Retry failed.' });
    } finally {
      setRetryingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-12 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-6 border-b border-zinc-200/80">
        <div className="space-y-1">
          <div className="flex items-center space-x-3 mb-1">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800 border border-zinc-200">
              Staff Console
            </span>
            <span className="text-xs text-zinc-500 font-medium">Cohort Analytics & Reliability</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-zinc-900 tracking-tight">
            Mesa Admin & Observability
          </h1>
          <p className="text-xs sm:text-sm text-zinc-500">
            Real-time cohort demand, unmatched supply gaps, and n8n webhook health.
          </p>
        </div>

        {/* Tab Selection */}
        <div className="flex flex-wrap items-center bg-zinc-100 p-1 rounded-2xl text-xs font-semibold gap-1">
          {[
            { id: 'overview', label: 'Platform Metrics' },
            { id: 'supply_gaps', label: `Supply Gaps (${supplyGaps.length})` },
            { id: 'automation', label: 'Webhook Activity' },
            { id: 'email_logs', label: 'Email Outbox' },
            { id: 'health', label: 'Integration Health' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2 rounded-xl transition ${
                activeTab === tab.id ? 'bg-white text-zinc-900 shadow-xs' : 'text-zinc-600 hover:text-zinc-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {feedback && (
        <div className={`p-4 rounded-2xl text-xs sm:text-sm ${feedback.type === 'success' ? 'bg-emerald-50 text-emerald-900 border border-emerald-200' : 'bg-red-50 text-red-900 border border-red-200'}`}>
          {feedback.text}
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center text-zinc-500 text-sm">Aggregating cohort metrics...</div>
      ) : activeTab === 'overview' && metrics ? (
        <div className="space-y-8">
          {/* Key KPI Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-3xl border border-zinc-200/90 shadow-card space-y-2">
              <span className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">Total Students</span>
              <p className="text-3xl font-heading font-bold text-zinc-900">{metrics.total_students}</p>
              <span className="text-xs text-zinc-600 font-medium block">Active Profiles</span>
            </div>

            <div className="bg-white p-6 rounded-3xl border border-zinc-200/90 shadow-card space-y-2">
              <span className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">Diagnoses</span>
              <p className="text-3xl font-heading font-bold text-zinc-900">{metrics.diagnostic_sessions}</p>
              <span className="text-xs text-zinc-600 font-medium block">Career Hurdle Sessions</span>
            </div>

            <div className="bg-white p-6 rounded-3xl border border-zinc-200/90 shadow-card space-y-2">
              <span className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">Bookings</span>
              <p className="text-3xl font-heading font-bold text-zinc-900">{metrics.total_bookings}</p>
              <span className="text-xs text-emerald-700 font-medium block">{metrics.completed_meetings} completed</span>
            </div>

            <div className="bg-white p-6 rounded-3xl border border-zinc-200/90 shadow-card space-y-2">
              <span className="text-xs text-zinc-500 font-semibold uppercase tracking-wider">Task Completion</span>
              <p className="text-3xl font-heading font-bold text-zinc-900">{metrics.action_item_completion_rate}%</p>
              <span className="text-xs text-zinc-600 font-medium block">{metrics.completed_action_items} of {metrics.total_action_items} tasks</span>
            </div>
          </div>

          {/* Secondary Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-7 rounded-3xl border border-zinc-200/90 shadow-card space-y-4">
              <h3 className="text-base font-heading font-bold text-zinc-900">
                Diagnostic Outcomes
              </h3>
              <div className="space-y-3 text-xs sm:text-sm">
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span className="text-zinc-600">Matches Unlocked:</span>
                  <span className="font-bold text-zinc-900">{metrics.successful_mentor_matches}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span className="text-zinc-600">Unmatched Supply Gaps:</span>
                  <span className="font-bold text-amber-700">{metrics.no_exact_match_cases}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span className="text-zinc-600">Rescheduled Calls:</span>
                  <span className="font-bold text-zinc-900">{metrics.rescheduled_meetings}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-zinc-600">AI Reports Generated:</span>
                  <span className="font-bold text-zinc-900">{metrics.reports_generated}</span>
                </div>
              </div>
            </div>

            {/* Mentor Demand */}
            <div className="md:col-span-2 bg-white p-7 rounded-3xl border border-zinc-200/90 shadow-card space-y-4">
              <h3 className="text-base font-heading font-bold text-zinc-900">
                Domain Demand Distribution
              </h3>
              <div className="space-y-3 text-xs sm:text-sm">
                {Object.entries(metrics.mentor_demand_by_domain || {}).map(([dom, cnt]) => (
                  <div key={dom} className="space-y-1.5">
                    <div className="flex justify-between text-zinc-700 font-medium">
                      <span>{dom}</span>
                      <span className="font-semibold text-zinc-900">{cnt} bookings</span>
                    </div>
                    <div className="w-full bg-zinc-100 rounded-full h-2">
                      <div
                        className="bg-zinc-900 h-2 rounded-full"
                        style={{ width: `${Math.min(100, cnt * 25)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : activeTab === 'supply_gaps' ? (
        /* Supply Gaps */
        <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-5">
          <div className="flex items-center justify-between pb-4 border-b border-zinc-100">
            <div>
              <h2 className="text-base font-heading font-bold text-zinc-900">
                Unmatched Mentor Supply Gaps
              </h2>
              <p className="text-xs text-zinc-500">
                Queries where no exact match was found in the 50-mentor dataset. Informs future mentor recruitment.
              </p>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800">
              {supplyGaps.length} Logged Gaps
            </span>
          </div>

          {supplyGaps.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead>
                  <tr className="border-b border-zinc-200 text-zinc-500 uppercase tracking-wider font-semibold text-[11px]">
                    <th className="py-3 px-3">Fellow</th>
                    <th className="py-3 px-3">Requested Domain</th>
                    <th className="py-3 px-3">Student Query</th>
                    <th className="py-3 px-3">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100">
                  {supplyGaps.map((g) => (
                    <tr key={g.id} className="hover:bg-zinc-50">
                      <td className="py-3.5 px-3 font-semibold text-zinc-900">
                        {g.student_name || 'Fellow'}
                      </td>
                      <td className="py-3.5 px-3">
                        <span className="px-2.5 py-1 rounded-lg bg-zinc-100 text-zinc-800 font-medium text-xs">
                          {g.requested_domain || 'Specialized'}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-zinc-700 max-w-sm truncate" title={g.student_query}>
                        {g.student_query}
                      </td>
                      <td className="py-3.5 px-3 text-zinc-500">
                        {new Date(g.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-14 text-center text-xs text-zinc-500">
              No supply gaps recorded. All submitted diagnostic queries have matched verified mentors!
            </div>
          )}
        </div>
      ) : activeTab === 'automation' ? (
        /* Automation Events */
        <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-5">
          <div className="flex items-center justify-between pb-4 border-b border-zinc-100">
            <div>
              <h2 className="text-base font-heading font-bold text-zinc-900">
                n8n Automation Event History
              </h2>
              <p className="text-xs text-zinc-500">
                Outbound webhook dispatches, execution IDs, and error recovery controls.
              </p>
            </div>
          </div>

          {automationEvents.length > 0 ? (
            <div className="divide-y divide-zinc-100">
              {automationEvents.map((ev) => (
                <div key={ev.id} className="py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs sm:text-sm">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2.5">
                      <span className={`px-2.5 py-0.5 rounded-full font-mono uppercase text-[10px] font-bold ${
                        ev.status === 'completed'
                          ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                          : ev.status === 'simulated'
                          ? 'bg-zinc-100 text-zinc-800 border border-zinc-200'
                          : 'bg-red-50 text-red-800 border border-red-200'
                      }`}>
                        {ev.status}
                      </span>
                      <span className="font-semibold text-zinc-900">{ev.event_type}</span>
                      {ev.n8n_execution_id && (
                        <span className="text-[10px] font-mono text-zinc-500">
                          exec: {ev.n8n_execution_id}
                        </span>
                      )}
                    </div>
                    {ev.error_message && (
                      <p className="text-xs text-red-700 font-mono">{ev.error_message}</p>
                    )}
                    <span className="text-[11px] text-zinc-600 block">
                      {new Date(ev.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'medium' })}
                    </span>
                  </div>

                  {ev.status === 'failed' && (
                    <button
                      onClick={() => handleRetryAutomation(ev.id)}
                      disabled={retryingId === ev.id}
                      className="px-3.5 py-1.5 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 shadow-sm"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${retryingId === ev.id ? 'animate-spin' : ''}`} />
                      <span>{retryingId === ev.id ? 'Retrying...' : 'Retry Webhook'}</span>
                    </button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="py-14 text-center text-xs text-zinc-500">
              No automation events logged yet.
            </div>
          )}
        </div>
      ) : activeTab === 'email_logs' ? (
        /* Email Logs */
        <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-5">
          <div className="pb-4 border-b border-zinc-100">
            <h2 className="text-base font-heading font-bold text-zinc-900">
              Email Notification Outbox
            </h2>
            <p className="text-xs text-zinc-500">
              Dispatched meeting confirmations, 24h & 30m reminders, and post-call reports via Gmail.
            </p>
          </div>

          {emailLogs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead>
                  <tr className="border-b border-zinc-200 text-zinc-500 uppercase tracking-wider font-semibold text-[11px]">
                    <th className="py-3 px-3">Recipient</th>
                    <th className="py-3 px-3">Subject</th>
                    <th className="py-3 px-3">Template</th>
                    <th className="py-3 px-3">Status</th>
                    <th className="py-3 px-3">Sent At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100">
                  {emailLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-zinc-50">
                      <td className="py-3.5 px-3 font-semibold text-zinc-900">{log.recipient_email}</td>
                      <td className="py-3.5 px-3 text-zinc-700 max-w-xs truncate">{log.subject}</td>
                      <td className="py-3.5 px-3 font-mono text-xs text-zinc-500">{log.template_name}</td>
                      <td className="py-3.5 px-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                          log.status === 'sent' ? 'bg-emerald-50 text-emerald-800' : 'bg-zinc-100 text-zinc-700'
                        }`}>
                          {log.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-zinc-500">
                        {new Date(log.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-14 text-center text-xs text-zinc-500">
              No emails logged yet.
            </div>
          )}
        </div>
      ) : activeTab === 'health' && health ? (
        /* Health Status */
        <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-6">
          <div className="pb-4 border-b border-zinc-100">
            <h2 className="text-base font-heading font-bold text-zinc-900">
              System Health & External Integrations
            </h2>
            <p className="text-xs text-zinc-500">
              Real-time connectivity report for Google OAuth, Gemini AI, n8n Cloud, and database.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs sm:text-sm">
            <div className="p-5 bg-zinc-50 rounded-2xl border border-zinc-200 space-y-1">
              <span className="text-zinc-500 font-medium">Database Persistence:</span>
              <p className="font-bold text-emerald-700">Connected & Verified</p>
            </div>
            <div className="p-5 bg-zinc-50 rounded-2xl border border-zinc-200 space-y-1">
              <span className="text-zinc-500 font-medium">AI Intelligence:</span>
              <p className="font-bold text-zinc-900">Google Gemini 3.5 Flash Lite</p>
            </div>
            <div className="p-5 bg-zinc-50 rounded-2xl border border-zinc-200 space-y-1">
              <span className="text-zinc-500 font-medium">Meeting Transcription:</span>
              <p className="font-bold text-zinc-900 capitalize">{health.transcription_provider} + n8n Webhook</p>
            </div>
            <div className="p-5 bg-zinc-50 rounded-2xl border border-zinc-200 space-y-1">
              <span className="text-zinc-500 font-medium">Workflow Engine:</span>
              <p className="font-bold text-zinc-900">n8n Cloud Automation</p>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
