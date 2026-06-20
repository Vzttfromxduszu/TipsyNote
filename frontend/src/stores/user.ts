import { defineStore } from "pinia";
import type { LoginPayload, UserProfile } from "@/types/user";
import { login } from "@/api/auth";
import { fetchMe } from "@/api/user";
import { storage } from "@/utils/storage";

interface UserState {
  token: string | null;
  profile: UserProfile | null;
  loading: boolean;
}

export const useUserStore = defineStore("user", {
  state: (): UserState => ({
    token: storage.getToken(),
    profile: null,
    loading: false,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
  },
  actions: {
    async login(payload: LoginPayload) {
      this.loading = true;
      try {
        const data = await login(payload);
        this.token = data.access_token;
        storage.setToken(data.access_token);
        await this.fetchProfile();
      } finally {
        this.loading = false;
      }
    },
    async fetchProfile() {
      if (!this.token) {
        this.profile = null;
        return;
      }
      this.profile = await fetchMe();
    },
    logout() {
      this.token = null;
      this.profile = null;
      storage.clearToken();
    },
  },
});
