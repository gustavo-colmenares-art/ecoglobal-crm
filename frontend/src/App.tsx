import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "@/components/AppLayout";
import ProtectedRoute from "@/components/ProtectedRoute";
import Cartera from "@/pages/Cartera";
import Clientes from "@/pages/Clientes";
import Configuracion from "@/pages/Configuracion";
import Dashboard from "@/pages/Dashboard";
import Declaraciones from "@/pages/Declaraciones";
import Facturacion from "@/pages/Facturacion";
import Login from "@/pages/Login";
import Manifiestos from "@/pages/Manifiestos";
import Servicios from "@/pages/Servicios";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clientes" element={<Clientes />} />
          <Route path="/servicios" element={<Servicios />} />
          <Route path="/manifiestos" element={<Manifiestos />} />
          <Route path="/declaraciones" element={<Declaraciones />} />
          <Route path="/facturacion" element={<Facturacion />} />
          <Route path="/cartera" element={<Cartera />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute roles={["superadmin"]} />}>
        <Route element={<AppLayout />}>
          <Route path="/configuracion" element={<Configuracion />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
