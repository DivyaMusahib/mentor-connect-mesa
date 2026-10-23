import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navigation from './components/Navigation';
import EvaluatorBanner from './components/EvaluatorBanner';

// Pages
import Login from './pages/Login';
import Overview from './pages/Overview';
import AiAdvisor from './pages/AiAdvisor';
import ExploreMentors from './pages/ExploreMentors';
import MySessions from './pages/MySessions';
import MeetingPreparation from './pages/MeetingPreparation';
import PostCallReportView from './pages/PostCallReportView';
import CareerRoadmap from './pages/CareerRoadmap';
import ProgressTracker from './pages/ProgressTracker';
import MesaAdmin from './pages/MesaAdmin';

// Guard: requires authentication
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAFAFA]">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-zinc-900 border-t-transparent animate-spin mx-auto" />
          <p className="text-xs text-zinc-500 font-medium">Verifying session...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Guard: student-only routes — redirect admins to /admin
function StudentRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === 'admin') return <Navigate to="/admin" replace />;

  return children;
}

// Guard: admin-only routes — redirect non-admins to /overview
function AdminRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== 'admin') return <Navigate to="/overview" replace />;

  return children;
}

function AppContent() {
  const { user } = useAuth();

  // Smart default redirect based on role
  const defaultRedirect = user?.role === 'admin' ? '/admin' : '/overview';

  return (
    <div className="min-h-screen flex flex-col bg-[#FAFAFA] text-zinc-900 font-sans selection:bg-zinc-900 selection:text-white">
      {/* Navigation */}
      <Navigation />

      {/* Floating Sandbox Widget */}
      <EvaluatorBanner />

      {/* Main Content */}
      <main className="flex-1 min-h-0">
        <Routes>
          <Route
            path="/login"
            element={user ? <Navigate to={defaultRedirect} replace /> : <Login />}
          />
          <Route path="/" element={<Navigate to={defaultRedirect} replace />} />

          {/* Student-only routes */}
          <Route path="/overview" element={<StudentRoute><Overview /></StudentRoute>} />
          <Route path="/advisor" element={<StudentRoute><AiAdvisor /></StudentRoute>} />
          <Route path="/mentors" element={<StudentRoute><ExploreMentors /></StudentRoute>} />
          <Route path="/sessions" element={<StudentRoute><MySessions /></StudentRoute>} />
          <Route path="/preparation" element={<StudentRoute><MeetingPreparation /></StudentRoute>} />
          <Route path="/report" element={<StudentRoute><PostCallReportView /></StudentRoute>} />
          <Route path="/roadmap" element={<StudentRoute><CareerRoadmap /></StudentRoute>} />
          <Route path="/progress" element={<StudentRoute><ProgressTracker /></StudentRoute>} />

          {/* Admin-only route */}
          <Route path="/admin" element={<AdminRoute><MesaAdmin /></AdminRoute>} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to={defaultRedirect} replace />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-200 bg-white py-6">
        <div className="max-w-7xl mx-auto px-6 lg:px-10 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-xs font-medium text-zinc-500">
            © 2026 Mesa School of Business — Mentor Connect
          </p>
          <p className="text-[11px] text-zinc-400">
            FastAPI · Gemini 2.5 Flash · n8n Cloud · Google OAuth
          </p>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}
