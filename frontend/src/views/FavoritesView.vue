<template>
  <div class="animate-fade-in">
    <div class="mb-6"><h1 class="page-title">My Favorites</h1><p class="page-subtitle">Saved articles</p></div>

    <div v-if="!auth.isAuthenticated" class="soft-card p-10 text-center">
      <span class="text-4xl">🔒</span>
      <p class="mt-3 text-gray-500 dark:text-dark-muted-muted"><router-link to="/login" class="text-primary-500 font-medium">Sign in</router-link> to see favorites.</p>
    </div>

    <div v-else-if="loading" class="text-center py-20 text-gray-400 dark:text-dark-muted dark:text-dark-muted-muted">Loading...</div>

    <div v-else-if="favs.length > 0" class="space-y-3">
      <div v-for="f in favs" :key="f.id" class="soft-card p-4 flex items-start gap-3 hover:shadow-soft-hover transition">
        <div class="flex-1 min-w-0 cursor-pointer" @click="$router.push('/article/' + f.article_id)">
          <h3 class="text-sm font-semibold text-gray-800 line-clamp-2">{{ f.title }}</h3>
          <div class="flex gap-2 mt-1.5">
            <span class="tag-soft text-[10px]">{{ f.journal?.abbreviation }}</span>
            <span class="text-xs text-gray-400 dark:text-dark-muted dark:text-dark-muted-muted">{{ f.published_date }}</span>
          </div>
          <p class="text-xs text-gray-500 dark:text-dark-muted-muted mt-1 line-clamp-2">{{ f.abstract }}</p>
        </div>
        <button @click="unfav(f)" class="text-lg text-yellow-400 hover:text-red-400 transition">⭐</button>
      </div>
    </div>

    <div v-else class="soft-card p-10 text-center text-gray-400 dark:text-dark-muted dark:text-dark-muted-muted">
      <span class="text-4xl">⭐</span><p class="mt-2">No favorites yet. Browse literature to save articles.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getFavorites, removeFavorite } from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const favs = ref<any[]>([])
const loading = ref(true)

const load = async () => {
  try {
    const res = await getFavorites()
    favs.value = res.data.items
  } catch (e) { console.error(e) }
  loading.value = false
}

const unfav = async (f: any) => {
  await removeFavorite(f.article_id)
  favs.value = favs.value.filter(x => x.id !== f.id)
}

onMounted(load)
</script>
