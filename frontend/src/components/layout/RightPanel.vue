<template>
  <aside class="w-72 bg-white shadow-soft-lg p-5 overflow-y-auto hidden xl:block dark:bg-dark-card dark:border-l dark:border-dark-border transition-colors">
    <div class="soft-card p-4 mb-5">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-avatar bg-gradient-to-br from-primary-300 to-soft-orange flex items-center justify-center text-white font-semibold text-sm">{{ initial }}</div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-gray-800 truncate dark:text-dark-text">{{ auth.user?.display_name || 'Researcher' }}</p>
          <p class="text-xs text-gray-400 truncate dark:text-dark-muted">{{ auth.user?.email || 'Sign in to sync' }}</p>
        </div>
      </div>
    </div>
    <div class="gradient-card p-4 mb-5">
      <p class="text-white/80 text-xs font-medium mb-1">Summary</p>
      <div class="mt-3 flex gap-4">
        <div><p class="text-white/70 text-[10px]">Articles</p><p class="text-white text-xl font-bold">{{ summary.total_articles }}</p></div>
        <div><p class="text-white/70 text-[10px]">Authors</p><p class="text-white text-xl font-bold">{{ summary.total_authors }}</p></div>
      </div>
    </div>
    <div class="soft-card p-4">
      <h4 class="text-sm font-semibold text-gray-700 mb-3 dark:text-dark-text">Trending Keywords</h4>
      <div class="flex flex-wrap gap-2">
        <span v-for="kw in keywords" :key="kw.name" class="tag-soft cursor-pointer hover:bg-primary-200"
          @click="$router.push('/search?q=' + kw.name)">{{ kw.name }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getBISummary, getWordCloud } from '@/api'

const auth = useAuthStore()
const summary = ref({ total_articles: '—', total_authors: '—' })
const keywords = ref<any[]>([])
const initial = computed(() => (auth.user?.display_name || 'R')[0].toUpperCase())

onMounted(async () => {
  try {
    const [s, w] = await Promise.all([getBISummary(), getWordCloud(10)])
    summary.value = s.data
    keywords.value = w.data.slice(0, 10)
  } catch (e) { console.error(e) }
})
</script>
