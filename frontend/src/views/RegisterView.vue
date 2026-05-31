<template>
  <div class="min-h-screen flex bg-bg-primary dark:bg-dark-bg transition-colors">
    <div class="hidden lg:flex w-1/2 items-center justify-center p-12">
      <svg width="320" height="280" viewBox="0 0 320 280" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="180" cy="70" rx="80" ry="40" fill="#F0E8FA" opacity="0.5"/>
        <ellipse cx="100" cy="50" rx="50" ry="30" fill="#E8E4FF" class="dark:opacity-50" opacity="0.4"/>
        <ellipse cx="230" cy="45" rx="45" ry="25" fill="#D1CAFF" opacity="0.35"/>
        <circle cx="160" cy="170" r="12" fill="#F5A992" opacity="0.5"/>
        <circle cx="148" cy="158" r="7" fill="#F9D068" opacity="0.5"/>
        <circle cx="172" cy="158" r="7" fill="#F9D068" opacity="0.5"/>
        <path d="M0 250 Q80 185 160 250" fill="#D1CAFF" opacity="0.3"/>
        <path d="M120 250 Q200 180 280 250" fill="#E8E4FF" class="dark:opacity-50" opacity="0.25"/>
      </svg>
    </div>
    <div class="w-full lg:w-1/2 flex items-center justify-center p-12">
      <div class="w-full max-w-md">
        <div class="text-center mb-8"><h2 class="text-2xl font-bold text-gray-800 dark:text-dark-text">Create Account</h2><p class="text-gray-400 dark:text-dark-muted dark:text-dark-muted-muted text-sm mt-1">Join the UTD24 platform</p></div>
        <form class="soft-card p-6 space-y-4" @submit.prevent="doRegister">
          <div><label class="text-sm font-medium text-gray-600 dark:text-dark-muted dark:text-dark-muted-muted mb-1.5 block">Username</label><input v-model="form.username" type="text" class="input-soft" placeholder="researcher" /></div>
          <div><label class="text-sm font-medium text-gray-600 dark:text-dark-muted dark:text-dark-muted-muted mb-1.5 block">Email</label><input v-model="form.email" type="email" class="input-soft" placeholder="you@example.com" /></div>
          <div><label class="text-sm font-medium text-gray-600 dark:text-dark-muted dark:text-dark-muted-muted mb-1.5 block">Password</label><input v-model="form.password" type="password" class="input-soft" placeholder="Min. 8 characters" /></div>
          <p v-if="error" class="text-red-400 text-xs">{{ error }}</p>
          <button type="submit" class="btn-primary w-full !py-3" :disabled="loading">{{ loading ? 'Creating...' : 'Create Account' }}</button>
        </form>
        <p class="text-center mt-6 text-sm text-gray-400 dark:text-dark-muted dark:text-dark-muted-muted">Already have an account?
          <router-link to="/login" class="text-primary-500 font-medium hover:underline">Sign in</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ username: '', email: '', password: '' })
const loading = ref(false)
const error = ref('')

const doRegister = async () => {
  loading.value = true; error.value = ''
  try {
    const res = await register(form.value)
    auth.setAuth(res.data.access_token, res.data.user)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Registration failed'
  }
  loading.value = false
}
</script>
