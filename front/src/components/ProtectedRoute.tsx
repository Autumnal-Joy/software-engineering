import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./UserManager";

export const ProtectedRoute = () => {
  const auth = useAuth();
  if (!auth.userAuth.username) {
    return <Navigate to="/" />;
  }
  return <Outlet />;
};
