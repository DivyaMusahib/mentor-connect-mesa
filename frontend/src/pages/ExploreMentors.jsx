import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import {
  Users,
  Search,
  Sparkles,
  Lock,
  Building,
  Briefcase,
  Wrench,
  ChevronRight
} from 'lucide-react';

export default function ExploreMentors() {
  const navigate = useNavigate();
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedSector, setSelectedSector] = useState('');
  const [selectedSeniority, setSelectedSeniority] = useState('');
  const [selectedTool, setSelectedTool] = useState('');

  useEffect(() => {
    loadMentors();
  }, [search, selectedDomain, selectedSector, selectedSeniority, selectedTool]);

  const loadMentors = async () => {
    setLoading(true);
    try {
      const data = await api.getMentors({
        search,
        domain: selectedDomain,
        sector: selectedSector,
        seniority: selectedSeniority,
        ai_tool: selectedTool,
      });
      setMentors(data || []);
    } catch (err) {
      console.error('Failed to load mentors:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckFit = (mentorId) => {
    navigate(`/advisor?candidate_mentor_id=${mentorId}`);
  };

  const domainOptions = [
    'Business Generalist',
    'Product Management',
    'Marketing',
    'Growth',
    'AI',
    'B2B sales and Partnerships/CSM',
    'Venture Capital',
    'Category Management',
  ];

  const sectorOptions = [
    'Edtech',
    'Fintech',
    'SaaS',
    'Quick Commerce',
    'D2C',
    'Healthtech',
    'Climatetech',
    'Gaming',
  ];

  return (
    <div className="max-w-7xl mx-auto px-6 lg:px-10 py-12 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-zinc-200/80">
        <div className="space-y-1">
          <div className="flex items-center space-x-3 mb-1">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 text-zinc-800 border border-zinc-200">
              Verified Directory
            </span>
            <span className="text-xs text-zinc-500 font-medium">50 Anonymised Industry Leaders</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-zinc-900 tracking-tight">
            Explore Mentors
          </h1>
          <p className="text-xs sm:text-sm text-zinc-500">
            Browse practitioners across tech, product, and growth. Booking unlocks automatically via AI diagnosis.
          </p>
        </div>

        <div className="flex items-center space-x-2.5 bg-zinc-100/80 border border-zinc-200 px-4 py-2.5 rounded-2xl text-xs text-zinc-700">
          <Lock className="w-4 h-4 text-zinc-500 flex-shrink-0" />
          <span>Click <strong>Assess Fit with AI</strong> to diagnose matching.</span>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="bg-white rounded-3xl border border-zinc-200/90 p-6 shadow-card space-y-4">
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-zinc-400 absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by mentor name, domain, company, or tools..."
              className="w-full pl-11 pr-4 py-3 bg-zinc-50 border border-zinc-200 hover:border-zinc-300 rounded-2xl text-xs sm:text-sm text-zinc-900 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-zinc-900 focus:bg-white transition"
            />
          </div>

          {(search || selectedDomain || selectedSector || selectedSeniority || selectedTool) && (
            <button
              onClick={() => {
                setSearch('');
                setSelectedDomain('');
                setSelectedSector('');
                setSelectedSeniority('');
                setSelectedTool('');
              }}
              className="text-xs text-red-600 font-semibold px-3 py-2 hover:bg-red-50 rounded-xl transition"
            >
              Reset Filters
            </button>
          )}
        </div>

        {/* Dropdowns */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-zinc-100 text-xs">
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="px-3.5 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900 focus:outline-none font-medium"
          >
            <option value="">All Domains</option>
            {domainOptions.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>

          <select
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="px-3.5 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900 focus:outline-none font-medium"
          >
            <option value="">All Sectors</option>
            {sectorOptions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          <select
            value={selectedSeniority}
            onChange={(e) => setSelectedSeniority(e.target.value)}
            className="px-3.5 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900 focus:outline-none font-medium"
          >
            <option value="">All Seniorities</option>
            <option value="Senior">Senior</option>
            <option value="Mid-career">Mid-Career</option>
            <option value="Mid-level">Mid-Level</option>
          </select>

          <select
            value={selectedTool}
            onChange={(e) => setSelectedTool(e.target.value)}
            className="px-3.5 py-2.5 bg-zinc-50 border border-zinc-200 rounded-xl text-zinc-800 focus:ring-2 focus:ring-zinc-900 focus:outline-none font-medium"
          >
            <option value="">All AI Tools</option>
            <option value="n8n">n8n</option>
            <option value="Make">Make</option>
            <option value="Zapier">Zapier</option>
            <option value="Notion AI">Notion AI</option>
            <option value="Langflow">Langflow</option>
          </select>
        </div>
      </div>

      {/* Mentors Grid */}
      {loading ? (
        <div className="py-20 text-center text-zinc-500 text-sm">
          Loading verified mentors...
        </div>
      ) : mentors.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
          {mentors.map((m) => (
            <div
              key={m.mentor_id}
              className="bg-white rounded-3xl border border-zinc-200/90 p-6 shadow-card hover:shadow-card-hover transition-all duration-200 flex flex-col justify-between space-y-5"
            >
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-0.5">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-heading font-bold text-base text-zinc-900">
                        {m.name}
                      </h3>
                      <span className="text-[10px] font-mono text-zinc-500 bg-zinc-100 px-2 py-0.5 rounded">
                        {m.mentor_id}
                      </span>
                    </div>
                    <p className="text-xs sm:text-sm text-zinc-600 font-medium">
                      {m.domain || 'Business Practitioner'}
                    </p>
                  </div>

                  {m.seniority && (
                    <span className="px-2.5 py-0.5 bg-zinc-100 text-zinc-700 rounded-full text-[10px] font-semibold border border-zinc-200">
                      {m.seniority}
                    </span>
                  )}
                </div>

                <div className="text-xs text-zinc-600 space-y-1.5 pt-1">
                  <div className="flex items-center space-x-2">
                    <Building className="w-3.5 h-3.5 text-zinc-400 flex-shrink-0" />
                    <span className="truncate">{m.company || 'Industry Leader'}</span>
                  </div>
                  {m.master_sector && (
                    <div className="flex items-center space-x-2">
                      <Briefcase className="w-3.5 h-3.5 text-zinc-400 flex-shrink-0" />
                      <span className="truncate">{m.master_sector}</span>
                    </div>
                  )}
                </div>

                {m.ai_tools_of_expertise && (
                  <div className="pt-2 border-t border-zinc-100 flex flex-wrap gap-1.5">
                    {m.ai_tools_of_expertise.split(',').slice(0, 3).map((tool, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-0.5 bg-zinc-100 text-zinc-700 rounded-lg text-[10px] font-medium"
                      >
                        {tool.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Card Footer Action */}
              <div className="pt-4 border-t border-zinc-100 flex items-center justify-between">
                <span className="text-[11px] text-zinc-500 font-medium">Diagnostic Lock</span>
                <button
                  onClick={() => handleCheckFit(m.mentor_id)}
                  className="px-4 py-2 bg-zinc-900 hover:bg-zinc-800 text-white rounded-xl text-xs font-semibold transition flex items-center space-x-1.5 shadow-sm"
                >
                  <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Assess Fit with AI</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-20 text-center bg-white rounded-3xl border border-zinc-200 p-8 space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-zinc-100 text-zinc-400 flex items-center justify-center mx-auto">
            <Users className="w-6 h-6" />
          </div>
          <p className="text-base font-semibold text-zinc-900">No mentors matched your search</p>
          <p className="text-xs sm:text-sm text-zinc-500 max-w-sm mx-auto">
            Try resetting your domain or tool filters to see all 50 verified mentors.
          </p>
        </div>
      )}
    </div>
  );
}
