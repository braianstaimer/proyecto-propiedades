<script setup lang="ts">
import type { PropertyOut } from '@/types/api'
import PropertyCard from './PropertyCard.vue'

defineProps<{ properties: PropertyOut[] }>()
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    <PropertyCard v-for="property in properties" :key="property.id" :property="property" />
  </div>
</template>
