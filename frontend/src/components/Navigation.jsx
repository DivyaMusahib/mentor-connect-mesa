import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Sparkles,
  Users,
  Calendar,
  Compass,
  ShieldCheck,
  LogOut,
  Menu,
  X
} from 'lucide-react';

const STUDENT_NAV = [
  { name: 'Dashboard', to: '/overview', icon: LayoutDashboard },
  { name: 'AI Advisor', to: '/advisor', icon: Sparkles },
  { name: 'Explore Mentors', to: '/mentors', icon: Users },
  { name: 'My Sessions', to: '/sessions', icon: Calendar },
  { name: 'Career Roadmap', to: '/roadmap', icon: Compass },
];

const ADMIN_NAV = [
  { name: 'Admin Console', to: '/admin', icon: ShieldCheck },
];

export default function Navigation() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = user?.role === 'admin' ? ADMIN_NAV : STUDENT_NAV;

  return (
    <header className="sticky top-0 z-40 bg-white/96 backdrop-blur-sm border-b border-zinc-200">
      <div className="max-w-7xl mx-auto px-6 lg:px-10">
        <div className="flex items-center justify-between h-16">

          {/* Brand */}
          <NavLink
            to={user?.role === 'admin' ? '/admin' : '/overview'}
            className="flex items-center gap-3 group flex-shrink-0"
          >
            <div className="w-9 h-9 rounded-xl bg-zinc-900 flex items-center justify-center text-white font-bold text-sm shadow-sm group-hover:bg-zinc-800 transition-colors">
              M
            </div>
            <div className="flex flex-col leading-tight">
              <span className="font-semibold text-zinc-900 text-sm tracking-tight">
                Mentor Connect
              </span>
              <span className="text-[10px] text-zinc-500 font-medium tracking-wide">
                Mesa School of Business
              </span>
            </div>
          </NavLink>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.name}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-zinc-900 text-white'
                        : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>

          {/* Right: User */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2.5 pl-3 border-l border-zinc-200">
                  <div className="w-8 h-8 rounded-full bg-zinc-100 border border-zinc-200 flex items-center justify-center font-semibold text-xs text-zinc-800 flex-shrink-0">
                    {user.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt={user.full_name}
                        className="w-full h-full rounded-full object-cover"
                      />
                    ) : (
                      user.full_name?.substring(0, 2).toUpperCase() || 'ME'
                    )}
                  </div>
                  <div className="flex flex-col text-left min-w-0">
                    <span className="text-xs font-semibold text-zinc-900 leading-tight truncate max-w-[120px]">
                      {user.full_name}
                    </span>
                    <span className="text-[10px] text-zinc-500">
                      {user.role === 'admin' ? 'Administrator' : 'Mesa Fellow'}
                    </span>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  title="Sign out"
                  className="p-2 text-zinc-400 hover:text-zinc-700 hover:bg-zinc-100 rounded-lg transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <NavLink
                to="/login"
                className="px-4 py-2 bg-zinc-900 hover:bg-zinc-800 text-white rounded-lg text-xs font-semibold transition-colors"
              >
                Sign In
              </NavLink>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100 transition-colors"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-zinc-200 bg-white px-6 py-4 space-y-1 shadow-lg">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.to}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors ${
                    isActive ? 'bg-zinc-900 text-white' : 'text-zinc-700 hover:bg-zinc-100'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
          {user && (
            <div className="pt-4 mt-3 border-t border-zinc-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-zinc-100 flex items-center justify-center text-xs font-semibold text-zinc-700">
                  {user.full_name?.substring(0, 2).toUpperCase() || 'ME'}
                </div>
                <span className="text-xs font-semibold text-zinc-800">{user.full_name}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-red-600 font-medium transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
