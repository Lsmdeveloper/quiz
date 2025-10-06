<script setup>
defineProps({
  variant: { type: String, default: 'solid' },
  disabled: { type: Boolean, default: false },
})
</script>

<template>
  <button
    :disabled="disabled"
    class="inline-flex items-center justify-center rounded-lg px-4 py-2 transition
           disabled:[#fff] disabled:cursor-not-allowed"
    :class="variant === 'ghost'
      ? 'bg-transparent border border-slate-300 hover:bg-slate-50'
      : 'bg-blue-600 hover:bg-blue-700 text-white'"
  >
    <slot />
  </button>
</template>

  