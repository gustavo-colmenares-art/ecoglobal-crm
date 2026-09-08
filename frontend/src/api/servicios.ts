import { api } from "@/api/client";
import type { APIResponse, PaginatedResponse, Servicio, ServicioDetalle, ServicioHistorial } from "@/types";

export interface ServicioInput {
  cliente_id: number;
  fecha_programada?: string;
  descripcion?: string;
  direccion_servicio?: string;
  ciudad_servicio?: string;
  prioridad?: string;
  observaciones?: string;
}

export async function listarServicios(params: {
  estado?: string;
  cliente_id?: number;
  fecha?: string;
  prioridad?: string;
  page?: number;
}) {
  const { data } = await api.get<APIResponse<PaginatedResponse<Servicio>>>("/servicios", { params });
  return data.data;
}

export async function crearServicio(payload: ServicioInput) {
  const { data } = await api.post<APIResponse<Servicio>>("/servicios", payload);
  return data.data;
}

export async function obtenerServicio(id: number) {
  const { data } = await api.get<APIResponse<ServicioDetalle>>(`/servicios/${id}`);
  return data.data;
}

export async function actualizarServicio(id: number, payload: Partial<ServicioInput>) {
  const { data } = await api.put<APIResponse<Servicio>>(`/servicios/${id}`, payload);
  return data.data;
}

export async function cambiarEstadoServicio(id: number, estado_nuevo: string, nota: string) {
  const { data } = await api.patch<APIResponse<Servicio>>(`/servicios/${id}/estado`, { estado_nuevo, nota });
  return data.data;
}

export async function historialServicio(id: number) {
  const { data } = await api.get<APIResponse<ServicioHistorial[]>>(`/servicios/${id}/historial`);
  return data.data;
}

export const ETAPAS_SERVICIO = [
  "cotizado",
  "confirmado",
  "programado",
  "en_ruta",
  "atendido",
  "manifiesto_pendiente",
  "manifiesto_recibido",
  "completado",
  "cancelado",
];

export const SIGUIENTE_ESTADO: Record<string, string[]> = {
  cotizado: ["confirmado", "cancelado"],
  confirmado: ["programado", "cancelado"],
  programado: ["en_ruta", "cancelado"],
  en_ruta: ["atendido", "cancelado"],
  atendido: ["manifiesto_pendiente", "cancelado"],
  manifiesto_pendiente: ["manifiesto_recibido", "cancelado"],
  manifiesto_recibido: ["completado", "cancelado"],
  completado: [],
  cancelado: [],
};
