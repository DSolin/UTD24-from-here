<template>
  <aside class="w-[72px] flex flex-col items-center py-6 gap-2 bg-white shadow-soft-lg z-10">
    <router-link to="/" class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center mb-6 shadow-glow">
      <span class="text-white font-bold text-lg">U</span>
    </router-link>
    <nav class="flex flex-col gap-1 w-full px-3">
      <NavItem v-for="item in navItems" :key="item.to" :icon="item.icon" :label="item.label" :to="item.to" />
    </nav>
    <div class="mt-auto flex flex-col gap-1 w-full px-3">
      <NavItem v-if="!auth.isAuthenticated" icon="🔑" label="Login" to="/login" />
      <NavItem v-else icon="⚙️" label="Settings" to="/settings" />
    </div>
  </aside>
</template>

<script setup lang="ts">
import NavItem from "./NavItem.vue";
import { useAuthStore } from "@/stores/auth";
const auth = useAuthStore();
const navItems = [
  { icon: "📊", label: "Dashboard", to: "/dashboard" },
  { icon: "📚", label: "Literature", to: "/literature" },
  { icon: "🔍", label: "Search", to: "/search" },
  { icon: "⭐", label: "Favorites", to: "/favorites" },
];
</script>
