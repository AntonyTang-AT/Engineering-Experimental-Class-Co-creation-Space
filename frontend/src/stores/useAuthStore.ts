import { create } from "zustand";
import { persist } from "zustand/middleware";

import { SAMPLE_ACCOUNTS } from "../data/roster2501";

export type AuthRole = "student" | "admin";

export interface AuthUser {
  id: string;
  username: string | null;
  display_name: string;
  role: AuthRole | string;
}

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  setAuth: (token: string, user: AuthUser) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setAuth: (token, user) => set({ token, user }),
      clearAuth: () => set({ token: null, user: null }),
    }),
    { name: "gongke-auth" },
  ),
);

/** 样例账号：学号登录，密码为学号后六位 */
export const DEMO_ACCOUNTS = [
  ...SAMPLE_ACCOUNTS.map((account) => ({
    username: account.studentId,
    password: account.password,
    label: account.name,
    hint: account.hint,
  })),
  {
    username: "admin",
    password: "admin",
    label: "admin / admin",
    hint: "教学管理",
  },
] as const;
