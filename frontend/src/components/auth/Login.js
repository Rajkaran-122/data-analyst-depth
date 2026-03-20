import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { AnalyticsIcon } from '@/components/icons';

export function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      await login(email, password);
      window.location.href = '/'; // Navigate to dashboard
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to sign in. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0F] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <AnalyticsIcon className="mx-auto h-12 w-12 text-[#3B82F6]" />
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-white">
          Sign in to Data Bridge
        </h2>
        <p className="mt-2 text-center text-sm text-[#71717A]">
          Or{' '}
          <a href="/register" className="font-medium text-[#3B82F6] hover:text-[#60A5FA]">
            create a new account
          </a>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-[#12121A] py-8 px-4 shadow sm:rounded-2xl sm:px-10 border border-[#1E1E2A]">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg p-3">
                <p className="text-sm text-[#EF4444] text-center">{error}</p>
              </div>
            )}
            
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-white">
                Email address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full appearance-none rounded-xl border border-[#2A2A3A] bg-[#1A1A24] px-3 py-2 text-white placeholder-[#71717A] focus:border-[#3B82F6] focus:outline-none focus:ring-[#3B82F6] sm:text-sm"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-white">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full appearance-none rounded-xl border border-[#2A2A3A] bg-[#1A1A24] px-3 py-2 text-white placeholder-[#71717A] focus:border-[#3B82F6] focus:outline-none focus:ring-[#3B82F6] sm:text-sm"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 rounded border-[#2A2A3A] bg-[#1A1A24] text-[#3B82F6] focus:ring-[#3B82F6]"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-[#71717A]">
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <a href="/login" className="font-medium text-[#3B82F6] hover:text-[#60A5FA]">
                  Forgot your password?
                </a>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="flex w-full justify-center rounded-xl bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] py-2 px-4 text-sm font-medium text-white shadow-sm hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[#3B82F6] focus:ring-offset-2 disabled:opacity-50 transition-all"
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>
            
            <div className="mt-4 pt-4 border-t border-[#1E1E2A] text-center">
              <p className="text-xs text-[#71717A]">
                <strong>Admin login:</strong> admin@dataanalyst.com / Admin@123
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
