import { api } from "@/api/client";
import type { APIResponse, Manifiesto, ManifiestoItem, PaginatedResponse } from "@/types";

export interface ManifiestoItemInput {
  tipo_residuo_id: number;
  cantidad_declarada?: number;
  unidad_medida?: string;
  descripcion_adicional?: string;
  numero_contenedor?: string;
  observaciones?: string;
}

export interface ManifiestoInput {
  servicio_id: number;
  operario_id?: number;
  fecha_recoleccion?: string;
  observaciones_campo?: string;
  items: ManifiestoItemInput[];
}

export async function listarManifiestos(params: { estado?: string; operario_id?: number; fecha?: string; page?: number }) {
  const { data } = await api.get<APIResponse<PaginatedResponse<Manifiesto>>>("/manifiestos", { params });
  return data.data;
}

export async function crearManifiesto(payload: ManifiestoInput) {
  const { data } = await api.post<APIResponse<Manifiesto>>("/manifiestos", payload);
  return data.data;
}

export async function obtenerManifiesto(id: number) {
  const { data } = await api.get<APIResponse<Manifiesto>>(`/manifiestos/${id}`);
  return data.data;
}

export async function actualizarManifiesto(id: number, payload: Partial<Manifiesto>) {
  const { data } = await api.put<APIResponse<Manifiesto>>(`/manifiestos/${id}`, payload);
  return data.data;
}

export async function cambiarEstadoManifiesto(id: number, estado_nuevo: string, nota: string) {
  const { data } = await api.patch<APIResponse<Manifiesto>>(`/manifiestos/${id}/estado`, { estado_nuevo, nota });
  return data.data;
}

export async function agregarItemManifiesto(id: number, payload: ManifiestoItemInput) {
  const { data } = await api.post<APIResponse<ManifiestoItem>>(`/manifiestos/${id}/items`, payload);
  return data.data;
}

export async function actualizarItemManifiesto(id: number, itemId: number, payload: Partial<ManifiestoItem>) {
  const { data } = await api.put<APIResponse<ManifiestoItem>>(`/manifiestos/${id}/items/${itemId}`, payload);
  return data.data;
}

export function rutaPdfManifiesto(id: number) {
  return `/manifiestos/${id}/pdf`;
}

export const SIGUIENTE_ESTADO_MANIFIESTO: Record<string, string[]> = {
  generado: ["en_campo"],
  en_campo: ["recibido"],
  recibido: ["declarado"],
  declarado: ["cerrado"],
  cerrado: [],
};
