import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('customer') || 'null'))
  const isAdmin = computed(() => user.value?.role === 'admin')

  function login(data) {
    user.value = data
    localStorage.setItem('customer', JSON.stringify(data))
  }
  function logout() {
    user.value = null
    localStorage.removeItem('customer')
  }
  return { user, isAdmin, login, logout }
})
