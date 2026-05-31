<template>
  <div class="animate-fade-in">
    <div class="mb-6"><h1 class="page-title">Settings</h1></div>
    <div class="soft-card p-6 space-y-4 max-w-lg">
      <div v-if="auth.isAuthenticated">
        <p class="text-sm text-gray-600 dark:text-dark-muted-muted"><strong>Username:</strong> {{ auth.user?.username }}</p>
        <p class="text-sm text-gray-600 dark:text-dark-muted-muted mt-1"><strong>Email:</strong> {{ auth.user?.email }}</p>
        <button @click="auth.logout(); $router.push('/login')" class="btn-primary mt-4 text-sm">Sign Out</button>
      </div>
      <div v-else class="text-center py-6">
        <p class="text-gray-400 dark:text-dark-muted dark:text-dark-muted-muted"><router-link to="/login" class="text-primary-500 font-medium">Sign in</router-link> to manage settings.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
</script>
