<script setup>

const props = defineProps({
  text: { type: String, required: true },
  options: { type: Array, default: () => [] },
  modelValue: { type: [String, Number, null], default: null },
})

const emit = defineEmits(['update:modelValue'])
function select(opt) { emit('update:modelValue', opt) }

</script>

<template>
  <div class="grid gap-3">
    <h2 class="text-xl font-medium">{{ text }}</h2>
    <div class="grid gap-2 text-white text-center">
      <button
        v-for="opt in options" :key="opt" @click="select(opt)"
        class="w-full rounded-lg border px-4 py-2 text-center hover:bg-slate-50
               data-[active=true]:border-blue-600 data-[active=true]:bg-blue-50"
        :data-active="modelValue === opt"
      >
        {{ opt }}
      </button>
    </div>
  </div>
</template>
