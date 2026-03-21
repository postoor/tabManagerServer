import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import BookmarksView from '../views/BookmarksView.vue'

const routes = [
  {
    path: '/',
    name: 'bookmarks',
    component: BookmarksView,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if ((to.name === 'login' || to.name === 'register') && token) {
    next({ name: 'bookmarks' })
  } else {
    next()
  }
})

export default router
