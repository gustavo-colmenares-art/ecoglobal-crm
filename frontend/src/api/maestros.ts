import { api } from "@/api/client";
import type { APIResponse, PaginatedResponse, Planta, Rol, TipoResiduo, Usuario } from "@/types";

export interface RolOut {
  id: number;
  nombre: Rol;
  descripcion: string | null;
}

export async function listarRoles() {
  const { data } = await api.get<APIResponse<RolOut[]>>("/roles");
  return data.data;
}

// Tipos de residuo
export async function listarResiduos() {
  const { data } = await api.get<APIResponse<TipoResiduo[]>>("/residuos");
  return data.data;
}
export async function crearResiduo(payload: Partial<TipoResiduo>) {
  const { data } = await api.post<APIResponse<TipoResiduo>>("/residuos", payload);
  return data.data;
}
export async function actualizarResiduo(id: number, payload: Partial<TipoResiduo>) {
  const { data } = await api.put<APIResponse<TipoResiduo>>(`/residuos/${id}`, payload);
  return data.data;
}

// Plantas certificadoras
export async function listarPlantas() {
  const { data } = await api.get<APIResponse<Planta[]>>("/plantas");
  return data.data;
}
export async function crearPlanta(payload: Partial<Planta>) {
  const { data } = await api.post<APIResponse<Planta>>("/plantas", payload);
  return data.data;
}
export async function actualizarPlanta(id: number, payload: Partial<Planta>) {
  const { data } = await api.put<APIResponse<Planta>>(`/plantas/${id}`, payload);
  return data.data;
}

// Usuarios
export async function listarUsuarios(page = 1) {
  const { data } = await api.get<APIResponse<PaginatedResponse<Usuario>>>("/usuarios", { params: { page } });
  return data.data;
}
export interface UsuarioInput {
  nombre: string;
  email: string;
  password: string;
  rol_id: number;
}
export async function crearUsuario(payload: UsuarioInput) {
  const { data } = await api.post<APIResponse<Usuario>>("/usuarios", payload);
  return data.data;
}
export async function actualizarUsuario(id: number, payload: Partial<{ nombre: string; email: string; rol_id: number; activo: boolean }>) {
  const { data } = await api.put<APIResponse<Usuario>>(`/usuarios/${id}`, payload);
  return data.data;
}
export async function desactivarUsuario(id: number) {
  await api.delete(`/usuarios/${id}`);
}
