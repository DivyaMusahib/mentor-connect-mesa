import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import {
  Compass,
  TrendingUp,
  CheckCircle2,
  Circle,
  Clock,
  Edit2,
  Save,
  Target
} from 'lucide-react';

export default function CareerRoadmap() {
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingGoal, setEditingGoal] = useState(false);
  const [goalForm, setGoalForm] = useState({ objective: '', current_blocker: '', next_milestone: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadRoadmap();
  }, []);

  const loadRoadmap = async () => {
    setLoading(true);
    try {
      const data = await api.getCareerRoadmap();
      setRoadmap(data);
      if (data?.goal) {
        setGoalForm({
          objective: data.goal.objective || '',
          current_blocker: data.goal.current_blocker || '',
          next_milestone: data.goal.next_milestone || '',
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveGoal = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.updateCareerGoal(goalForm);
      setEditingGoal(false);
      await loadRoadmap();
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const toggleStep = async (step) => {
    try {
      await api.updateRoadmapStep(step.id, { is_completed: !step.is_completed });
      await loadRoadmap();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 lg:px-10 py-12 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-6 border-b border-zinc-200/80">
        <div className="space-y-1">
          <div className="flex items-center space-x-3 mb-1">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800 border border-zinc-200">
              Personalized Plan
            </span>
            <span className="text-xs text-zinc-500 font-medium">Cohort 2026</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-zinc-900 tracking-tight">
            Career Roadmap & Milestones
          </h1>
          <p className="text-xs sm:text-sm text-zinc-500">
            Actionable execution steps aligned with your diagnosed blockers and mentor outcomes.
          </p>
        </div>

        {roadmap && (
          <div className="flex items-center space-x-3 bg-white px-5 py-3 rounded-2xl border border-zinc-200 shadow-subtle">
            <span className="text-xs text-zinc-500 font-medium">Overall Completion:</span>
            <span className="text-lg font-heading font-bold text-zinc-900">
              {roadmap.completion_percentage}%
            </span>
          </div>
        )}
      </div>

      {loading ? (
        <div className="py-20 text-center text-zinc-500 text-sm">Loading career roadmap...</div>
      ) : roadmap ? (
        <div className="space-y-8">
          {/* Active Career Goal Card */}
          <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-100">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-zinc-700" />
                <h2 className="text-base font-heading font-bold text-zinc-900">
                  Primary Career Objective
                </h2>
              </div>
              {!editingGoal ? (
                <button
                  onClick={() => setEditingGoal(true)}
                  className="px-3.5 py-1.5 text-xs text-zinc-700 hover:text-zinc-900 border border-zinc-200 rounded-xl flex items-center space-x-1.5 hover:bg-zinc-50 transition font-medium"
                >
                  <Edit2 className="w-3.5 h-3.5 text-zinc-500" />
                  <span>Edit Objective</span>
                </button>
              ) : (
                <button
                  onClick={() => setEditingGoal(false)}
                  className="text-xs text-zinc-500 hover:text-zinc-800 font-medium"
                >
                  Cancel
                </button>
              )}
            </div>

            {editingGoal ? (
              <form onSubmit={handleSaveGoal} className="space-y-4 text-xs">
                <div>
                  <label className="block font-semibold text-zinc-800 mb-1.5">Career Goal / Target Role</label>
                  <input
                    type="text"
                    required
                    value={goalForm.objective}
                    onChange={(e) => setGoalForm({ ...goalForm, objective: e.target.value })}
                    className="w-full px-4 py-2.5 border border-zinc-300 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-zinc-800 mb-1.5">Diagnosed Blocker</label>
                  <input
                    type="text"
                    value={goalForm.current_blocker}
                    onChange={(e) => setGoalForm({ ...goalForm, current_blocker: e.target.value })}
                    className="w-full px-4 py-2.5 border border-zinc-300 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-zinc-800 mb-1.5">Next Measurable Milestone</label>
                  <input
                    type="text"
                    value={goalForm.next_milestone}
                    onChange={(e) => setGoalForm({ ...goalForm, next_milestone: e.target.value })}
                    className="w-full px-4 py-2.5 border border-zinc-300 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900"
                  />
                </div>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2.5 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl font-semibold flex items-center space-x-1.5 shadow-sm"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                </button>
              </form>
            ) : (
              <div className="space-y-4">
                <p className="text-lg sm:text-xl font-heading font-bold text-zinc-900">
                  {roadmap.goal?.objective}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-1">
                  <div className="p-4 bg-zinc-50 rounded-2xl border border-zinc-200/80 space-y-1">
                    <span className="font-semibold text-zinc-500 uppercase tracking-wider block text-[10px]">
                      Immediate Blocker
                    </span>
                    <p className="text-zinc-800 font-medium text-xs sm:text-sm">{roadmap.goal?.current_blocker || 'None diagnosed'}</p>
                  </div>
                  <div className="p-4 bg-zinc-50 rounded-2xl border border-zinc-200/80 space-y-1">
                    <span className="font-semibold text-zinc-500 uppercase tracking-wider block text-[10px]">
                      Next Measurable Milestone
                    </span>
                    <p className="text-zinc-900 font-bold text-xs sm:text-sm">{roadmap.goal?.next_milestone || 'In progress'}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sequential Execution Steps */}
          <div className="bg-white rounded-3xl border border-zinc-200/90 p-7 sm:p-8 shadow-card space-y-6">
            <h2 className="text-base font-heading font-bold text-zinc-900 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-zinc-700" />
              <span>Execution Steps & Timelines</span>
            </h2>

            <div className="space-y-5 relative before:absolute before:inset-0 before:left-5 before:w-0.5 before:bg-zinc-200">
              {roadmap.steps?.map((step, idx) => (
                <div
                  key={step.id}
                  className="relative flex items-start space-x-4 pl-1 group"
                >
                  <button
                    onClick={() => toggleStep(step)}
                    className="relative z-10 w-8 h-8 rounded-full bg-white border-2 flex items-center justify-center transition shadow-xs mt-0.5 flex-shrink-0"
                  >
                    {step.is_completed ? (
                      <CheckCircle2 className="w-7 h-7 text-emerald-700 bg-white rounded-full" />
                    ) : (
                      <Circle className="w-5 h-5 text-zinc-300 group-hover:text-zinc-500" />
                    )}
                  </button>

                  <div className={`flex-1 p-5 rounded-2xl border transition ${
                    step.is_completed ? 'bg-zinc-50/60 border-zinc-200 text-zinc-400' : 'bg-white border-zinc-200/90 shadow-subtle'
                  }`}>
                    <div className="flex items-center justify-between">
                      <h3 className={`text-xs sm:text-sm font-semibold ${step.is_completed ? 'line-through text-zinc-500' : 'text-zinc-900'}`}>
                        {idx + 1}. {step.title}
                      </h3>
                      {step.time_estimate && (
                        <span className="text-[10px] font-mono text-zinc-500 bg-zinc-100 px-2.5 py-1 rounded-lg">
                          {step.time_estimate}
                        </span>
                      )}
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-600 mt-1.5 leading-relaxed">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
