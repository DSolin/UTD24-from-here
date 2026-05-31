<template>
  <div class="animate-fade-in" v-if="article">
    <router-link to="/literature" class="text-primary-500 text-sm hover:underline mb-4 inline-block">&larr; Back</router-link>

    <div class="soft-card p-6">
      <div class="flex items-center gap-2 mb-3">
        <span class="tag-soft">{{ article.journal?.abbreviation }}</span>
      </div>

      <h1 class="text-xl font-bold text-gray-800 leading-snug">{{ article.title }}</h1>

      <div class="flex flex-wrap items-center gap-3 mt-3 text-sm text-gray-400">
        <span v-if="article.published_date">&#x1F4C5; {{ article.published_date }}</span>
        <span v-if="article.volume">Vol. {{ article.volume }}</span>
        <span v-if="article.issue">No. {{ article.issue }}</span>
        <span v-if="article.pages">pp. {{ article.pages }}</span>
      </div>

      <!-- 作者（可点击跳转到Search） -->
      <div class="mt-4">
        <h3 class="text-xs font-semibold text-gray-500 mb-2">AUTHORS</h3>
        <div class="flex flex-wrap gap-2">
          <button v-for="au in article.authors" :key="au.id"
            @click="goAuthor(au)"
            class="inline-flex items-center gap-1.5 bg-soft-lavender text-primary-700 px-3 py-1.5 rounded-full text-sm hover:bg-primary-100 transition">
            &#x1F464; {{ au.name }}
            <span v-if="au.country" class="text-[10px] opacity-60">({{ au.country }})</span>
          </button>
        </div>
      </div>

      <!-- 摘要 -->
      <div class="mt-6">
        <h3 class="text-sm font-semibold text-gray-700 mb-2">ABSTRACT</h3>
        <p class="text-sm text-gray-600 leading-relaxed whitespace-pre-line">{{ article.abstract || 'No abstract available.' }}</p>
      </div>

      <!-- 关键词 -->
      <div v-if="article.keywords?.length" class="mt-5">
        <h3 class="text-xs font-semibold text-gray-500 mb-2">KEYWORDS</h3>
        <div class="flex flex-wrap gap-1.5">
          <button v-for="kw in article.keywords" :key="kw.id"
            @click="goKeyword(kw.keyword)"
            class="tag-soft cursor-pointer hover:bg-primary-200 transition text-xs">
            {{ kw.keyword }}
          </button>
        </div>
      </div>

      <!-- 链接 + 收藏 -->
      <div class="mt-6 flex flex-wrap gap-3 pt-4 border-t">
        <a v-if="article.doi" :href="'https://doi.org/' + article.doi" target="_blank" class="btn-primary text-sm">&#x1F4C4; View on Publisher</a>
        <a v-if="article.source_url" :href="article.source_url" target="_blank" class="btn-ghost text-sm">&#x1F517; Source</a>
        <button @click="toggleFav" class="btn-ghost text-sm flex items-center gap-1">
          {{ isFav ? '\u2B50' : '\u2606' }} {{ isFav ? 'Saved' : 'Save to Favorites' }}
        </button>
      </div>
    </div>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading...</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticle, addFavorite, removeFavorite, checkFavorite } from '@/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const article = ref<any>(null)
const isFav = ref(false)

onMounted(async () => {
  try {
    const res = await getArticle(route.params.id as string)
    article.value = res.data
    if (auth.isAuthenticated) {
      const favRes = await checkFavorite(article.value.id)
      isFav.value = favRes.data.favorited
    }
  } catch (e) { console.error(e) }
})

function goAuthor(au: any) {
  router.push('/search?author=' + encodeURIComponent(au.name))
}

function goKeyword(kw: string) {
  router.push('/search?q=' + encodeURIComponent(kw))
}

async function toggleFav() {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  try {
    if (isFav.value) {
      await removeFavorite(article.value.id)
      isFav.value = false
    } else {
      await addFavorite(article.value.id)
      isFav.value = true
    }
  } catch (e) { console.error(e) }
}
</script>
