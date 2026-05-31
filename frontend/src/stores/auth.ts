import { defineStore } from "pinia";
import { ref, computed } from "vue";
export const useAuthStore = defineStore("auth", () => {
  const token = ref<string|null>(localStorage.getItem("access_token"));
  const user = ref<any>(null);
  const isAuthenticated = computed(() => !!token.value);
  function setAuth(newToken: string, userData: any) { token.value=newToken; user.value=userData; localStorage.setItem("access_token",newToken); }
  function logout() { token.value=null; user.value=null; localStorage.removeItem("access_token"); }
  return { token, user, isAuthenticated, setAuth, logout };
});
