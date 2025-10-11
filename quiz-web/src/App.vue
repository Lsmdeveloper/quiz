<script setup>
</script>

<template>
  <div class="min-h-dvh bg-[#1E1B4B] text-white">
    <header class="border-b bg-[#1E1B4B]">
      <nav class="max-w-5xl mx-auto flex items-center justify-between p-4">
        <RouterLink to="/" class="font-bold">Quiz</RouterLink>
        <div class="flex items-center gap-4">
          <RouterLink to="/results" class="text-sm hover:underline">Resultados</RouterLink>
        </div>
      </nav>
    </header>
    <main class="bg-[#1E1B4B] flex flex-col items-center justify-center min-h-[calc(100vh-540px)] max-w-5xl p-4">
      <RouterView />
    </main>
  </div>
</template>