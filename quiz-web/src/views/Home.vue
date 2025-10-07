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
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Escolha seu Quiz:</h1>
    <ul class="space-y-3">
      <li
        v-for="quiz in quizzes"
        :key="quiz.id"
        class="border p-4 rounded shadow hover:bg-gray-100 cursor-pointer"
        @click="goToQuiz(quiz.slug)"
      >
        {{ quiz.title }}
      </li>
    </ul>
  </div>
</template>