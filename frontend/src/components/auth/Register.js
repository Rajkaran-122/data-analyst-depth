import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { AnalyticsIcon } from '@/components/icons';

export function RegisterPage() {
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setLoading(true);
    
    try {
      await register(name, email, password);
      window.location.href = '/'; // Navigate to dashboard
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0F] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <AnalyticsIcon className="mx-auto h-12 w-12 text-[#10B981]" />
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-white">
          Create an account
        </h2>
        <p className="mt-2 text-center text-sm text-[#71717A]">
          Already have an account?{' '}
          <a href="/login" className="font-medium text-[#10B981] hover:text-[#34D399]">
            Sign in
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
              <label htmlFor="name" className="block text-sm font-medium text-white">
                Full Name
              </label>
              <div className="mt-1">
                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="block w-full appearance-none rounded-xl border border-[#2A2A3A] bg-[#1A1A24] px-3 py-2 text-white placeholder-[#71717A] focus:border-[#10B981] focus:outline-none focus:ring-[#10B981] sm:text-sm"
                />
              </div>
            </div>

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
                  className="block w-full appearance-none rounded-xl border border-[#2A2A3A] bg-[#1A1A24] px-3 py-2 text-white placeholder-[#71717A] focus:border-[#10B981] focus:outline-none focus:ring-[#10B981] sm:text-sm"
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
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full appearance-none rounded-xl border border-[#2A2A3A] bg-[#1A1A24] px-3 py-2 text-white placeholder-[#71717A] focus:border-[#10B981] focus:outline-none focus:ring-[#10B981] sm:text-sm"
                />
              </div>
              <p className="mt-2 text-xs text-[#71717A]">Must be at least 8 characters, 1 uppercase, 1 number, 1 symbol.</p>
            </div>

            <div>
              <label htmlFor="confirm-password" className="block text-sm font-medium text-white">
                Confirm Password
              </label>
              <div className="mt-1">
                <input
                  id="confirm-password"
                  name="confirm-password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="block w-full appearance-none rounded-xl border border-[#2A2A3A] bg-[#1A1A24] px-3 py-2 text-white placeholder-[#71717A] focus:border-[#10B981] focus:outline-none focus:ring-[#10B981] sm:text-sm"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="flex w-full justify-center rounded-xl bg-gradient-to-r from-[#10B981] to-[#34D399] py-2 px-4 text-sm font-medium text-white shadow-sm hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[#10B981] focus:ring-offset-2 disabled:opacity-50 transition-all"
              >
                {loading ? 'Creating account...' : 'Create account'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
