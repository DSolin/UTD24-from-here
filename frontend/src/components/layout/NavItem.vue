<template>
  <router-link :to="to"
    class="flex flex-col items-center gap-0.5 py-2.5 px-1 rounded-xl text-gray-400 hover:text-primary-500 hover:bg-soft-pink transition-all duration-200 group"
    active-class="!text-primary-500 !bg-soft-lavender">
    <span class="text-xl group-hover:scale-110 transition-transform">{{ icon }}</span>
    <span class="text-[10px] font-medium leading-tight">{{ label }}</span>
  </router-link>
</template>
<script setup lang="ts">
defineProps<{ icon: string; label: string; to: string }>();
</script>
