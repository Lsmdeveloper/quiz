<script>
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default {
  data() {
    return {
      quizzes: []
    };
  },
  mounted() {
    fetch(`${API_BASE_URL}/api/quiz/list`)
      .then((res) => res.json())
      .then((data) => (this.quizzes = data));
  },
  methods: {
    goToQuiz(slug) {
      this.$router.push(`/quiz/${slug}`);
    }
  }
};
</script>

<template>
  <div class="p-4">
    <h1 class="text-2xl pb-6 font-bold ">Escolha seu Quiz:</h1>
    <ul class="grid grid-cols-2 gap-3">
      <li
        v-for="quiz in quizzes"
        :key="quiz.id"
        class="cursor-pointer"
        @click="goToQuiz(quiz.slug)"
      > 
      <template v-if="quiz.cover">
        <img
          :src="quiz.cover"
          alt="Capa do Quiz"
          class="w-full h-40 rounded-t-[20px] object-cover"
        />
      </template>
      <template v-else>
        <!-- Avatar SVG genérico -->
        <div
          class="w-full hover:bg-blue-200 h-40 flex items-center justify-center bg-[#C7C9F2] rounded-t-[20px]"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="w-12 h-12 text-gray-500"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l3.409 3.409a2.25 2.25 0 003.182 0L21.75 9.75M3 19.5h18"
            />
          </svg>
        </div>
      </template>
      <div class="p-4 font-bold shadow-xl bg-[#8486f7] rounded-b-[15px]">
          {{ quiz.title }}
      </div>
      </li>
    </ul>
  </div>
</template>