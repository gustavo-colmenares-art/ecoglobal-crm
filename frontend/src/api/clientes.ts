import { api } from "@/api/client";
import type { APIResponse, Cliente, PaginatedResponse, Servicio } from "@/types";

export interface ClienteInput {
  razon_social: string;
  nit: string;
  direccion?: string;
  ciudad?: string;
  departamento?: string;
  telefono?: string;
  email?: string;
  contacto_nombre?: string;
  contacto_cargo?: string;
}

export async function listarClientes(params: { nombre?: string; nit?: string; ciudad?: string; page?: number; size?: number }) {
  const { data } = await api.get<APIResponse<PaginatedResponse<Cliente>>>("/clientes", { params });
  return data.data;
}

export async function crearCliente(payload: ClienteInput) {
  const { data } = await api.post<APIResponse<Cliente>>("/clientes", payload);
  return data.data;
}

export async function actualizarCliente(id: number, payload: Partial<ClienteInput> & { activo?: boolean }) {
  const { data } = await api.put<APIResponse<Cliente>>(`/clientes/${id}`, payload);
  return data.data;
}

export async function serviciosDeCliente(id: number) {
  const { data } = await api.get<APIResponse<Servicio[]>>(`/clientes/${id}/servicios`);
  return data.data;
}
