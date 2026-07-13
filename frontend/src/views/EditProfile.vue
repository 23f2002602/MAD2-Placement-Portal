<template>
  <div style="min-height: 100vh; background: #f8f9fa;">

    <nav class="navbar navbar-dark px-4 py-3" style="background: #343a40; border-bottom: 1px solid #495057;">
      <span class="navbar-brand fw-bold d-flex align-items-center gap-2" style="color: #ffffff;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-mortarboard" viewBox="0 0 16 16">
          <path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.135 3.76a.5.5 0 0 0 0 .882L4 8.386V11a.5.5 0 0 0 .193.398l3.5 2.5a.5.5 0 0 0 .614 0l3.5-2.5A.5.5 0 0 0 12 11V8.386l3.346-1.697a.5.5 0 0 0 0-.882zM11 11.23 8 13.374l-3-2.144V8.892l3 1.523 3-1.523zM1.78 5.75 8 2.472l6.22 3.278L8 9.028z"/>
        </svg>
        PlaceMe
      </span>
      <router-link to="/student" class="btn btn-sm btn-outline-light">← Back to Dashboard</router-link>
    </nav>

    <div class="container py-4" style="max-width: 600px;">

      <h4 class="text-dark mb-4">Edit Profile</h4>

      <div v-if="error"      class="alert alert-danger">{{ error }}</div>
      <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else>
        
        <div class="card p-4 mb-4 bg-white border">
          <h6 class="text-dark mb-3">Personal Information</h6>
          <form @submit.prevent="saveProfile">

            <div class="mb-3">
              <label class="form-label text-dark">Full Name</label>
              <input v-model="form.full_name" type="text" class="form-control border-secondary" />
            </div>

            <div class="row g-3 mb-3">
              <div class="col">
                <label class="form-label text-dark">Department</label>
                <select v-model="form.department" class="form-select border-secondary">
                  <option value="">Select...</option>
                  <option>CS</option><option>IT</option><option>EC</option>
                  <option>ME</option><option>CE</option><option>EE</option>
                </select>
              </div>
              <div class="col">
                <label class="form-label text-dark">CGPA (0–10)</label>
                <input v-model="form.cgpa" type="number" step="0.1" min="0" max="10"
                       class="form-control border-secondary" />
              </div>
            </div>

            <div class="row g-3 mb-3">
              <div class="col">
                <label class="form-label text-dark">Graduation Year</label>
                <input v-model="form.graduation_year" type="number" min="2020" max="2030"
                       class="form-control border-secondary" />
              </div>
              <div class="col">
                <label class="form-label text-dark">Phone</label>
                <input v-model="form.phone" type="text"
                       class="form-control border-secondary" />
              </div>
            </div>

            <button type="submit" class="btn btn-primary" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              Save Profile
            </button>

          </form>
        </div>

        <div class="card p-4 bg-white border">
          <h6 class="text-dark mb-3">Resume Upload</h6>

          <div v-if="currentResume" class="alert alert-info py-2 mb-3 d-flex align-items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark-text text-info" viewBox="0 0 16 16">
              <path d="M8.5 1.5A1.5 1.5 0 0 1 10 0h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h6.5zM8 2v1.5a1.5 1.5 0 0 0 1.5 1.5h1.5zm.5 5.5a.5.5 0 0 0 0 1H13a.5.5 0 0 0 0-1zM8 9.5a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1zm0 2a.5.5 0 0 0 0 1h5a.5.5 0 0 0 0-1z"/>
            </svg>
            Current: <strong>{{ currentResume }}</strong>
          </div>

          <p class="text-muted small mb-3">
            Allowed formats: PDF, DOC, DOCX. Max size: 5 MB.
          </p>

          <input type="file" ref="fileInput" accept=".pdf,.doc,.docx"
                 class="form-control border-secondary mb-3"
                 @change="onFileSelected" />

          <button class="btn btn-outline-primary" @click="uploadResume" :disabled="!selectedFile || uploading">
            <span v-if="uploading" class="spinner-border spinner-border-sm me-1"></span>
            Upload Resume
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api.js'

const loading      = ref(true)
const saving       = ref(false)
const uploading    = ref(false)
const error        = ref('')
const successMsg   = ref('')
const currentResume = ref('')
const selectedFile = ref(null)

const form = ref({
  full_name: '',
  department: '',
  cgpa: '',
  graduation_year: '',
  phone: '',
})

onMounted(async () => {
  try {
    const profile     = await api.getStudentProfile()
    form.value        = { ...profile }
    currentResume.value = profile.resume_path || ''
  } catch (e) {
    error.value = 'Failed to load profile.'
  } finally {
    loading.value = false
  }
})

async function saveProfile() {
  saving.value = true
  error.value  = ''
  successMsg.value = ''
  try {
    await api.updateStudentProfile(form.value)
    successMsg.value = 'Profile saved successfully!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to save profile.'
  } finally {
    saving.value = false
  }
}

function onFileSelected(event) {
  selectedFile.value = event.target.files[0] || null
}

async function uploadResume() {
  if (!selectedFile.value) return
  uploading.value = true
  error.value     = ''
  successMsg.value = ''
  try {
    
    const formData = new FormData()
    formData.append('resume', selectedFile.value)
    const result = await api.uploadResume(formData)
    currentResume.value = result.filename
    successMsg.value = 'Resume uploaded successfully!'
    selectedFile.value = null
  } catch (e) {
    error.value = e.response?.data?.error || 'Upload failed.'
  } finally {
    uploading.value = false
  }
}
</script>