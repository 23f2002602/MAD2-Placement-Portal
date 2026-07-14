import { createRouter, createWebHistory } from 'vue-router'
import { store } from '../store.js'

const LoginView        = () => import('../views/LoginView.vue')
const RegisterView     = () => import('../views/RegisterView.vue')
const AdminDashboard   = () => import('../views/AdminDashboard.vue')
const CompanyDashboard = () => import('../views/CompanyDashboard.vue')
const StudentDashboard = () => import('../views/StudentDashboard.vue')
const EditProfile      = () => import('../views/EditProfile.vue')

const routes = [
  { path: '/',          component: LoginView },
  { path: '/register',  component: RegisterView },
  { path: '/admin',     component: AdminDashboard,   meta: { role: 'admin'   } },
  { path: '/company',   component: CompanyDashboard, meta: { role: 'company' } },
  { path: '/student',   component: StudentDashboard, meta: { role: 'student' } },
  { path: '/profile',   component: EditProfile,      meta: { requiresAuth: true } },
  
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),  
  routes
})

router.beforeEach((to, from, next) => {
  const user = store.user

  if ((to.path === '/' || to.path === '/register') && user) {
    
    return next(`/${user.role}`)
  }

  if (to.meta.role) {
    if (!user) {
      return next('/')          
    }
    if (user.role !== to.meta.role) {
      return next(`/${user.role}`)  
    }
  }

  if (to.meta.requiresAuth && !user) {
    return next('/')
  }

  next()  
})

export default router