import { createRouter, createWebHistory } from 'vue-router'

const Home = () => import('../views/Home.vue')
const Quiz = () => import('../views/Quiz.vue')
const Results = () => import('../views/Results.vue')
const NotFound = () => import('../views/NotFound.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home, meta: { title: 'Home' } },
    { path: '/quiz/:slug', name: 'quiz', component: Quiz, meta: { title: 'Quiz' } },
    { path: '/results', name: 'results', component: Results, meta: { title: 'Resultados' } },
    { path: '/:pathMatch(.*)*', name: '404', component: NotFound, meta: { title: 'Não encontrado' } },
  ],
})

router.afterEach((to) => {
  if (to.meta?.title) document.title = `Quiz • ${to.meta.title}`
})

export default router
