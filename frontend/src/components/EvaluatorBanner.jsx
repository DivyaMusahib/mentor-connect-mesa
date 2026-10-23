import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import {
  ShieldCheck,
  UserCheck,
  RefreshCw,
  RotateCcw,
  Sliders,
  CheckCircle2,
  X,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

export default function EvaluatorBanner() {
  const { user, loginWithDemo } = useAuth();
  const [health, setHealth] = useState(null);
  const [seeding, setSeeding] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadHealth();
  }, []);

  const loadHealth = async () => {
    try {
      const data = await api.getIntegrationHealth();
      setHealth(data);
    } catch (e) {
      // Ignored
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    setFeedback(null);
    try {
      const res = await api.seedDemo();
      setFeedback({ type: 'success', text: res.message || 'Demo sessions seeded successfully!' });
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      setFeedback({ type: 'error', text: err.message || 'Seeding failed.' });
    } finally {
      setSeeding(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset demo data back to a clean initial state?')) return;
    try {
      await api.resetDemo();
      setFeedback({ type: 'success', text: 'Clean state restored.' });
      setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      setFeedback({ type: 'error', text: err.message || 'Reset failed.' });
    }
  };

  const switchRole = async (targetRole) => {
    await loginWithDemo(targetRole);
    window.location.reload();
  };

  return (
    <aside aria-label="Reviewer Sandbox Controls" className="fixed bottom-5 right-5 z-50">
      {/* Expanded Popover Panel */}
      {isOpen && (
        <div className="mb-3 w-80 bg-white rounded-2xl border border-zinc-200/90 shadow-2xl p-5 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center justify-between pb-3 border-b border-zinc-100">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <h2 className="text-xs font-bold text-zinc-900 tracking-tight uppercase">
                Reviewer Sandbox
              </h2>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 text-zinc-400 hover:text-zinc-700 rounded-lg hover:bg-zinc-100 transition"
              aria-label="Close Sandbox Controls"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Current Active Role */}
          <div className="flex items-center justify-between text-xs bg-zinc-50 p-2.5 rounded-xl border border-zinc-100">
            <span className="text-zinc-500 font-medium">Active Account:</span>
            <span className="font-semibold text-zinc-900">
              {user ? (user.role === 'admin' ? 'Mesa Administrator' : 'Student (Arjun Bansal)') : 'Guest'}
            </span>
          </div>

          {/* Role Switcher */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider block">
              1-Click Role Switcher
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => switchRole('student')}
                className={`py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center space-x-1.5 transition border ${
                  user?.role === 'student'
                    ? 'bg-zinc-900 text-white border-zinc-900'
                    : 'bg-white hover:bg-zinc-50 text-zinc-700 border-zinc-200'
                }`}
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>Student</span>
              </button>
              <button
                onClick={() => switchRole('admin')}
                className={`py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center space-x-1.5 transition border ${
                  user?.role === 'admin'
                    ? 'bg-zinc-900 text-white border-zinc-900'
                    : 'bg-white hover:bg-zinc-50 text-zinc-700 border-zinc-200'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Admin</span>
              </button>
            </div>
          </div>

          {/* Sample Data Actions */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider block">
              Evaluation Helper
            </label>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleSeed}
                disabled={seeding}
                className="flex-1 py-2 px-3 bg-zinc-900 hover:bg-zinc-800 disabled:bg-zinc-300 text-white rounded-xl text-xs font-semibold transition flex items-center justify-center space-x-1.5 shadow-sm"
              >
                <RefreshCw className={`w-3 h-3 ${seeding ? 'animate-spin' : ''}`} />
                <span>{seeding ? 'Populating...' : 'Seed Sample Sessions'}</span>
              </button>
              <button
                onClick={handleReset}
                className="p-2 text-zinc-400 hover:text-red-600 hover:bg-red-50 rounded-xl border border-zinc-200 transition"
                title="Reset database to initial clean state"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Backend Health Check */}
          {health && (
            <div className="pt-2 border-t border-zinc-100 text-[11px] text-zinc-500 space-y-1">
              <div className="flex justify-between items-center">
                <span>Database:</span>
                <span className="text-emerald-700 font-semibold">Connected</span>
              </div>
              <div className="flex justify-between items-center">
                <span>AI Pipeline:</span>
                <span className="text-zinc-700 font-semibold">Gemini 3.5 Flash Lite</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Transcription:</span>
                <span className="text-zinc-700 font-semibold capitalize">{health.transcription_provider}</span>
              </div>
            </div>
          )}

          {feedback && (
            <div className={`p-2 rounded-lg text-[11px] text-center font-medium ${
              feedback.type === 'success' ? 'bg-emerald-50 text-emerald-800' : 'bg-red-50 text-red-800'
            }`}>
              {feedback.text}
            </div>
          )}
        </div>
      )}

      {/* Floating Bottom Pill Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="glass-panel hover:bg-white text-zinc-800 px-3.5 py-2 rounded-full text-xs font-semibold flex items-center space-x-2 shadow-lg hover:shadow-xl transition border border-zinc-300/80 group"
      >
        <span className="w-2 h-2 rounded-full bg-emerald-600 group-hover:scale-110 transition" />
        <span className="text-zinc-900 font-medium tracking-tight">
          Sandbox: {user?.role === 'admin' ? 'Admin' : 'Student'}
        </span>
        <Sliders className="w-3.5 h-3.5 text-zinc-500" />
      </button>
    </aside>
  );
}
