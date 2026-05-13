<script setup lang="ts">
import { computed } from 'vue'
import type { PropertyOut } from '@/types/api'

const props = defineProps<{ property: PropertyOut }>()

const formattedPrice = computed(() =>
  new Intl.NumberFormat('es-GT', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(props.property.precio),
)

const formattedDate = computed(() =>
  new Intl.DateTimeFormat('es-GT', { day: 'numeric', month: 'long', year: 'numeric' }).format(
    new Date(props.property.fecha_publicacion + 'T00:00:00'),
  ),
)

const gradientByTipo: Record<string, string> = {
  casa: 'from-primary-100 to-primary-300',
  departamento: 'from-accent-100 to-accent-300',
  terreno: 'from-emerald-100 to-emerald-300',
  oficina: 'from-violet-100 to-violet-300',
  local: 'from-amber-100 to-amber-300',
}

const iconByTipo: Record<string, string> = {
  casa: 'M3 12 12 3l9 9M5 10v10h14V10',
  departamento: 'M3 21V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14M9 21V11M15 21V11',
  terreno: 'M3 12h18M3 18h18M3 6h18',
  oficina: 'M6 4h12v16H6zM10 8h4M10 12h4M10 16h4',
  local: 'M3 9 5 4h14l2 5M3 9v11h18V9M9 14h6',
}
</script>

<template>
  <article class="card flex flex-col">
    <div
      class="aspect-[16/10] bg-gradient-to-br flex items-center justify-center"
      :class="gradientByTipo[property.tipo] ?? 'from-neutral-100 to-neutral-200'"
    >
      <svg class="w-16 h-16 text-white/90" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path :d="iconByTipo[property.tipo]" />
      </svg>
    </div>
    <div class="p-5 flex flex-col gap-3 flex-1">
      <header class="flex items-start justify-between gap-3">
        <h3 class="text-h2 leading-tight text-neutral-900">{{ property.titulo }}</h3>
        <p class="text-h2 text-primary-700 whitespace-nowrap font-semibold">{{ formattedPrice }}</p>
      </header>
      <p v-if="property.descripcion" class="text-body text-neutral-600 line-clamp-2">
        {{ property.descripcion }}
      </p>
      <p class="text-caption text-neutral-500 flex items-center gap-1">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
          <circle cx="12" cy="10" r="3" />
        </svg>
        {{ property.ubicacion }}
      </p>
      <div class="flex flex-wrap gap-2 mt-auto pt-2">
        <span class="chip capitalize">{{ property.tipo }}</span>
        <span v-if="property.habitaciones !== null" class="chip">
          {{ property.habitaciones }} hab.
        </span>
        <span v-if="property.banos !== null" class="chip">{{ property.banos }} baños</span>
        <span v-if="property.area_m2 !== null" class="chip">{{ property.area_m2 }} m²</span>
      </div>
      <footer class="pt-3 border-t border-neutral-100">
        <p class="text-caption text-neutral-400">Publicado el {{ formattedDate }}</p>
      </footer>
    </div>
  </article>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
