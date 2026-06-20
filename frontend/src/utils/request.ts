import axios, { AxiosError, type AxiosInstance } from "axios";
import router from "@/router";
import { storage } from "@/utils/storage";
import { ElMessage } from "element-plus";

const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";

const request: AxiosInstance = axios.create({
  baseURL: apiBase,
  timeout: 150000,
});

request.interceptors.request.use((config) => {
  const token = storage.getToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

request.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    if (error.response?.status === 401) {
      storage.clearToken();
      if (router.currentRoute.value.path !== "/login") {
        router.replace({ path: "/login", query: { redirect: router.currentRoute.value.fullPath } });
      }
    }
    const message = error.response?.data?.detail || error.message || "请求失败";
    ElMessage.error(message);
    return Promise.reject(error);
  }
);

export default request;
