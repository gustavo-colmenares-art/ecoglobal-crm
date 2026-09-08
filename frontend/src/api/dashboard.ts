import { api } from "@/api/client";
import type { APIResponse } from "@/types";

export interface DashboardGeneral {
  total_clientes: number;
  servicios_activos: number;
  manifiestos_en_campo: number;
  facturas_vencidas: number;
  cartera_total: number;
}

export interface FlujoEtapa {
  estado: string;
  cantidad: number;
}

export interface AlertaItem {
  id: number;
  numero: string;
  fecha_recoleccion?: string | null;
  fecha_envio?: string | null;
  fecha_vencimiento?: string | null;
  total?: number;
}

export interface DashboardAlertas {
  manifiestos_demorados: AlertaItem[];
  declaraciones_sin_certificar: AlertaItem[];
  facturas_por_vencer: AlertaItem[];
  facturas_vencidas: AlertaItem[];
}

export interface ServiciosDashboard {
  por_estado: Record<string, number>;
  por_mes: Record<string, number>;
  total: number;
}

export async function getDashboardGeneral() {
  const { data } = await api.get<APIResponse<DashboardGeneral>>("/dashboard");
  return data.data;
}

export async function getDashboardFlujo() {
  const { data } = await api.get<APIResponse<FlujoEtapa[]>>("/dashboard/flujo");
  return data.data;
}

export async function getDashboardAlertas() {
  const { data } = await api.get<APIResponse<DashboardAlertas>>("/dashboard/alertas");
  return data.data;
}

export async function getServiciosDashboard() {
  const { data } = await api.get<APIResponse<ServiciosDashboard>>("/servicios/dashboard");
  return data.data;
}
