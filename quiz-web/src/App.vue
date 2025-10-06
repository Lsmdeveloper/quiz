<script setup>
</script>

<template>
  <div class="min-h-dvh bg-slate-50 text-slate-900">
    <header class="border-b bg-white">
      <nav class="max-w-5xl mx-auto flex items-center justify-between p-4">
        <RouterLink to="/" class="font-bold">Quiz</RouterLink>
        <div class="flex items-center gap-4">
          <RouterLink to="/quiz" class="text-sm hover:underline">Começar</RouterLink>
          <RouterLink to="/results" class="text-sm hover:underline">Resultados</RouterLink>
        </div>
      </nav>
    </header>
    <main class="flex flex-col items-start justify-center min-h-[calc(100vh-540px)] max-w-5xl p-4">
      <RouterView />
    </main>
  </div>
</template>