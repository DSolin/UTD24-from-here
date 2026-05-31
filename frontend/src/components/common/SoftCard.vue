<template>
  <div class="soft-card p-5 animate-fade-in" :class="[gradient ? 'gradient-card' : '', customClass]">
    <div v-if="$slots.header" class="flex items-center justify-between mb-4"><slot name="header" /></div>
    <slot />
  </div>
</template>
<script setup lang="ts">
withDefaults(defineProps<{ gradient?: boolean; customClass?: string }>(), { gradient: false, customClass: "" });
</script>
