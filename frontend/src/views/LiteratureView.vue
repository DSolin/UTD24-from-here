<template>
  <div class="animate-fade-in">
    <div class="mb-6"><h1 class="page-title">Literature</h1><p class="page-subtitle">Latest articles from UTD24 journals</p></div>

    <div class="soft-card p-4 mb-5 flex flex-wrap gap-3 items-center">
      <select v-model="filters.journal" class="input-soft w-48 text-sm">
        <option value="">All Journals</option>
        <option v-for="j in journals" :key="j.id" :value="j.id">{{ j.abbreviation }}</option>
      </select>
      <input v-model="filters.query" class="input-soft flex-1 min-w-[180px] text-sm" placeholder="Search title, keyword..." @keyup.enter="search" />
      <button @click="search" class="btn-primary text-sm">Search</button>
      <button @click="reset" class="btn-ghost text-sm">Reset</button>
      <button @click="exportCSV" class="btn-ghost text-sm ml-auto">Export CSV</button>
    </div>

    <div v-if="loading" class="text-center py-20 text-gray-400">
      <div class="animate-spin w-8 h-8 mx-auto mb-3 border-2 border-primary-300 border-t-primary-500 rounded-full"></div>
      Loading...
    </div>

    <div v-else-if="articles.length > 0" class="space-y-3">
      <div v-for="a in articles" :key="a.id" class="soft-card p-4 hover:shadow-soft-hover transition flex items-start gap-3">
        <div class="flex-1 min-w-0 cursor-pointer" @click="goDetail(a.id)">
          <h3 class="text-sm font-semibold text-gray-800 leading-snug line-clamp-2">{{ a.title }}</h3>
          <div class="flex flex-wrap items-center gap-2 mt-2">
            <span class="tag-soft text-[10px]">{{ a.journal?.abbreviation || '?' }}</span>
            <span class="text-xs text-gray-400">{{ a.published_date }}</span>
          </div>
          <p class="text-xs text-gray-500 mt-1.5 line-clamp-2">{{ a.abstract }}</p>
          <div class="flex flex-wrap gap-1 mt-1.5">
            <span v-for="au in a.authors?.slice(0, 4)" :key="au.id" class="text-[10px] text-primary-400">{{ au.name }}</span>
          </div>
        </div>
        <button @click.stop="toggleFav(a)" class="text-xl transition hover:scale-125 flex-shrink-0 mt-1"
          :class="favSet.has(a.id) ? 'text-yellow-400' : 'text-gray-300'"
          :title="favSet.has(a.id) ? 'Remove favorite' : 'Add favorite'">
          {{ favSet.has(a.id) ? '\u2B50' : '\u2606' }}
        </button>
      </div>
    </div>

    <div v-else class="soft-card p-12 text-center text-gray-400">
      <span class="text-4xl">\u{1F4ED}</span><p class="mt-2">No articles found.</p>
    </div>

    <div v-if="totalPages > 1" class="flex justify-center items-center gap-1 mt-6">
      <!-- Prev -->
      <button @click="goPage(page - 1)" :disabled="page <= 1"
        class="w-9 h-9 rounded-lg text-sm font-medium transition"
        :class="page <= 1 ? 'text-gray-300 cursor-not-allowed pointer-events-none' : 'bg-white text-gray-500 hover:bg-soft-pink'">‹</button>

      <!-- Page numbers with ellipsis -->
      <template v-for="(p, idx) in visiblePages" :key="idx">
        <button v-if="p !== '...'" @click="goPage(p as any)"
          class="w-9 h-9 rounded-lg text-sm font-medium transition"
          :class="p === page ? 'bg-primary-500 text-white' : 'bg-white text-gray-500 hover:bg-soft-pink'">{{ p }}</button>
        <span v-else class="w-9 h-9 flex items-center justify-center text-gray-400 text-sm select-none">…</span>
      </template>

      <!-- Next -->
      <button @click="goPage(page + 1)" :disabled="page >= totalPages"
        class="w-9 h-9 rounded-lg text-sm font-medium transition"
        :class="page >= totalPages ? 'text-gray-300 cursor-not-allowed pointer-events-none' : 'bg-white text-gray-500 hover:bg-soft-pink'">›</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticles, getJournalsStats, getFavorites, addFavorite, removeFavorite } from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const articles = ref<any[]>([])
const journals = ref<any[]>([])
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const pageSize = 20
const totalPages = ref(1)
const filters = ref({ query: '', journal: '', author: '' })
const favSet = ref(new Set<string>())

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const total = totalPages.value
  const current = page.value
  const delta = 2
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current - delta > 2) pages.push('...')
    const start = Math.max(2, current - delta)
    const end = Math.min(total - 1, current + delta)
    for (let i = start; i <= end; i++) pages.push(i)
    if (current + delta < total - 1) pages.push('...')
    pages.push(total)
  }
  return pages
})

const load = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize, sort_by: 'published_date', sort_order: 'desc' }
    if (filters.value.query) params.query = filters.value.query
    if (filters.value.journal) params.journal_id = filters.value.journal
    if (filters.value.author) params.author = filters.value.author
    const res = await getArticles(params)
    articles.value = res.data.items
    total.value = res.data.total
    totalPages.value = Math.ceil(res.data.total / pageSize)
  } catch (e) { console.error(e) }
  loading.value = false
}

const search = () => { page.value = 1; load() }
const reset = () => { filters.value = { query: '', journal: '', author: '' }; page.value = 1; load() }
const goPage = (p: number) => { page.value = p; load(); window.scrollTo(0, 0) }
const goDetail = (id: string) => router.push('/article/' + id)

const loadFavs = async () => {
  if (!auth.isAuthenticated) return
  try {
    const res = await getFavorites()
    favSet.value = new Set(res.data.items.map((i: any) => i.article_id))
  } catch (e) { /* ignore */ }
}

const toggleFav = async (a: any) => {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  try {
    if (favSet.value.has(a.id)) {
      await removeFavorite(a.id)
      favSet.value.delete(a.id)
    } else {
      await addFavorite(a.id)
      favSet.value.add(a.id)
    }
  } catch (e) { console.error(e) }
}

const exportCSV = () => {
  const params = new URLSearchParams()
  if (filters.value.query) params.set('query', filters.value.query)
  if (filters.value.journal) params.set('journal_id', filters.value.journal)
  if (filters.value.author) params.set('author', filters.value.author)
  window.open('/api/v1/articles/export/csv?' + params.toString(), '_blank')
}

onMounted(async () => {
  const jr = await getJournalsStats()
  journals.value = jr.data
  // 从 URL 读取作者参数
  if (route.query.author) { filters.value.author = route.query.author as string }
  await load()
  await loadFavs()
})
</script>
