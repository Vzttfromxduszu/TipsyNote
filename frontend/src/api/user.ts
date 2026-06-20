import request from "@/utils/request";
import type { RegisterPayload, SendCodePayload, UserProfile } from "@/types/user";

export const fetchMe = () => request.get<UserProfile>("/me").then((res) => res.data);

export const uploadAvatar = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  return request.post<{ avatar_url: string }>("/users/me/avatar", formData).then((res) => res.data);
};

export const sendCode = (payload: SendCodePayload) =>
  request.post<{ message: string }>("/auth/send-code", payload).then((res) => res.data);

export const registerUser = (payload: RegisterPayload) =>
  request.post<{ id: number; phone: string; nickname: string | null }>("/users", payload).then((res) => res.data);
