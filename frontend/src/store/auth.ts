import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { Usuario } from "@/types";

interface AuthState {
  token: string | null;
  user: Usuario | null;
  setSession: (token: string, user: Usuario) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setSession: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
    }),
    { name: "ecoglobal-auth" },
  ),
);
