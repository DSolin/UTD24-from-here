<template>
  <div v-if="store.isDrilledDown" class="flex items-center gap-1.5 text-sm mb-4 soft-card p-3 animate-fade-in">
    <button @click="store.goToBreadcrumb(0)" class="text-primary-500 hover:underline font-medium">All</button>
    <template v-for="(item, i) in store.breadcrumb" :key="i">
      <span class="text-gray-300">></span>
      <button @click="store.goToBreadcrumb(i+1)" class="text-primary-500 hover:underline font-medium">
        <span v-if="item.type==='country'">🌍</span>
        <span v-else-if="item.type==='keyword'">🏷️</span>
        <span v-else>👤</span>
        {{ item.label }}
      </button>
    </template>
    <button @click="store.clearAll()" class="ml-3 text-xs text-gray-400 hover:text-red-400">✕ clear</button>
  </div>
</template>

<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard'
const store = useDashboardStore()
</script>
