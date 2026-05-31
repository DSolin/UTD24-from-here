<template>
  <div class="flex h-screen overflow-hidden bg-bg-primary">
    <SideNav />
    <main class="flex-1 overflow-y-auto px-8 py-6">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in"><component :is="Component" /></transition>
      </router-view>
    </main>
    <RightPanel />
  </div>
</template>

<script setup lang="ts">
import SideNav from "./SideNav.vue";
import RightPanel from "./RightPanel.vue";
</script>
