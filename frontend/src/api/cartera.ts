import { api } from "@/api/client";
import type { APIResponse, CarteraFactura, CarteraReporte, Gestion, Pago } from "@/types";

export async function listarCartera() {
  const { data } = await api.get<APIResponse<CarteraFactura[]>>("/cartera");
  return data.data;
}

export async function reporteCartera() {
  const { data } = await api.get<APIResponse<CarteraReporte>>("/cartera/reporte");
  return data.data;
}

export async function dashboardCartera() {
  const { data } = await api.get<
    APIResponse<{ cartera_total: number; facturas_vencidas: number; monto_vencido: number; dias_promedio_recaudo: number }>
  >("/cartera/dashboard");
  return data.data;
}

export interface PagoInput {
  factura_id: number;
  fecha_pago: string;
  monto: number;
  medio_pago?: string;
  referencia?: string;
  banco?: string;
  observaciones?: string;
}

export async function registrarPago(payload: PagoInput) {
  const { data } = await api.post<APIResponse<Pago>>("/cartera/pagos", payload);
  return data.data;
}

export async function historialPagos(factura_id?: number) {
  const { data } = await api.get<APIResponse<Pago[]>>("/cartera/pagos", { params: { factura_id } });
  return data.data;
}

export interface GestionInput {
  factura_id: number;
  tipo_gestion: string;
  resultado?: string;
  proxima_accion?: string;
  fecha_proxima?: string;
}

export async function registrarGestion(payload: GestionInput) {
  const { data } = await api.post<APIResponse<Gestion>>("/cartera/gestiones", payload);
  return data.data;
}

export async function gestionesDeFactura(factura_id: number) {
  const { data } = await api.get<APIResponse<Gestion[]>>(`/cartera/gestiones/${factura_id}`);
  return data.data;
}
