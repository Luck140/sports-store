import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('customer') || 'null'))

  const isAdmin = computed(() => user.value?.role === 'admin')

  function login(customerData) {
    user.value = customerData
    localStorage.setItem('customer', JSON.stringify(customerData))
  }

  function logout() {
    user.value = null
    localStorage.removeItem('customer')
  }

  return { user, isAdmin, login, logout }
})