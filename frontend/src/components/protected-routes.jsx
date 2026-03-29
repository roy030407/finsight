import useStore from "../store";
import { Navigate, Outlet } from "react-router-dom";
import Layout from "./layout";

function ProtectedRoute() {
  const { isAuthenticated, rehydrated, user } = useStore((state) => state.auth);

  // If still rehydrating, show nothing (or a loader/spinner)
  if (!rehydrated) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  return <Layout><Outlet /></Layout>;
}

export default ProtectedRoute;

// Component to redirect authenticated users away from auth pages
export function PublicRoute({ children }) {
  const { isAuthenticated, rehydrated } = useStore((state) => state.auth);

  // If still rehydrating, show nothing (or a loader/spinner)
  if (!rehydrated) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
