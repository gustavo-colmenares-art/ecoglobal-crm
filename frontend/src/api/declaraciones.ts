import { api } from "@/api/client";
import type { APIResponse, Declaracion, PaginatedResponse } from "@/types";

export interface DeclaracionInput {
  manifiesto_id: number;
  planta_id: number;
  fecha_envio?: string;
  observaciones?: string;
}

export async function listarDeclaraciones(params: { estado?: string; planta_id?: number; manifiesto_id?: number; page?: number }) {
  const { data } = await api.get<APIResponse<PaginatedResponse<Declaracion>>>("/declaraciones", { params });
  return data.data;
}

export async function crearDeclaracion(payload: DeclaracionInput) {
  const { data } = await api.post<APIResponse<Declaracion>>("/declaraciones", payload);
  return data.data;
}

export async function actualizarDeclaracion(id: number, payload: Partial<DeclaracionInput>) {
  const { data } = await api.put<APIResponse<Declaracion>>(`/declaraciones/${id}`, payload);
  return data.data;
}

export async function cambiarEstadoDeclaracion(id: number, estado_nuevo: string, nota?: string) {
  const { data } = await api.patch<APIResponse<Declaracion>>(`/declaraciones/${id}/estado`, { estado_nuevo, nota });
  return data.data;
}

export async function certificarDeclaracion(id: number, numero_certificado: string, fecha_certificacion: string) {
  const { data } = await api.post<APIResponse<Declaracion>>(`/declaraciones/${id}/certificar`, {
    numero_certificado,
    fecha_certificacion,
  });
  return data.data;
}

export const SIGUIENTE_ESTADO_DECLARACION: Record<string, string[]> = {
  pendiente: ["enviada"],
  enviada: ["certificada", "rechazada"],
  certificada: [],
  rechazada: ["pendiente"],
};
