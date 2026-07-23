import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-slate-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center text-white font-bold text-sm group-hover:scale-110 transition-transform">
              CG
            </div>
            <span className="text-lg font-semibold text-slate-100 hidden sm:block">
              CGMS
            </span>
          </Link>

          {/* Right side */}
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              <Link
                to="/grievances/new"
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-indigo-600 text-white text-sm font-medium hover:from-indigo-600 hover:to-indigo-700 transition-all shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40"
              >
                + New Grievance
              </Link>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm font-medium text-indigo-300">
                  {user?.full_name?.[0]?.toUpperCase() || '?'}
                </div>
                <span className="text-sm text-slate-300 hidden sm:block">
                  {user?.full_name}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-slate-400 hover:text-slate-200 transition-colors ml-2"
                  aria-label="Log out"
                >
                  Logout
                </button>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="text-sm text-slate-300 hover:text-white transition-colors"
              >
                Log In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-lg bg-indigo-500 text-white text-sm font-medium hover:bg-indigo-600 transition-colors"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
