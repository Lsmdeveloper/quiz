<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'

const route = useRoute()
const score = computed(() => Number(route.query.score ?? 0))

const summary = computed(() => {
  if (score.value >= 3) return 'Excelente!'
  if (score.value === 2) return 'Muito bom!'
  return 'Vamos melhorar!'
})
</script>

<template>
  <section class="max-w-2xl mx-auto grid gap-4">
    <h1 class="text-2xl font-semibold">Resultados</h1>
    <p class="text-slate-700">Sua pontuação: <strong>{{ score }}</strong></p>
    <p class="text-slate-600">{{ summary }}</p>

    <!-- ponto para paywall/checkout futuramente -->
    <RouterLink
      to="/quiz"
      class="inline-flex items-center justify-center rounded-lg px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 w-fit"
    >
      Refazer
    </RouterLink>
  </section>
</template>
