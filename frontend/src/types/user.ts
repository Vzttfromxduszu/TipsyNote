import type { PubInfo } from "./pubs";

export interface UserProfile {
  id: number;
  phone: string;
  nickname: string | null;
  avatar_url: string | null;
  role: number;
  status: number;
  managed_pubs: PubInfo[];
}

export interface LoginPayload {
  phone: string;
  secret: string;
}

export interface SendCodePayload {
  phone: string;
}

export interface RegisterPayload {
  phone: string;
  secret: string;
  code: string;
  nickname?: string;
}
