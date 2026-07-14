<template>
  <div style="min-height: 100vh; background: #f8f9fa;">

    <nav class="navbar navbar-dark px-4 py-3" style="background: #343a40; border-bottom: 1px solid #495057;">
      <span class="navbar-brand fw-bold d-flex align-items-center gap-2" style="color: #ffffff;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-mortarboard" viewBox="0 0 16 16">
          <path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.135 3.76a.5.5 0 0 0 0 .882L4 8.386V11a.5.5 0 0 0 .193.398l3.5 2.5a.5.5 0 0 0 .614 0l3.5-2.5A.5.5 0 0 0 12 11V8.386l3.346-1.697a.5.5 0 0 0 0-.882zM11 11.23 8 13.374l-3-2.144V8.892l3 1.523 3-1.523zM1.78 5.75 8 2.472l6.22 3.278L8 9.028z"/>
        </svg>
        PlaceMe
      </span>
      <div class="d-flex gap-2">
        <button class="btn btn-sm" :class="activeTab==='drives'?'btn-light text-dark':'btn-outline-light'"
                @click="switchTab('drives')">Drives</button>
        <button class="btn btn-sm" :class="activeTab==='applications'?'btn-light text-dark':'btn-outline-light'"
                @click="switchTab('applications')">My Applications</button>
        <button class="btn btn-sm" :class="activeTab==='history'?'btn-light text-dark':'btn-outline-light'"
                @click="switchTab('history')">History</button>
        <router-link id="link-profile" to="/profile" class="btn btn-sm btn-outline-light">Profile</router-link>
        <button class="btn btn-sm btn-outline-light" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="container-fluid p-4">

      <div v-if="student" class="card p-3 mb-4 d-flex flex-row align-items-center gap-3 bg-white border">
        <div class="rounded-circle d-flex align-items-center justify-content-center fw-bold fs-4"
             style="width:50px;height:50px;background:#007bff;color:white;">
          {{ student.full_name?.[0] || student.username?.[0] || 'S' }}
        </div>
        <div>
          <div class="fw-bold text-dark">{{ student.full_name || student.username }}</div>
          <div class="text-muted small">
            {{ student.department || 'No dept' }}
            | CGPA: <strong class="text-dark">{{ student.cgpa }}</strong>
            | Batch {{ student.graduation_year || '—' }}
          </div>
        </div>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="activeTab === 'drives'">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
          <h5 class="text-dark mb-0">Placement Drives</h5>
          <div class="d-flex gap-2">
            <input v-model="driveSearch" type="text" class="form-control border-secondary"
                   placeholder="Search drives..." style="width:200px;" @input="filterDrives" />
            <div class="form-check form-switch d-flex align-items-center gap-2 ms-2">
              <input class="form-check-input" type="checkbox" id="eligibleOnly" v-model="eligibleOnly" @change="filterDrives" />
              <label class="form-check-label text-muted" for="eligibleOnly">Eligible only</label>
            </div>
          </div>
        </div>

        <div v-if="filteredDrives.length === 0" class="text-center py-5 text-muted">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-briefcase text-secondary mb-2" viewBox="0 0 16 16">
            <path d="M6.5 1A1.5 1.5 0 0 0 5 2.5V3H1.5A1.5 1.5 0 0 0 0 4.5v8A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-8A1.5 1.5 0 0 0 14.5 3H11v-.5A1.5 1.5 0 0 0 9.5 1zm0 1h3a.5.5 0 0 1 .5.5V3H6v-.5a.5.5 0 0 1 .5-.5m1.886 6.914L15 7.151V12.5a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5V7.15l6.614 1.764a1.5 1.5 0 0 0 .772 0M1.5 4h13a.5.5 0 0 1 .5.5v1.616L8.129 7.948a.5.5 0 0 1-.258 0L1 6.116V4.5a.5.5 0 0 1 .5-.5"/>
          </svg>
          <p>No placement drives available right now.</p>
        </div>

        <div class="row g-3">
          <div class="col-md-6 col-lg-4" v-for="drive in filteredDrives" :key="drive.id">
            <div class="card h-100 p-3 border-secondary" :style="drive.eligible ? '' : 'opacity: 0.75;'">

              <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <h6 class="text-dark mb-0">{{ drive.drive_name }}</h6>
                  <small class="text-muted">{{ drive.company_name }}</small>
                </div>
                <span class="badge bg-secondary">{{ drive.interview_type }}</span>
              </div>

              <p class="text-dark mb-1 d-flex align-items-center gap-2 small">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-person" viewBox="0 0 16 16">
                  <path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6m2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0m4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4m-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10s-3.516.68-4.168 1.332c-.678.678-.83 1.418-.832 1.664z"/>
                </svg>
                {{ drive.job_title }}
              </p>
              <p v-if="drive.salary" class="text-dark mb-1 d-flex align-items-center gap-2 small">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-cash-stack" viewBox="0 0 16 16">
                  <path d="M14 3H1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h13a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1M2 5h10v6H2zm12 7H2v-1h12z"/>
                </svg>
                {{ drive.salary }}
              </p>
              <p v-if="drive.location" class="text-dark mb-2 d-flex align-items-center gap-2 small">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-geo-alt" viewBox="0 0 16 16">
                  <path d="M12.166 8.94c-.524 1.062-1.234 2.12-1.96 3.07A32 32 0 0 1 8 14.58a32 32 0 0 1-2.206-2.57c-.726-.95-1.436-2.008-1.96-3.07C3.304 7.867 3 6.862 3 6a5 5 0 0 1 10 0c0 .862-.305 1.867-.834 2.94M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10"/>
                  <path d="M8 8a2 2 0 1 1 0-4 2 2 0 0 1 0 4m0 1a3 3 0 1 0 0-6 3 3 0 0 0 0 6"/>
                </svg>
                {{ drive.location }}
              </p>

              <p v-if="drive.application_deadline" class="small mb-2 d-flex align-items-center gap-2"
                 :class="isDeadlineSoon(drive.application_deadline) ? 'text-danger fw-bold' : 'text-muted'">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-clock" viewBox="0 0 16 16">
                  <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71z"/>
                  <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0"/>
                </svg>
                Deadline: {{ formatDate(drive.application_deadline) }}
              </p>

              <div v-if="!drive.eligible && drive.eligibility_errors.length" class="mb-2">
                <span v-for="err in drive.eligibility_errors" :key="err"
                      class="badge bg-danger me-1 d-block text-start mb-1" style="font-size:0.7rem; white-space:normal;">
                  Not Eligible: {{ err }}
                </span>
              </div>

              <div class="mt-auto pt-2 d-flex gap-1 flex-column">
                <button class="btn btn-outline-secondary btn-sm w-100" @click="showDetail('Drive Detail', drive)">Show Details</button>
                <span v-if="drive.already_applied" class="badge bg-success w-100 py-2">Applied</span>
                <button v-else-if="drive.eligible" class="btn btn-primary btn-sm w-100"
                        @click="applyToDrive(drive.id)" :disabled="applying === drive.id">
                  <span v-if="applying === drive.id" class="spinner-border spinner-border-sm me-1"></span>
                  Apply Now
                </button>
                <button v-else class="btn btn-outline-secondary btn-sm w-100" disabled>
                  Not Eligible
                </button>
              </div>

            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'applications'">
        <h5 class="text-dark mb-3">My Applications</h5>
        <div v-if="applications.length === 0" class="text-center py-5 text-muted">
          You haven't applied to any drives yet.
        </div>
        <div class="table-responsive" v-else>
          <table class="table table-striped table-hover align-middle border bg-white">
            <thead><tr>
              <th>Company</th><th>Drive</th><th>Job Title</th><th>Status</th><th>Applied</th><th>Actions</th>
            </tr></thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td class="text-dark">{{ app.company_name }}</td>
                <td class="text-dark">{{ app.drive_name }}</td>
                <td class="text-muted small">{{ app.job_title }}</td>
                <td><span class="badge" :class="`badge-${app.status}`">{{ app.status }}</span></td>
                <td class="text-muted small">{{ new Date(app.applied_at).toLocaleDateString() }}</td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-outline-secondary" @click="showDetail('Application Detail', app)">Show</button>
                    <button
                      v-if="app.status === 'applied'"
                      class="btn btn-sm btn-danger d-flex align-items-center gap-1"
                      @click="withdrawApplication(app.id)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                      </svg>
                      Withdraw
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="activeTab === 'history'">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
          <h5 class="text-dark mb-0">Placement History</h5>
          <div class="d-flex align-items-center gap-2 flex-wrap">

            <button
              id="btn-download-csv-direct"
              class="btn btn-sm btn-success d-flex align-items-center gap-2"
              @click="downloadDirect"
              :disabled="directDownloading"
            >
              <span v-if="directDownloading" class="spinner-border spinner-border-sm me-1"></span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5"/>
                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708z"/>
              </svg>
              {{ directDownloading ? 'Preparing…' : 'Download CSV' }}
            </button>

            <span class="text-muted small">|</span>

            <span v-if="exportStatus && exportStatus !== 'SUCCESS' && exportStatus !== 'FAILURE'"
                  class="badge bg-secondary">
              <span class="spinner-border spinner-border-sm me-1"></span>
              {{ exportStatus }}
            </span>
            <a v-if="exportFilename"
               :href="api.getExportDownloadUrl(exportFilename)"
               class="btn btn-sm btn-outline-success d-flex align-items-center gap-2"
               download>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark-excel" viewBox="0 0 16 16">
                <path d="M5.884 6.68a.5.5 0 1 0-.768.64L7.349 10l-2.233 2.68a.5.5 0 0 0 .768.64L8 10.781l2.116 2.54a.5.5 0 0 0 .768-.641L8.651 10l2.233-2.68a.5.5 0 0 0-.768-.64L8 9.219l-2.116-2.54z"/>
                <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2M9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5z"/>
              </svg>
              Async CSV Ready
            </a>
            <span v-if="exportStatus === 'FAILURE'" class="badge bg-danger">Export failed</span>
            <button
              id="btn-export-csv-celery"
              class="btn btn-sm btn-outline-secondary d-flex align-items-center gap-2"
              @click="exportCsv"
              :disabled="exporting"
              title="Runs as background job and sends you an email when done"
            >
              <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-envelope" viewBox="0 0 16 16">
                <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v.217l7 4.2 7-4.2V4a1 1 0 0 0-1-1zm13 2.383-4.708 2.825L15 11.105zm-.034 6.876-5.64-3.471L8 9.583l-1.326-.795-5.64 3.47A1 1 0 0 0 2 13h12a1 1 0 0 0 .966-.741M1 11.105l4.708-2.897L1 5.383z"/>
              </svg>
              Export + Email
            </button>
          </div>
        </div>
        <div v-if="history.length === 0" class="text-center py-5 text-muted">
          No placement history yet.
        </div>
        <div class="table-responsive" v-else>
          <table class="table table-striped table-hover align-middle border bg-white">
            <thead><tr>
              <th>Company</th><th>Drive</th><th>Job Title</th><th>Status</th><th>Applied</th><th>Actions</th>
            </tr></thead>
            <tbody>
              <tr v-for="app in history" :key="app.id">
                <td class="text-dark">{{ app.company_name }}</td>
                <td class="text-dark">{{ app.drive_name }}</td>
                <td class="text-muted small">{{ app.job_title }}</td>
                <td><span class="badge" :class="`badge-${app.status}`">{{ app.status }}</span></td>
                <td class="text-muted small">{{ new Date(app.applied_at).toLocaleDateString() }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-secondary" @click="showDetail('Placement Record Detail', app)">Show</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="detailModalOpen" class="modal-backdrop fade show" style="z-index: 1040;"></div>
      <div v-if="detailModalOpen" class="modal fade show d-block" tabindex="-1" style="z-index: 1050; background: rgba(0,0,0,0.5);" @click.self="closeDetailModal">
        <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content bg-white text-dark border-secondary">
            <div class="modal-header border-secondary bg-light">
              <h5 class="modal-title text-dark">{{ detailTitle }}</h5>
              <button type="button" class="btn-close" @click="closeDetailModal"></button>
            </div>
            <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
              <table class="table table-bordered mb-0 bg-white">
                <tbody>
                  <tr v-for="(value, key) in detailData" :key="key">
                    <td class="text-muted fw-bold" style="width: 35%;">{{ key }}</td>
                    <td class="text-dark">{{ value }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="modal-footer border-secondary bg-light">
              <button type="button" class="btn btn-secondary" @click="closeDetailModal">Close</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'
import { clearUser } from '../store.js'

const router = useRouter()

const loading      = ref(true)
const student      = ref(null)
const drives       = ref([])
const applications = ref([])
const history      = ref([])
const activeTab    = ref('drives')
const driveSearch  = ref('')
const eligibleOnly = ref(false)
const applying     = ref(null)   
const exporting    = ref(false)
const directDownloading = ref(false)   
const exportStatus   = ref('')      
const exportFilename = ref('')      
const error        = ref('')
const successMsg   = ref('')

const detailModalOpen = ref(false)
const detailTitle     = ref('')
const detailData      = ref({})

function showDetail(title, data) {
  detailTitle.value = title
  detailData.value = { ...data }
  detailModalOpen.value = true
}

function closeDetailModal() {
  detailModalOpen.value = false
}

onMounted(async () => {
  try {
    const data     = await api.getStudentDashboard()
    student.value  = data.student
    drives.value   = data.available_drives
    applications.value = data.my_applications
  } catch (e) {
    error.value = 'Failed to load dashboard.'
  } finally {
    loading.value = false
  }
})

const filteredDrives = computed(() => {
  return drives.value.filter(d => {
    const matchesSearch = !driveSearch.value ||
      d.drive_name.toLowerCase().includes(driveSearch.value.toLowerCase()) ||
      d.job_title.toLowerCase().includes(driveSearch.value.toLowerCase())
    const matchesEligible = !eligibleOnly.value || d.eligible
    return matchesSearch && matchesEligible
  })
})

function filterDrives() {  }

async function switchTab(tab) {
  activeTab.value = tab
  if (tab === 'history' && history.value.length === 0) {
    try {
      const data = await api.getHistory()
      history.value = data.history
    } catch (e) {
      error.value = 'Failed to load history.'
    }
  }
}

async function applyToDrive(driveId) {
  applying.value = driveId
  error.value    = ''
  successMsg.value = ''
  try {
    await api.applyToDrive(driveId)
    
    const data = await api.getStudentDashboard()
    drives.value   = data.available_drives
    applications.value = data.my_applications
    successMsg.value = 'Applied successfully!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to apply.'
  } finally {
    applying.value = null
  }
}

async function withdrawApplication(appId) {
  if (!confirm('Are you sure you want to withdraw this application? This action cannot be undone.')) return
  error.value = ''
  successMsg.value = ''
  try {
    await api.withdrawApplication(appId)
    
    const data = await api.getStudentDashboard()
    drives.value   = data.available_drives
    applications.value = data.my_applications
    
    if (history.value.length > 0) {
      const histData = await api.getHistory()
      history.value = histData.history
    }
    
    successMsg.value = 'Application withdrawn successfully!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to withdraw application.'
  }
}

async function exportCsv() {
  exporting.value    = true
  exportStatus.value = ''
  exportFilename.value = ''
  error.value = ''
  try {
    const { task_id } = await api.exportCsv()
    successMsg.value = 'Export started — polling for result…'

    const poll = setInterval(async () => {
      try {
        const res = await api.getExportStatus(task_id)
        exportStatus.value = res.status

        if (res.status === 'SUCCESS') {
          clearInterval(poll)
          exporting.value    = false
          exportFilename.value = res.result?.filename || ''
          successMsg.value = 'CSV ready! Click "Download CSV" to save it.'
          setTimeout(() => { successMsg.value = '' }, 8000)
        } else if (res.status === 'FAILURE') {
          clearInterval(poll)
          exporting.value = false
          error.value = 'Export failed on the server. Is Celery running?'
        }
      } catch {
        clearInterval(poll)
        exporting.value = false
        error.value = 'Could not check export status.'
      }
    }, 2000)
  } catch (e) {
    exporting.value = false
    error.value = 'Export failed to start. Make sure Celery is running.'
  }
}

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

function isDeadlineSoon(isoString) {
  const diff = new Date(isoString) - new Date()
  return diff > 0 && diff < 3 * 24 * 60 * 60 * 1000
}

async function downloadDirect() {
  directDownloading.value = true
  error.value = ''
  try {
    await api.downloadStudentCsvDirect()
    successMsg.value = '✅ CSV downloaded!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (e) {
    error.value = 'Download failed. Please try again.'
  } finally {
    directDownloading.value = false
  }
}

function logout() {
  clearUser()
  router.push('/')
}
</script>