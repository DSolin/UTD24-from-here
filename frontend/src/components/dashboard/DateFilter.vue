<template>
  <div class="flex flex-wrap items-center gap-2 soft-card p-3 mb-5">
    <span class="text-sm font-medium text-gray-600 mr-1">Date:</span>
    <input type="date" :value="store.filterDateFrom" @change="store.setDateRange(($event.target as HTMLInputElement).value, store.filterDateTo)" class="input-soft w-36 text-xs py-1.5" />
    <span class="text-gray-300 text-xs">to</span>
    <input type="date" :value="store.filterDateTo" @change="store.setDateRange(store.filterDateFrom, ($event.target as HTMLInputElement).value)" class="input-soft w-36 text-xs py-1.5" />
    <div class="flex gap-1 ml-2">
      <button v-for="btn in quickBtns" :key="btn.label" @click="applyQuick(btn.days)" class="text-xs px-2.5 py-1 rounded-lg transition"
        :class="btn.active ? 'bg-primary-500 text-white' : 'bg-soft-pink text-primary-600 hover:bg-primary-100'">
        {{ btn.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
const store = useDashboardStore()

const quickBtns = computed(() => {
  const to = new Date().toISOString().slice(0, 10)
  const d30 = new Date(Date.now() - 30*86400000).toISOString().slice(0, 10)
  const d180 = new Date(Date.now() - 180*86400000).toISOString().slice(0, 10)
  return [
    { label: '30d', days: 30, active: store.filterDateFrom === d30 && store.filterDateTo === to },
    { label: '180d', days: 180, active: store.filterDateFrom === d180 && store.filterDateTo === to },
    { label: 'All', days: 0, active: !store.filterDateFrom && !store.filterDateTo },
  ]
})

function applyQuick(days: number) {
  if (days === 0) { store.setDateRange(null, null); return }
  const to = new Date().toISOString().slice(0, 10)
  const from = new Date(Date.now() - days*86400000).toISOString().slice(0, 10)
  store.setDateRange(from, to)
}
</script>
