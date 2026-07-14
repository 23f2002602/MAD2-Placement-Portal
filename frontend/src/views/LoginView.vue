<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center" style="background: #eef1f6;">

    <div class="card p-4 shadow-sm" style="width: 100%; max-width: 420px; border: 1px solid #ced4da;">

      <div class="text-center mb-4">
        <h2 class="fw-bold d-flex align-items-center justify-content-center gap-2" style="color: #007bff;">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-mortarboard" viewBox="0 0 16 16">
            <path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.135 3.76a.5.5 0 0 0 0 .882L4 8.386V11a.5.5 0 0 0 .193.398l3.5 2.5a.5.5 0 0 0 .614 0l3.5-2.5A.5.5 0 0 0 12 11V8.386l3.346-1.697a.5.5 0 0 0 0-.882zM11 11.23 8 13.374l-3-2.144V8.892l3 1.523 3-1.523zM1.78 5.75 8 2.472l6.22 3.278L8 9.028z"/>
          </svg>
          PlaceMe
        </h2>
        <p class="text-muted mb-0">College Placement Portal</p>
      </div>

      <div v-if="error" class="alert alert-danger py-2" role="alert">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">

        <div class="mb-3">
          <label for="email" class="form-label text-dark">Email Address</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-control border-secondary"
            placeholder="you@example.com"
            required
          />
        </div>

        <div class="mb-4">
          <label for="password" class="form-label text-dark">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-control border-secondary"
            placeholder="••••••••"
            required
          />
        </div>

        <button
          type="submit"
          class="btn w-100 fw-semibold"
          style="background: #007bff; color: white;"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>

      </form>

      <p class="text-center text-secondary mt-3 mb-0">
        Don't have an account?
        <router-link to="/register" style="color: #007bff;">Register here</router-link>
      </p>

    </div>
  </div>
</template>

<script setup>

import { ref } from 'vue'            
import { useRouter } from 'vue-router'
import api from '../api.js'
import { setUser } from '../store.js'

const router = useRouter()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)  
const error   = ref('')     

async function handleLogin() {
  error.value   = ''        
  loading.value = true

  try {
    
    const data = await api.login(form.value)

    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)

    setUser(data.user)

    router.push(`/${data.user.role}`)

  } catch (err) {
    
    error.value = err.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>