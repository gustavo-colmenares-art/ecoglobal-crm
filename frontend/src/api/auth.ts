import { api } from "@/api/client";
import type { APIResponse, Usuario } from "@/types";

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: Usuario;
}

export async function login(email: string, password: string) {
  const { data } = await api.post<APIResponse<TokenResponse>>("/auth/login", { email, password });
  return data.data;
}

export async function me() {
  const { data } = await api.get<APIResponse<Usuario>>("/auth/me");
  return data.data;
}
