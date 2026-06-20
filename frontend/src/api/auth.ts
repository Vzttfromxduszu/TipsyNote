import request from "@/utils/request";
import type { TokenResponse } from "@/types/api";
import type { LoginPayload } from "@/types/user";

export const login = (payload: LoginPayload) =>
  request.post<TokenResponse>("/auth/login", payload).then((res) => res.data);
