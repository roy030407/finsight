import useStore from "./store";
import DashboardPage from "./pages/home";
import SummaryPage from "./pages/summary";
import Home from "./pages/LandingPage";
import Optimise from "./pages/OptimisePage";
import GrowPage from "./pages/Grow";
import AIChatPage from "./pages/AIChat";
import { useEffect } from "react";
import LoginPage from "./pages/login";
import SignupPage from "./pages/signup";
import ProtectedRoute, { PublicRoute } from "./components/protected-routes";
import { ThemeProvider } from "./components/theme-provider";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import Layout from "./components/layout";

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
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
            <Route path="/signup" element={<PublicRoute><SignupPage /></PublicRoute>} />
            
            {/* Protected routes */}
            <Route path="/" element={<ProtectedRoute />}>
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="summary" element={<SummaryPage />} />
              <Route path="optimise" element={<Optimise />} />
              <Route path="grow" element={<GrowPage />} />
              <Route path="chat" element={<AIChatPage />} />
            </Route>
            
            {/* Legacy redirects */}
            <Route path="/ai-chat" element={<Navigate to="/chat" replace />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;