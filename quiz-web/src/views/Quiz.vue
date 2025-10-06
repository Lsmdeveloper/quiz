<template>
  <div class="p-6 max-w-2xl mx-auto">
    <h2 class="text-2xl font-bold mb-4">{{ quiz?.title }}</h2>

    <!-- Barra de progresso -->
    <div class="w-full h-2 bg-gray-200 rounded mb-6 overflow-hidden">
      <div
        class="h-2 bg-blue-600 transition-all"
        :style="{ width: progressPercent + '%' }"
        aria-hidden="true"
      ></div>
    </div>
    <div class="text-sm text-gray-600 mb-4">
      {{ currentStep }} / {{ totalSteps }}
    </div>

    <!-- Estado vazio / carregando -->
    <div v-if="!currentQuestion" class="text-gray-600">Carregando perguntas…</div>

    <!-- Questão atual -->
    <form v-else @submit.prevent="goNext">
      <p class="font-semibold text-lg mb-4">
        {{ currentStep }}. {{ currentQuestion.title }}
      </p>

      <div class="ml-2 space-y-3">
        <label
          v-for="(optionText, letter) in currentQuestion.options"
          :key="letter"
          class="flex items-center gap-2 cursor-pointer"
        >
          <input
            type="radio"
            :name="'question-' + currentQuestion.slug"
            :value="letter"
            v-model="answers[currentQuestion.slug]"
            class="w-4 h-4"
            required
          />
          <span class="select-none">
            {{ letter.toUpperCase() }}) {{ optionText }}
          </span>
        </label>
      </div>

      <!-- Navegação -->
      <div class="mt-6 flex gap-3">
        <button
          type="button"
          class="px-4 py-2 rounded border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          @click="goPrev"
          :disabled="currentIndex === 0 || isSubmitting"
        >
          Voltar
        </button>

        <button
          v-if="!isLast"
          type="submit"
          class="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          :disabled="!answers[currentQuestion.slug] || isSubmitting"
        >
          Avançar
        </button>

        <button
          v-else
          type="button"
          class="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
          @click="submitAnswers"
          :disabled="!answers[currentQuestion.slug] || isSubmitting"
        >
          Finalizar
        </button>
      </div>
    </form>

    <!-- Resultado -->
    <div
      v-if="result"
      class="mt-8 p-4 border rounded bg-green-100 text-green-800"
    >
      <p><strong>Resultado:</strong> {{ result.score }} / {{ totalSteps }}</p>
      <p v-if="result.message">{{ result.message }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      quiz: null,
      sessionId: null,
      questions: [],
      answers: {},        // { [question.slug]: 'a' | 'b' | 'c' | 'd' }
      currentIndex: 0,
      isSubmitting: false,
      result: null,
    };
  },
  computed: {
    totalSteps() {
      return this.questions.length || 0;
    },
    currentStep() {
      return this.currentIndex + 1;
    },
    currentQuestion() {
      return this.questions[this.currentIndex] || null;
    },
    isLast() {
      return this.currentIndex === this.totalSteps - 1;
    },
    progressPercent() {
      if (this.totalSteps === 0) return 0;
      // progresso baseado na questão atual (exibe avanço ao chegar na questão)
      return Math.round((this.currentStep - 1) / this.totalSteps * 100);
    },
  },
  mounted() {
    const slug = this.$route.params.slug;
    // Inicia a sessão e carrega perguntas
    fetch("http://localhost:8000/api/quiz/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slug }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(`Erro ${res.status}: ${text}`);
        }
        return res.json();
      })
      .then((data) => {
        this.sessionId = data.session_id; // importante para salvar/fechar
        this.quiz = data.quiz;
        this.questions = data.questions || [];
        this.questions.forEach((q) => (this.answers[q.slug] = this.answers[q.slug] ?? null));

        // atalhos de teclado: Enter para avançar, Shift+Enter para voltar
        window.addEventListener("keydown", this.handleKeys);
      })
      .catch((err) => console.error("Erro ao iniciar quiz:", err.message));
  },
  beforeUnmount() {
    window.removeEventListener("keydown", this.handleKeys);
  },
  methods: {
    handleKeys(e) {
      if (this.isSubmitting || !this.currentQuestion) return;
      // Enter: avança (ou finaliza se for a última)
      if (e.key === "Enter") {
        e.preventDefault();
        if (this.isLast) {
          if (this.answers[this.currentQuestion.slug]) this.submitAnswers();
        } else {
          if (this.answers[this.currentQuestion.slug]) this.goNext();
        }
      }
      // Shift+Enter: volta
      if (e.key === "Enter" && e.shiftKey) {
        e.preventDefault();
        if (this.currentIndex > 0) this.goPrev();
      }
      // Setas esquerda/direita podem navegar (opcional)
      if (e.key === "ArrowLeft" && this.currentIndex > 0) this.goPrev();
      if (e.key === "ArrowRight" && !this.isLast && this.answers[this.currentQuestion.slug]) this.goNext();
    },
    goNext() {
      if (this.currentIndex < this.totalSteps - 1) {
        this.currentIndex += 1;
      }
    },
    goPrev() {
      if (this.currentIndex > 0) {
        this.currentIndex -= 1;
      }
    },
    async submitAnswers() {
      if (!this.sessionId) {
        console.error("Sem sessionId — verifique o retorno do /api/quiz/start.");
        return;
      }
      this.isSubmitting = true;

      try {
        // monta payload no formato que seu backend espera
        const payload = {
          answers: this.questions.map((q) => ({
            questionId: q.slug,                 // seu SaveAnswers usa slug
            choices: [this.answers[q.slug]],    // radiobutton => 1 letra
          })),
        };

        // salva todas as respostas
        const r1 = await fetch(`http://localhost:8000/api/quiz/${this.sessionId}/answer`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!r1.ok) {
          const t = await r1.text();
          throw new Error(`Salvar respostas: ${t}`);
        }

        // finaliza e pega o resultado
        const r2 = await fetch(
          `http://localhost:8000/api/quiz/${this.sessionId}/finish?slug=${this.quiz.slug}`,
          { method: "POST" }
        );
        if (!r2.ok) {
          const t = await r2.text();
          throw new Error(`Finalizar quiz: ${t}`);
        }
        this.result = await r2.json();

        // 100% na barra ao finalizar
        this.currentIndex = this.totalSteps - 1;
      } catch (err) {
        console.error(err.message);
      } finally {
        this.isSubmitting = false;
      }
    },
  },
};
</script>
