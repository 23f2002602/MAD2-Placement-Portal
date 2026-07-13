import { reactive } from 'vue'

export const store = reactive({
  
  user: null,

  loading: true,
})

export function setUser(userData) {
  store.user = userData
  localStorage.setItem('user', JSON.stringify(userData))
}

export function clearUser() {
  store.user = null
  localStorage.removeItem('user')
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export function restoreSession() {
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    store.user = JSON.parse(savedUser)
  }
  store.loading = false
}