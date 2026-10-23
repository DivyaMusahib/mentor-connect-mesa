import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, UserCheck, ArrowRight, Lock } from 'lucide-react';

export default function Login() {
  const { loginWithDemo } = useAuth();
  const navigate = useNavigate();
  const [loadingRole, setLoadingRole] = useState(null);
  const [error, setError] = useState(null);

  const handleDemoSignIn = async (role) => {
    setLoadingRole(role);
    setError(null);
    try {
      await loginWithDemo(role);
      navigate(role === 'admin' ? '/admin' : '/overview');
    } catch (err) {
      setError(err.message || 'Demo sign-in failed');
    } finally {
      setLoadingRole(null);
    }
  };

  const handleGoogleSignIn = () => {
    const apiBase = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
    window.location.href = `${apiBase}/api/v1/auth/google/login`;
  };

  return (
    <div className="min-h-[calc(100vh-72px)] flex flex-col justify-center items-center py-16 px-4 sm:px-6 lg:px-8 bg-[#FAFAFA]">
      <div className="max-w-md w-full space-y-8">
        {/* Brand header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-zinc-900 text-white flex items-center justify-center font-bold text-xl mx-auto shadow-sm mb-4">
            M
          </div>
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-zinc-900 tracking-tight">
            Sign in to Mentor Connect
          </h1>
          <p className="text-xs sm:text-sm text-zinc-600 font-medium">
            Mesa School of Business • Executive Mentorship Platform
          </p>
        </div>

        {error && (
          <div className="p-4 bg-red-50/80 border border-red-200/80 text-red-800 rounded-xl text-xs font-medium text-center">
            {error}
          </div>
        )}

        {/* Card */}
        <div className="bg-white p-7 sm:p-9 rounded-3xl border border-zinc-200/90 shadow-card space-y-7">
          {/* Google Sign-in */}
          <div>
            <button
              onClick={handleGoogleSignIn}
              className="w-full flex items-center justify-center space-x-3 py-3.5 px-4 bg-white border border-zinc-300 hover:border-zinc-400 hover:bg-zinc-50/70 rounded-2xl text-sm font-semibold text-zinc-800 transition shadow-subtle focus:ring-2 focus:ring-zinc-900 focus:outline-none"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>Continue with Google</span>
            </button>
            <p className="text-[11px] text-zinc-600 text-center mt-2.5">
              Secure OAuth 2.0 with cryptographic session tokens
            </p>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-zinc-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-3 text-zinc-500 font-semibold tracking-wider text-[10px]">
                or explore interactive demo
              </span>
            </div>
          </div>

          {/* Quick Demo Credentials */}
          <div className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                onClick={() => handleDemoSignIn('student')}
                disabled={loadingRole !== null}
                className="flex flex-col items-start p-4 bg-zinc-50 hover:bg-zinc-100/80 border border-zinc-200 rounded-2xl transition text-left group"
              >
                <div className="flex items-center space-x-2 text-xs font-bold text-zinc-900 mb-1">
                  <UserCheck className="w-4 h-4 text-emerald-700" />
                  <span>Mesa Student</span>
                </div>
                <span className="text-[11px] text-zinc-600 leading-snug">
                  Arjun Bansal • Test diagnostic matching and session booking.
                </span>
              </button>

              <button
                onClick={() => handleDemoSignIn('admin')}
                disabled={loadingRole !== null}
                className="flex flex-col items-start p-4 bg-zinc-50 hover:bg-zinc-100/80 border border-zinc-200 rounded-2xl transition text-left group"
              >
                <div className="flex items-center space-x-2 text-xs font-bold text-zinc-900 mb-1">
                  <ShieldCheck className="w-4 h-4 text-amber-700" />
                  <span>Mesa Admin</span>
                </div>
                <span className="text-[11px] text-zinc-600 leading-snug">
                  Administrator • Inspect cohort demand, outbox, and logs.
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="text-center text-xs text-zinc-600 space-y-1">
          <p className="flex items-center justify-center space-x-1.5">
            <Lock className="w-3.5 h-3.5 text-zinc-400" />
            <span>Session cookies protected via HttpOnly & SameSite flags</span>
          </p>
        </div>
      </div>
    </div>
  );
}
