import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/Home.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue') },
  { path: '/register', name: 'register', component: () => import('@/views/Register.vue') },
  { path: '/forgot-password', name: 'forgot', component: () => import('@/views/ForgotPassword.vue') },
  { path: '/products', name: 'products', component: () => import('@/views/Products.vue') },
  { path: '/products/:id', name: 'product-detail', component: () => import('@/views/ProductDetail.vue') },
  { path: '/cart', name: 'cart', component: () => import('@/views/Cart.vue'), meta: { requiresAuth: true } },
  { path: '/orders', name: 'orders', component: () => import('@/views/Orders.vue'), meta: { requiresAuth: true } },
  { path: '/orders/:id', name: 'order-detail', component: () => import('@/views/OrderDetail.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'profile', component: () => import('@/views/Profile.vue'), meta: { requiresAuth: true } },
  { path: '/admin', name: 'admin', component: () => import('@/views/Admin.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/orders', name: 'admin-orders', component: () => import('@/views/AdminOrders.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/purchases', name: 'admin-purchases', component: () => import('@/views/AdminPurchases.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/reports', name: 'admin-reports', component: () => import('@/views/AdminReports.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const customer = JSON.parse(localStorage.getItem('customer') || 'null')
  if (to.meta.requiresAuth && !customer) return '/login'
  if (to.meta.requiresAdmin && customer?.role !== 'admin') return '/'
})

export default router
