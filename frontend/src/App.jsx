import useStore from "./store";
import DashboardPage from "./pages/home";
import SummaryPage from "./pages/summary";
import Home from "./pages/Home";
import OptimisePage from "./pages/OptimisePage";
import GrowPage from "./pages/Grow";
import { useEffect } from "react";
import LoginPage from "./pages/login";
import SignupPage from "./pages/signup";
import ReportsPage from "./pages/reports";
import SettingsPage from "./pages/settings";
import TransactionsPage from "./pages/transactions";
import CategoriesPage from "./pages/categories/categories";
import ProtectedRoute from "./components/protected-routes";
import { ThemeProvider } from "./components/theme-provider";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const rehydrateAuth = useStore((state) => state.rehydrateAuth);

  useEffect(() => {
    rehydrateAuth();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/transactions"
              element={
                <ProtectedRoute>
                  <TransactionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/optimise"
              element={
                <ProtectedRoute>
                  <OptimisePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/categories"
              element={
                <ProtectedRoute>
                  <CategoriesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <ReportsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/summary"
              element={
                <ProtectedRoute>
                  <SummaryPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/grow"
              element={
                <ProtectedRoute>
                  <GrowPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;