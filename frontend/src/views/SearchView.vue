<template>
  <div class="animate-fade-in">
    <div class="mb-6"><h1 class="page-title">Advanced Search</h1><p class="page-subtitle">Search across UTD24 literature</p></div>

    <div class="soft-card p-6 max-w-3xl mb-6">
      <div class="space-y-4">
        <div><label class="text-sm font-medium text-gray-600 mb-1.5 block">Keywords / Title</label>
          <input v-model="f.query" class="input-soft" placeholder="Enter keywords or title..." @keyup.enter="doSearch()" /></div>
        <div class="grid grid-cols-3 gap-4">
          <div><label class="text-sm font-medium text-gray-600 mb-1.5 block">Author</label>
            <input v-model="f.author" class="input-soft" placeholder="Author name..." @keyup.enter="doSearch()" /></div>
          <div><label class="text-sm font-medium text-gray-600 mb-1.5 block">Journal</label>
            <select v-model="f.journal" class="input-soft"><option value="">All Journals</option><option v-for="j in journals" :key="j.id" :value="j.id">{{ j.abbreviation }}</option></select></div>
          <div><label class="text-sm font-medium text-gray-600 mb-1.5 block">Country</label>
            <input v-model="f.country" class="input-soft" placeholder="e.g. USA, China..." /></div>
        </div>
        <div class="flex gap-3 pt-2"><button @click="doSearch()" class="btn-primary">Search</button><button @click="reset" class="btn-ghost">Reset</button></div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-16">
      <div class="animate-spin w-8 h-8 mx-auto mb-3 border-2 border-primary-300 border-t-primary-500 rounded-full"></div>
      <p class="text-gray-400 text-sm">Searching...</p>
    </div>

    <div v-else-if="results.length > 0">
      <p class="text-sm text-gray-400 mb-3">{{ total }} results found</p>
      <div class="space-y-3">
        <div v-for="a in results" :key="a.id" class="soft-card p-4 cursor-pointer hover:shadow-soft-hover" @click="$router.push('/article/' + a.id)">
          <h3 class="text-sm font-semibold text-gray-800 line-clamp-2">{{ a.title }}</h3>
          <div class="flex gap-2 mt-1.5">
            <span class="tag-soft text-[10px]">{{ a.journal?.abbreviation }}</span>
            <span class="text-xs text-gray-400">{{ a.published_date }}</span>
          </div>
          <p class="text-xs text-gray-500 mt-1 line-clamp-2">{{ a.abstract }}</p>
          <div class="flex flex-wrap gap-1 mt-2">
            <span v-for="au in a.authors?.slice(0,5)" :key="au.id" class="text-[10px] text-primary-500">{{ au.name }}</span>
          </div>
        </div>
      </div>

      <!-- 翻页 -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-6">
        <button v-for="p in totalPages" :key="p" @click="goPage(p)"
          class="w-9 h-9 rounded-lg text-sm font-medium transition"
          :class="p === page ? 'bg-primary-500 text-white' : 'bg-white text-gray-500 hover:bg-soft-pink'">{{ p }}</button>
      </div>
    </div>

    <div v-else-if="searched" class="soft-card p-10 text-center text-gray-400">
      <span class="text-4xl">&#x1F50D;</span><p class="mt-2">No results. Try different keywords.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getArticles, getJournalsStats } from '@/api'

const route = useRoute()
const journals = ref<any[]>([])
const results = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const totalPages = ref(1)
const loading = ref(false)
const searched = ref(false)

const f = ref({ query: '', journal: '', author: '', country: '' })

const doSearch = async (p?: number) => {
  if (p) page.value = p
  searched.value = true
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize, sort_by: 'published_date', sort_order: 'desc' }
    if (f.value.query) params.query = f.value.query
    if (f.value.journal) params.journal_id = f.value.journal
    if (f.value.author) params.author = f.value.author
    if (f.value.country) params.country = f.value.country
    const res = await getArticles(params)
    results.value = res.data.items
    total.value = res.data.total
    totalPages.value = Math.ceil(res.data.total / pageSize)
  } catch (e) { console.error(e) }
  loading.value = false
}

const goPage = (p: number) => { doSearch(p); window.scrollTo(0, 0) }
const reset = () => { f.value = { query: '', journal: '', author: '', country: '' }; results.value = []; searched.value = false; page.value = 1 }

onMounted(async () => {
  const jr = await getJournalsStats()
  journals.value = jr.data
  // 从 URL 读取参数
  if (route.query.author) { f.value.author = route.query.author as string; doSearch() }
  else if (route.query.q) { f.value.query = route.query.q as string; doSearch() }
})
</script>
