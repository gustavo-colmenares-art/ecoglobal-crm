import { Navigate, Outlet } from "react-router-dom";

import { useAuthStore } from "@/store/auth";
import type { Rol } from "@/types";

interface Props {
  roles?: Rol[];
}

export default function ProtectedRoute({ roles }: Props) {
  const { token, user } = useAuthStore();

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }
  if (roles && (!user.rol || !roles.includes(user.rol.nombre))) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}
