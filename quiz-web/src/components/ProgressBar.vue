<script setup>
defineProps({ value: { type: Number, default: 0 } })
</script>

<template>
  <div class="h-2 w-full rounded-full bg-slate-200 overflow-hidden">
    <div class="h-full bg-blue-600 transition-all" :style="{ width: `${Math.min(100, Math.max(0, value))}%` }"></div>
  </div>
</template>
