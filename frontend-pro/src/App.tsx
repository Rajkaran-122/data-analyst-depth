import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { useAuthStore } from '@/stores/authStore';
import { LoginPage } from '@/pages/LoginPage';
import DataStudioPage from '@/pages/DataStudioPage';

// Placeholder Pages
const DashboardPage = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold mb-4">Dashboard Overview</h1>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="p-6 bg-card rounded-lg border">
        <h3 className="text-lg font-semibold mb-2">Total Queries</h3>
        <p className="text-3xl font-bold text-primary">1,234</p>
      </div>
      <div className="p-6 bg-card rounded-lg border">
        <h3 className="text-lg font-semibold mb-2">Datasets</h3>
        <p className="text-3xl font-bold text-primary">56</p>
      </div>
      <div className="p-6 bg-card rounded-lg border">
        <h3 className="text-lg font-semibold mb-2">Active Users</h3>
        <p className="text-3xl font-bold text-primary">12</p>
      </div>
    </div>
  </div>
);

const DatasetsPage = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold">Datasets</h1>
    <p className="text-muted-foreground mt-2">Manage your connected datasets</p>
  </div>
);

const SettingsPage = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold">Settings</h1>
    <p className="text-muted-foreground mt-2">Configure your workspace preferences</p>
  </div>
);

// Config
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  // In production, enforce authentication
  // For development, you can bypass by always returning children
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={
                <ErrorBoundary>
                  <DashboardPage />
                </ErrorBoundary>
              } />
              <Route path="/studio" element={
                <ErrorBoundary>
                  <DataStudioPage />
                </ErrorBoundary>
              } />
              <Route path="/datasets" element={
                <ErrorBoundary>
                  <DatasetsPage />
                </ErrorBoundary>
              } />
              <Route path="/settings" element={
                <ErrorBoundary>
                  <SettingsPage />
                </ErrorBoundary>
              } />
            </Route>

            {/* Catch-all 404 */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;

