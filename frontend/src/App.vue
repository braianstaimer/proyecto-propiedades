<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'

const showSql = ref(false)
</script>

<template>
  <AppHeader :show-sql="showSql" @toggle-sql="showSql = !showSql" />
  <RouterView v-slot="{ Component }">
    <component :is="Component" :show-sql="showSql" />
  </RouterView>
</template>
