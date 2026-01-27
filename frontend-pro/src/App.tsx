import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { useAuthStore } from '@/stores/authStore';
import DataStudioPage from '@/pages/DataStudioPage';

// Placeholder Pages
const DashboardPage = () => <div className="p-8 text-2xl font-bold text-muted-foreground flex items-center justify-center h-full">Welcome to the Dashboard</div>;
const LoginPage = () => <div className="flex h-screen items-center justify-center text-xl">Login Page Placeholder</div>;

// Config
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  // For dev, bypass if needed or strictly enforce
  // return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
  return <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/studio" element={<DataStudioPage />} />
            <Route path="/datasets" element={<div>Datasets Page</div>} />
            <Route path="/settings" element={<div>Settings Page</div>} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
