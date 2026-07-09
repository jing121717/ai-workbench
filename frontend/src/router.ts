import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('./views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('./views/LayoutView.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/chat' },
        { path: 'chat', name: 'Chat', component: () => import('./views/ChatView.vue') },
        { path: 'knowledge', name: 'Knowledge', component: () => import('./views/KnowledgeView.vue') },
        { path: 'code-repository', name: 'CodeRepository', component: () => import('./views/CodeRepositoryView.vue') },
        { path: 'code-ai', name: 'CodeAI', component: () => import('./views/CodeAIView.vue') },
        { path: 'snippets', name: 'Snippets', component: () => import('./views/CodeSnippetsView.vue') },
        { path: 'settings', name: 'Settings', component: () => import('./views/SettingsView.vue') },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return '/login'
  }
  if (to.path === '/login' && auth.isLoggedIn) {
    return '/chat'
  }
})

export default router
