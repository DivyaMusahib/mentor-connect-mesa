import React, { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import {
  Sparkles,
  Calendar,
  Video,
  FileText,
  Clock,
  TrendingUp,
  Award,
  Compass,
  ChevronRight,
  ArrowRight,
  AlertCircle
} from 'lucide-react';

export default function Overview() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [bookings, setBookings] = useState([]);
  const [roadmap, setRoadmap] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [bookingsData, roadmapData, timelineData] = await Promise.all([
        api.getBookings().catch(() => []),
        api.getCareerRoadmap().catch(() => null),
        api.getCareerTimeline().catch(() => []),
      ]);
      setBookings(bookingsData || []);
      setRoadmap(roadmapData);
      setTimeline(timelineData || []);
    } catch (err) {
      setError(err.message || 'Unable to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const upcomingBooking = bookings.find(
    (b) => b.status === 'confirmed' || b.status === 'rescheduled'
  );
  const completedBookings = bookings.filter((b) => b.status === 'completed');
  const firstName = user?.full_name?.split(' ')[0] || 'Fellow';

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-6 lg:px-10 py-16 text-center">
        <div className="w-7 h-7 rounded-full border-2 border-zinc-900 border-t-transparent animate-spin mx-auto mb-3" />
        <p className="text-sm text-zinc-500">Loading your dashboard…</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-12 space-y-10">
      {error && (
        <div className="p-4 rounded-2xl bg-red-50 text-red-900 border border-red-200 text-xs sm:text-sm flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={loadDashboardData} className="font-semibold underline ml-3 hover:text-red-950">
            Retry
          </button>
        </div>
      )}

      {/* Welcome Hero */}
      <div className="bg-white rounded-2xl border border-zinc-200 p-8 lg:p-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8">
        <div className="space-y-2 max-w-xl">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 mb-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Active Mesa Fellow · Cohort 2026
          </span>
          <h1 className="text-3xl lg:text-4xl font-bold text-zinc-900 tracking-tight">
            Welcome back, {firstName}
          </h1>
          <p className="text-sm text-zinc-600 leading-relaxed">
            {roadmap?.goal?.objective ||
              'Accelerating your transition into high-impact business and tech leadership.'}
          </p>
          {roadmap?.goal?.current_blocker && (
            <p className="text-xs text-zinc-700 bg-zinc-100 border border-zinc-200 px-3.5 py-2 rounded-xl inline-block mt-1">
              <span className="font-semibold">Current Focus:</span>{' '}
              {roadmap.goal.current_blocker}
            </p>
          )}
        </div>

        <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto flex-shrink-0">
          <NavLink
            to="/advisor"
            className="flex items-center justify-center gap-2 px-6 py-3 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl text-sm font-semibold transition-colors shadow-sm"
          >
            <Sparkles className="w-4 h-4 text-emerald-400" />
            AI Career Advisor
          </NavLink>
          <NavLink
            to="/mentors"
            className="flex items-center justify-center gap-2 px-5 py-3 bg-zinc-100 hover:bg-zinc-200 text-zinc-800 rounded-xl text-sm font-semibold transition-colors"
          >
            Browse Mentors
            <ArrowRight className="w-4 h-4" />
          </NavLink>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white rounded-2xl border border-zinc-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
              Sessions Completed
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center">
              <Award className="w-4 h-4 text-emerald-700" />
            </div>
          </div>
          <div>
            <p className="text-3xl font-bold text-zinc-900">{completedBookings.length}</p>
            <p className="text-xs text-zinc-500 mt-0.5">mentorship calls done</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-zinc-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
              Roadmap Progress
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-amber-700" />
            </div>
          </div>
          <div>
            <p className="text-3xl font-bold text-zinc-900">
              {roadmap?.completion_percentage || 0}%
            </p>
            <div className="w-full bg-zinc-100 h-1.5 rounded-full mt-2">
              <div
                className="bg-emerald-600 h-1.5 rounded-full transition-all duration-700"
                style={{ width: `${roadmap?.completion_percentage || 0}%` }}
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-zinc-200 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-widest text-zinc-500">
              Active Booking
            </span>
            <div className="w-8 h-8 rounded-lg bg-zinc-50 flex items-center justify-center">
              <Calendar className="w-4 h-4 text-zinc-700" />
            </div>
          </div>
          <div>
            <p className="text-3xl font-bold text-zinc-900">{upcomingBooking ? 1 : 0}</p>
            <p className="text-xs text-zinc-500 mt-0.5">upcoming session</p>
          </div>
        </div>
      </div>

      {/* Main 2-col layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

        {/* Upcoming Session (8 cols) */}
        <div className="lg:col-span-8">
          <div className="bg-white rounded-2xl border border-zinc-200 p-7 space-y-6">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-5">
              <div className="flex items-center gap-2.5">
                <Calendar className="w-5 h-5 text-zinc-700" />
                <h2 className="text-base font-bold text-zinc-900">Next Mentorship Session</h2>
              </div>
              {upcomingBooking && (
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                  Confirmed
                </span>
              )}
            </div>

            {upcomingBooking ? (
              <div className="space-y-5">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 bg-zinc-50 rounded-xl border border-zinc-200 gap-5">
                  <div className="space-y-1.5">
                    <h3 className="font-bold text-zinc-900 text-lg">{upcomingBooking.mentor_name}</h3>
                    <p className="text-sm text-zinc-600">
                      {upcomingBooking.mentor_domain} · {upcomingBooking.mentor_company || 'Industry Practitioner'}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-zinc-600 font-medium pt-0.5">
                      <span className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-zinc-400" />
                        {new Date(upcomingBooking.scheduled_at).toLocaleString([], {
                          dateStyle: 'medium',
                          timeStyle: 'short',
                        })}
                      </span>
                      <span className="text-zinc-300">·</span>
                      <span>45 min · Google Meet</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 w-full sm:w-auto">
                    {upcomingBooking.meet_link && (
                      <a
                        href={upcomingBooking.meet_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-5 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-sm font-semibold transition-colors shadow-sm"
                      >
                        <Video className="w-4 h-4" />
                        Join Meet
                      </a>
                    )}
                    <button
                      onClick={() => navigate(`/preparation?booking_id=${upcomingBooking.id}`)}
                      className="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 py-2.5 bg-white hover:bg-zinc-50 text-zinc-700 rounded-xl text-sm font-semibold border border-zinc-200 transition-colors"
                    >
                      <FileText className="w-4 h-4 text-zinc-400" />
                      Prep Brief
                    </button>
                  </div>
                </div>

                <p className="text-xs text-zinc-500 px-1">
                  Your AI-generated preparation brief with 3 tailored questions is ready to review.
                </p>
              </div>
            ) : (
              <div className="py-14 text-center space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-zinc-100 flex items-center justify-center mx-auto">
                  <Calendar className="w-6 h-6 text-zinc-400" />
                </div>
                <div className="space-y-1.5">
                  <p className="font-semibold text-zinc-900">No sessions scheduled</p>
                  <p className="text-sm text-zinc-500 max-w-sm mx-auto">
                    Describe your career challenge to get matched with the right mentor.
                  </p>
                </div>
                <NavLink
                  to="/advisor"
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl text-sm font-semibold transition-colors"
                >
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  Start AI Career Advisor
                </NavLink>
              </div>
            )}
          </div>
        </div>

        {/* Career Timeline (4 cols) */}
        <div className="lg:col-span-4">
          <div className="bg-white rounded-2xl border border-zinc-200 p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-4">
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-zinc-700" />
                <h2 className="text-sm font-bold text-zinc-900">Career Journey</h2>
              </div>
              <NavLink
                to="/roadmap"
                className="flex items-center gap-1 text-xs font-semibold text-zinc-500 hover:text-zinc-900 transition-colors"
              >
                Full view <ChevronRight className="w-3.5 h-3.5" />
              </NavLink>
            </div>

            {timeline.length > 0 ? (
              <div className="relative pl-5 border-l-2 border-zinc-100 space-y-5">
                {timeline.slice(0, 5).map((ev) => (
                  <div key={ev.id} className="relative">
                    <div className="absolute -left-[25px] top-1 w-2.5 h-2.5 rounded-full bg-zinc-900 border-2 border-white" />
                    <p className="text-sm font-semibold text-zinc-900">{ev.title}</p>
                    <p className="text-xs text-zinc-500 mt-0.5 line-clamp-2 leading-relaxed">
                      {ev.description}
                    </p>
                    <span className="text-[10px] text-zinc-400 font-medium mt-1 block">
                      {new Date(ev.timestamp).toLocaleDateString([], {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-10 text-center text-xs text-zinc-500">
                No journey events yet. Complete your first career diagnosis!
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
