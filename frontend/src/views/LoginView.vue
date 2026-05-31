<template>
  <div class="min-h-screen flex bg-bg-primary dark:bg-dark-bg transition-colors">
    <div class="hidden lg:flex w-1/2 items-center justify-center p-12">
      <svg width="320" height="280" viewBox="0 0 320 280" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="160" cy="60" rx="90" ry="45" fill="#E8E4FF" class="dark:opacity-50" opacity="0.6"/>
        <ellipse cx="130" cy="45" rx="55" ry="35" fill="#D1CAFF" opacity="0.5"/>
        <ellipse cx="190" cy="45" rx="50" ry="30" fill="#C6B9FF" opacity="0.4"/>
        <ellipse cx="80" cy="130" rx="55" ry="30" fill="#F0E8FA" opacity="0.4"/>
        <ellipse cx="250" cy="110" rx="45" ry="25" fill="#E8E4FF" class="dark:opacity-50" opacity="0.4"/>
        <circle cx="140" cy="190" r="10" fill="#C6B9FF" opacity="0.6"/>
        <circle cx="130" cy="180" r="6" fill="#E8E4FF" class="dark:opacity-50" opacity="0.6"/>
        <circle cx="150" cy="180" r="6" fill="#E8E4FF" class="dark:opacity-50" opacity="0.6"/>
        <path d="M0 250 Q60 190 120 250" fill="#E8E4FF" class="dark:opacity-50" opacity="0.35"/>
        <path d="M60 250 Q130 175 200 250" fill="#D1CAFF" opacity="0.3"/>
        <path d="M140 250 Q210 185 280 250" fill="#E8E4FF" class="dark:opacity-50" opacity="0.25"/>
        <circle cx="100" cy="30" r="2" fill="#F9D068" opacity="0.6"/>
        <circle cx="220" cy="25" r="2.5" fill="#F9D068" opacity="0.5"/>
      </svg>
    </div>
    <div class="w-full lg:w-1/2 flex items-center justify-center p-12">
      <div class="w-full max-w-md">
        <div class="text-center mb-8">
          <div class="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-glow mb-4">
            <span class="text-white font-bold text-2xl">U</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 dark:text-dark-text">Welcome Back</h2>
          <p class="text-gray-400 dark:text-dark-muted dark:text-dark-muted-muted text-sm mt-1">Sign in to your account</p>
        </div>
        <form class="soft-card p-6 space-y-4" @submit.prevent="doLogin">
          <div><label class="text-sm font-medium text-gray-600 dark:text-dark-muted dark:text-dark-muted-muted mb-1.5 block">Email or Username</label>
            <input v-model="form.username" type="text" class="input-soft" placeholder="you@example.com" /></div>
          <div><label class="text-sm font-medium text-gray-600 dark:text-dark-muted dark:text-dark-muted-muted mb-1.5 block">Password</label>
            <input v-model="form.password" type="password" class="input-soft" placeholder="........" /></div>
          <p v-if="error" class="text-red-400 text-xs">{{ error }}</p>
          <button type="submit" class="btn-primary w-full !py-3" :disabled="loading">{{ loading ? 'Signing in...' : 'Sign In' }}</button>
        </form>
        <p class="text-center mt-6 text-sm text-gray-400 dark:text-dark-muted dark:text-dark-muted-muted">Don't have an account?
          <router-link to="/register" class="text-primary-500 font-medium hover:underline">Create one</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

const doLogin = async () => {
  loading.value = true; error.value = ''
  try {
    const res = await login({ username_or_email: form.value.username, password: form.value.password })
    auth.setAuth(res.data.access_token, res.data.user)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Login failed'
  }
  loading.value = false
}
</script>
