import { api } from "@/api/client";
import type { APIResponse, Factura, FacturaItem, PaginatedResponse } from "@/types";

export interface FacturaItemInput {
  descripcion: string;
  cantidad: number;
  precio_unitario: number;
  descuento_pct?: number;
  tipo_residuo_id?: number;
}

export interface FacturaInput {
  servicio_id: number;
  fecha_vencimiento?: string;
  descuento?: number;
  condiciones_pago?: string;
  observaciones?: string;
  items: FacturaItemInput[];
}

export async function listarFacturas(params: { estado?: string; cliente_id?: number; vencimiento?: string; page?: number }) {
  const { data } = await api.get<APIResponse<PaginatedResponse<Factura>>>("/facturas", { params });
  return data.data;
}

export async function crearFactura(payload: FacturaInput) {
  const { data } = await api.post<APIResponse<Factura>>("/facturas", payload);
  return data.data;
}

export async function obtenerFactura(id: number) {
  const { data } = await api.get<APIResponse<Factura>>(`/facturas/${id}`);
  return data.data;
}

export async function cambiarEstadoFactura(id: number, estado_nuevo: string, nota?: string) {
  const { data } = await api.patch<APIResponse<Factura>>(`/facturas/${id}/estado`, { estado_nuevo, nota });
  return data.data;
}

export async function agregarItemFactura(id: number, payload: FacturaItemInput) {
  const { data } = await api.post<APIResponse<FacturaItem>>(`/facturas/${id}/items`, payload);
  return data.data;
}

export function rutaPdfFactura(id: number) {
  return `/facturas/${id}/pdf`;
}

export const SIGUIENTE_ESTADO_FACTURA: Record<string, string[]> = {
  borrador: ["emitida"],
  emitida: ["enviada"],
  enviada: ["parcialmente_pagada", "pagada", "vencida", "anulada"],
  parcialmente_pagada: ["pagada", "vencida"],
  vencida: ["pagada", "parcialmente_pagada"],
  pagada: [],
  anulada: [],
};
