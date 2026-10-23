import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import {
  CheckSquare,
  Square,
  Clock,
  Calendar,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';

export default function ProgressTracker() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all | active | completed | high

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    setLoading(true);
    try {
      const data = await api.getActionItems();
      setItems(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (item) => {
    try {
      await api.updateActionItem(item.id, { is_completed: !item.is_completed });
      await loadItems();
    } catch (e) {
      console.error(e);
    }
  };

  const completedCount = items.filter((i) => i.is_completed).length;
  const totalCount = items.length;
  const completionRate = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  const filteredItems = items.filter((item) => {
    if (filter === 'active') return !item.is_completed;
    if (filter === 'completed') return item.is_completed;
    if (filter === 'high') return item.priority === 'high' && !item.is_completed;
    return true;
  });

  return (
    <div className="max-w-5xl mx-auto px-6 lg:px-10 py-12 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-6 border-b border-zinc-200/80">
        <div className="space-y-1">
          <div className="flex items-center space-x-3 mb-1">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800 border border-zinc-200">
              Task Checklist
            </span>
            <span className="text-xs text-zinc-500 font-medium">Post-Call Commitments</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-zinc-900 tracking-tight">
            Action Items & Follow-Through
          </h1>
          <p className="text-xs sm:text-sm text-zinc-500">
            Commitments and deliverables generated from your mentorship sessions with deadline tracking.
          </p>
        </div>

        <div className="flex items-center space-x-4 bg-white px-5 py-3 rounded-2xl border border-zinc-200 shadow-subtle">
          <div>
            <span className="text-[10px] text-zinc-500 uppercase tracking-wider block font-semibold">Completed</span>
            <span className="text-base font-heading font-bold text-zinc-900">{completedCount} of {totalCount}</span>
          </div>
          <div className="w-11 h-11 flex items-center justify-center rounded-xl bg-zinc-100 text-zinc-900 font-bold text-xs border border-zinc-200">
            {completionRate}%
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 text-xs font-semibold">
        {['all', 'active', 'high', 'completed'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3.5 py-2 rounded-xl transition capitalize ${
              filter === f ? 'bg-zinc-900 text-white shadow-xs' : 'bg-white text-zinc-600 border border-zinc-200 hover:bg-zinc-50'
            }`}
          >
            {f === 'high' ? 'High Priority' : f}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="py-20 text-center text-zinc-500 text-sm">Loading action items...</div>
      ) : filteredItems.length > 0 ? (
        <div className="space-y-3.5">
          {filteredItems.map((item) => {
            const isOverdue = item.due_date && new Date(item.due_date) < new Date() && !item.is_completed;
            return (
              <div
                key={item.id}
                className={`p-5 rounded-3xl border transition flex items-start space-x-4 ${
                  item.is_completed
                    ? 'bg-zinc-50/60 border-zinc-200 text-zinc-400'
                    : isOverdue
                    ? 'bg-red-50/40 border-red-200/80 shadow-xs'
                    : 'bg-white border-zinc-200/90 shadow-card'
                }`}
              >
                <button
                  onClick={() => handleToggle(item)}
                  className="mt-0.5 text-zinc-400 hover:text-zinc-900 transition flex-shrink-0"
                >
                  {item.is_completed ? (
                    <CheckSquare className="w-5 h-5 text-emerald-700" />
                  ) : (
                    <Square className="w-5 h-5 text-zinc-300 hover:text-zinc-500" />
                  )}
                </button>

                <div className="flex-1 space-y-1.5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <h3 className={`text-xs sm:text-sm font-semibold ${item.is_completed ? 'line-through text-zinc-500' : 'text-zinc-900'}`}>
                      {item.title}
                    </h3>
                    <div className="flex items-center space-x-2">
                      {isOverdue && (
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200 flex items-center space-x-1">
                          <AlertTriangle className="w-3 h-3 text-red-600" />
                          <span>Overdue</span>
                        </span>
                      )}
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                        item.priority === 'high' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-zinc-100 text-zinc-700'
                      }`}>
                        {item.priority}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs sm:text-sm text-zinc-600 leading-relaxed">{item.description}</p>

                  <div className="flex flex-wrap items-center gap-4 pt-1.5 text-xs text-zinc-500">
                    {item.deliverable && (
                      <span className="font-mono bg-zinc-100 px-2.5 py-1 rounded-lg text-[11px]">
                        Target: {item.deliverable}
                      </span>
                    )}
                    {item.due_date && (
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3.5 h-3.5 text-zinc-400" />
                        <span>Due {new Date(item.due_date).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                      </span>
                    )}
                    {item.completed_at && (
                      <span className="text-emerald-700 font-semibold text-[11px]">
                        Completed on {new Date(item.completed_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="py-20 text-center bg-white rounded-3xl border border-zinc-200/90 p-8 space-y-3">
          <CheckCircle2 className="w-12 h-12 text-zinc-300 mx-auto" />
          <p className="text-base font-semibold text-zinc-800">No action items in this filter</p>
          <p className="text-xs sm:text-sm text-zinc-500 max-w-sm mx-auto">
            Complete a mentorship call to automatically extract action deliverables.
          </p>
        </div>
      )}
    </div>
  );
}
