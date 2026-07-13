<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center py-5" style="background: #eef1f6;">

    <div class="card p-4 shadow-sm" style="width: 100%; max-width: 500px; border: 1px solid #ced4da;">

      <div class="text-center mb-4">
        <h2 class="fw-bold d-flex align-items-center justify-content-center gap-2" style="color: #007bff;">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-mortarboard" viewBox="0 0 16 16">
            <path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.135 3.76a.5.5 0 0 0 0 .882L4 8.386V11a.5.5 0 0 0 .193.398l3.5 2.5a.5.5 0 0 0 .614 0l3.5-2.5A.5.5 0 0 0 12 11V8.386l3.346-1.697a.5.5 0 0 0 0-.882zM11 11.23 8 13.374l-3-2.144V8.892l3 1.523 3-1.523zM1.78 5.75 8 2.472l6.22 3.278L8 9.028z"/>
          </svg>
          PlaceMe
        </h2>
        <p class="text-muted mb-0">Create your account</p>
      </div>

      <div v-if="error"   class="alert alert-danger py-2">{{ error }}</div>
      <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

      <form @submit.prevent="handleRegister">

        <div class="mb-3">
          <label class="form-label text-dark">I am a...</label>
          <div class="d-flex gap-3">
            <div
              class="flex-fill text-center p-2 rounded border cursor-pointer d-flex align-items-center justify-content-center gap-2"
              :class="form.role === 'student' ? 'border-primary bg-primary bg-opacity-10 text-primary fw-bold' : 'border-secondary text-dark'"
              style="cursor: pointer;"
              @click="form.role = 'student'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">
                <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6"/>
              </svg>
              Student
            </div>
            <div
              class="flex-fill text-center p-2 rounded border d-flex align-items-center justify-content-center gap-2"
              :class="form.role === 'company' ? 'border-primary bg-primary bg-opacity-10 text-primary fw-bold' : 'border-secondary text-dark'"
              style="cursor: pointer;"
              @click="form.role = 'company'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-building" viewBox="0 0 16 16">
                <path d="M4 2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5zm3.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zM4 5.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5zm3.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zM4 8.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5zm3.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5zM4 11.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5zm3.5-.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5z"/>
              </svg>
              Company
            </div>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label text-dark">Username</label>
          <input v-model="form.username" type="text" class="form-control border-secondary"
                 placeholder="johndoe" required />
        </div>

        <div class="mb-3">
          <label class="form-label text-dark">Email</label>
          <input v-model="form.email" type="email" class="form-control border-secondary"
                 placeholder="you@example.com" required />
        </div>

        <div class="mb-3">
          <label class="form-label text-dark">Password</label>
          <input v-model="form.password" type="password" class="form-control border-secondary"
                 placeholder="At least 6 characters" required />
        </div>

        <template v-if="form.role === 'student'">
          <div class="row g-3 mb-3">
            <div class="col">
              <label class="form-label text-dark">Full Name</label>
              <input v-model="form.full_name" type="text" class="form-control border-secondary"
                     placeholder="John Doe" />
            </div>
            <div class="col">
              <label class="form-label text-dark">Department</label>
              <select v-model="form.department" class="form-select border-secondary">
                <option value="">Select...</option>
                <option>CS</option>
                <option>IT</option>
                <option>EC</option>
                <option>ME</option>
                <option>CE</option>
                <option>EE</option>
              </select>
            </div>
          </div>
          <div class="row g-3 mb-3">
            <div class="col">
              <label class="form-label text-dark">CGPA</label>
              <input v-model="form.cgpa" type="number" step="0.1" min="0" max="10"
                     class="form-control border-secondary" placeholder="8.5" />
            </div>
            <div class="col">
              <label class="form-label text-dark">Graduation Year</label>
              <input v-model="form.graduation_year" type="number" min="2020" max="2030"
                     class="form-control border-secondary" placeholder="2025" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label text-dark">Phone</label>
            <input v-model="form.phone" type="text" class="form-control border-secondary"
                   placeholder="9876543210" />
          </div>
        </template>

        <template v-if="form.role === 'company'">
          <div class="mb-3">
            <label class="form-label text-dark">Company Name</label>
            <input v-model="form.company_name" type="text" class="form-control border-secondary"
                   placeholder="Acme Corp" required />
          </div>
          <div class="mb-3">
            <label class="form-label text-dark">HR Contact Email</label>
            <input v-model="form.hr_contact" type="email" class="form-control border-secondary"
                   placeholder="hr@acmecorp.com" />
          </div>
          <div class="mb-3">
            <label class="form-label text-dark">Website</label>
            <input v-model="form.website" type="url" class="form-control border-secondary"
                   placeholder="https://acmecorp.com" />
          </div>
          <div class="mb-3">
            <label class="form-label text-dark">Description</label>
            <textarea v-model="form.description" class="form-control border-secondary" rows="3"
                      placeholder="Brief company description..."></textarea>
          </div>
          <div class="alert alert-info py-2 d-flex align-items-center gap-2" style="font-size: 0.85rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle-fill text-info" viewBox="0 0 16 16">
              <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412-1 4.705c-.07.34.029.533.304.533.194 0 .487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703 0-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381 2.29-.287zM8 5.5a1 1 0 1 1 0-2 1 1 0 0 1 0 2z"/>
            </svg>
            Company registrations require admin approval before you can login.
          </div>
        </template>

        <button type="submit" class="btn w-100 fw-semibold" style="background: #007bff; color: white;"
                :disabled="loading || !form.role">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Registering...' : 'Register' }}
        </button>

      </form>

      <p class="text-center text-secondary mt-3 mb-0">
        Already have an account?
        <router-link to="/" style="color: #007bff;">Sign in</router-link>
      </p>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'

const router = useRouter()

const form = ref({
  role: 'student',   
  username: '',
  email: '',
  password: '',
  
  full_name: '',
  department: '',
  cgpa: '',
  graduation_year: '',
  phone: '',
  
  company_name: '',
  hr_contact: '',
  website: '',
  description: '',
})

const loading = ref(false)
const error   = ref('')
const success = ref('')

async function handleRegister() {
  error.value   = ''
  success.value = ''
  loading.value = true

  try {
    const result = await api.register(form.value)
    success.value = result.message + ' Redirecting to login...'
    
    setTimeout(() => router.push('/'), 2000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed.'
  } finally {
    loading.value = false
  }
}
</script>