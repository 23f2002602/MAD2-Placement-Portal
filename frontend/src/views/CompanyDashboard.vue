<!--
  CompanyDashboard.vue — Company's main page
  
  Tabs:
    Overview      → Stats + status check
    My Drives     → All drives + create new drive
    Applicants    → View and manage applicants per drive
-->

<template>
  <div style="min-height: 100vh; background: #f8f9fa;">

    <!-- Navbar -->
    <nav class="navbar navbar-dark px-4 py-3" style="background: #343a40; border-bottom: 1px solid #495057;">
      <span class="navbar-brand fw-bold d-flex align-items-center gap-2" style="color: #ffffff;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-mortarboard" viewBox="0 0 16 16">
          <path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.135 3.76a.5.5 0 0 0 0 .882L4 8.386V11a.5.5 0 0 0 .193.398l3.5 2.5a.5.5 0 0 0 .614 0l3.5-2.5A.5.5 0 0 0 12 11V8.386l3.346-1.697a.5.5 0 0 0 0-.882zM11 11.23 8 13.374l-3-2.144V8.892l3 1.523 3-1.523zM1.78 5.75 8 2.472l6.22 3.278L8 9.028z"/>
        </svg>
        PlaceMe
      </span>
      <div class="d-flex gap-2">
        <button class="btn btn-sm" :class="activeTab==='overview'?'btn-light text-dark':'btn-outline-light'"
                @click="switchTab('overview')">Overview</button>
        <button class="btn btn-sm" :class="activeTab==='drives'?'btn-light text-dark':'btn-outline-light'"
                @click="switchTab('drives')">My Drives</button>
        <button class="btn btn-sm" :class="activeTab==='applicants'?'btn-light text-dark':'btn-outline-light'"
                @click="switchTab('applicants')">Applicants</button>
        <button class="btn btn-sm btn-outline-light" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="container-fluid p-4">

      <!-- Messages -->
      <div v-if="error"      class="alert alert-danger">{{ error }}</div>
      <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <!-- ── Overview Tab ── -->
      <div v-else-if="activeTab === 'overview'">
        <div v-if="company" class="mb-4">
          <h4 class="text-dark mb-1">{{ company.company_name }}</h4>
          <p class="text-muted mb-2">{{ company.description || 'No description yet.' }}</p>
          <div v-if="company.approval_status === 'pending'" class="alert alert-warning d-flex align-items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-clock-history text-warning" viewBox="0 0 16 16">
              <path d="M8.515 1.019A7 7 0 0 0 8 1V0a8 8 0 0 1 .589.022zm2.004.45a7 7 0 0 0-.985-.299l.219-.976c.383.086.76.2 1.126.342zm1.37.71a7 7 0 0 0-.439-.27l.493-.87a8 8 0 0 1 .979.654l-.61.785c-.135-.1-.28-.2-.423-.3zM16 8A8 8 0 1 1 8 0v1a7 7 0 1 0 7 7zm-5.646-.646a.5.5 0 0 0-.708.708l3 3a.5.5 0 0 0 .708-.708l-3-3z"/>
            </svg>
            Your company registration is pending admin approval. You can't post drives yet.
          </div>
          <div v-else-if="company.approval_status === 'rejected'" class="alert alert-danger d-flex align-items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-circle-fill text-danger" viewBox="0 0 16 16">
              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 1 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293z"/>
            </svg>
            Your company registration was rejected. Contact the admin.
          </div>
          <div v-else class="alert alert-success d-flex align-items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle-fill text-success" viewBox="0 0 16 16">
              <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
            </svg>
            Company approved. You can post placement drives.
          </div>
        </div>

        <!-- Stats -->
        <div class="row g-3" v-if="dashData">
          <div class="col-md-4">
            <div class="card text-center p-4 bg-white border">
              <div class="text-primary mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-journal-text" viewBox="0 0 16 16">
                  <path d="M5 10.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5m0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5m0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5"/>
                  <path d="M3 0h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2m0 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1z"/>
                </svg>
              </div>
              <div class="fs-2 fw-bold text-dark">{{ dashData.total_drives }}</div>
              <div class="text-muted small">Total Drives</div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card text-center p-4 bg-white border">
              <div class="text-primary mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-people" viewBox="0 0 16 16">
                  <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1zm-7.978-1L7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002-.014.002zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4m3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0M6.936 9.28a6 6 0 0 0-1.23-.247A7 7 0 0 0 5 9c-4 0-5 3-5 4q0 1 1 1h4.216A2.24 2.24 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816M4.92 10A5.5 5.5 0 0 0 4 13H1c0-.26.164-1.03.76-1.724C2.3 10.652 3.25 10 5 10zM3.05 7a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5m.5-4a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0"/>
                </svg>
              </div>
              <div class="fs-2 fw-bold text-dark">{{ dashData.total_applicants }}</div>
              <div class="text-muted small">Total Applicants</div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card text-center p-4 bg-white border">
              <div class="text-primary mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-patch-check" viewBox="0 0 16 16">
                  <path fill-rule="evenodd" d="M10.354 6.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708 0l-1.5-1.5a.5.5 0 1 1 .708-.708L7 8.793l2.646-2.647a.5.5 0 0 1 .708 0"/>
                  <path d="m10.273 2.513-.921-.944.715-.698.922.944-.716.698zm.93 2.29-.98-.883.666-.74.98.883-.666.74zm-.507 3.563a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0m1 0a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0"/>
                </svg>
              </div>
              <div class="fs-2 fw-bold text-dark">
                {{ dashData.drives?.filter(d => d.status === 'approved').length || 0 }}
              </div>
              <div class="text-muted small">Active Drives</div>
            </div>
          </div>
        </div>

        <!-- Download stats CSV -->
        <div class="mt-4" v-if="company?.approval_status === 'approved'">
          <div class="card p-3 d-flex flex-row align-items-center justify-content-between bg-white border">
            <div>
              <h6 class="text-dark mb-0">Download Placement Stats</h6>
              <small class="text-muted">Full CSV of all drives with applicant counts and status breakdowns</small>
            </div>
            <button
              id="btn-company-download-csv"
              class="btn btn-success btn-sm d-flex align-items-center gap-2"
              @click="downloadStats"
              :disabled="csvLoading"
            >
              <span v-if="csvLoading" class="spinner-border spinner-border-sm me-1"></span>
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
                <path d="M.5 9.9a.5.5 0 0 1 .5-.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5"/>
                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708z"/>
              </svg>
              {{ csvLoading ? 'Preparing…' : 'Download CSV' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ── My Drives Tab ── -->
      <div v-else-if="activeTab === 'drives'">

        <!-- Create Drive button (only for approved companies) -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="text-dark mb-0">My Placement Drives</h5>
          <button v-if="company?.approval_status === 'approved'"
                  class="btn btn-primary btn-sm" @click="showCreateForm = !showCreateForm">
            {{ showCreateForm ? 'Cancel' : '+ New Drive' }}
          </button>
        </div>

        <!-- Create Drive Form -->
        <div v-if="showCreateForm" class="card p-4 mb-4 bg-white border">
          <h6 class="text-dark mb-3">Create New Drive</h6>
          <form @submit.prevent="createDrive">
            <div class="row g-3 mb-3">
              <div class="col">
                <label class="form-label text-dark">Drive Name</label>
                <input v-model="driveForm.drive_name" class="form-control border-secondary"
                       placeholder="Campus Hiring 2025" required />
              </div>
              <div class="col">
                <label class="form-label text-dark">Job Title</label>
                <input v-model="driveForm.job_title" class="form-control border-secondary"
                       placeholder="Software Engineer" required />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label text-dark">Job Description</label>
              <textarea v-model="driveForm.job_description" class="form-control border-secondary" rows="3"></textarea>
            </div>

            <div class="row g-3 mb-3">
              <div class="col">
                <label class="form-label text-dark">Salary (e.g. ₹6 LPA)</label>
                <input v-model="driveForm.salary" class="form-control border-secondary" placeholder="₹6 LPA" />
              </div>
              <div class="col">
                <label class="form-label text-dark">Location</label>
                <input v-model="driveForm.location" class="form-control border-secondary" placeholder="Bangalore" />
              </div>
              <div class="col">
                <label class="form-label text-dark">Interview Type</label>
                <select v-model="driveForm.interview_type" class="form-select border-secondary">
                  <option>In-person</option>
                  <option>Online</option>
                  <option>Hybrid</option>
                </select>
              </div>
            </div>

            <!-- Eligibility Criteria -->
            <div class="row g-3 mb-3">
              <div class="col">
                <label class="form-label text-dark">Min CGPA (0 = no min)</label>
                <input v-model="driveForm.min_cgpa" type="number" step="0.1" min="0" max="10"
                       class="form-control border-secondary" placeholder="7.0" />
              </div>
              <div class="col">
                <label class="form-label text-dark">Application Deadline</label>
                <input v-model="driveForm.application_deadline" type="datetime-local"
                       class="form-control border-secondary" />
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label text-dark">Eligible Branches (comma-separated, blank = all)</label>
              <input v-model="branchesInput" class="form-control border-secondary"
                     placeholder="CS, IT, EC" />
            </div>

            <div class="mb-3">
              <label class="form-label text-dark">Grad Years (comma-separated, blank = all)</label>
              <input v-model="gradYearsInput" class="form-control border-secondary"
                     placeholder="2025, 2026" />
            </div>

            <button type="submit" class="btn btn-primary" :disabled="creating">
              <span v-if="creating" class="spinner-border spinner-border-sm me-1"></span>
              Submit for Approval
            </button>
          </form>
        </div>

        <!-- Drives list -->
        <div class="row g-3">
          <div class="col-md-6" v-for="d in drives" :key="d.id">
            <div class="card p-3 bg-white border border-secondary">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <h6 class="text-dark mb-0">{{ d.drive_name }}</h6>
                  <small class="text-muted">{{ d.job_title }}</small>
                </div>
                <span class="badge" :class="`badge-${d.status}`">{{ d.status }}</span>
              </div>
              <p class="text-dark small mb-1">Applicants: {{ d.applicant_count }}</p>
              <p v-if="d.salary" class="text-dark small mb-1">Salary: {{ d.salary }}</p>
              <div class="d-flex gap-2 mt-2">
                <button class="btn btn-sm btn-outline-secondary" @click="showDetail('Drive Detail', d)">Show</button>
                <button class="btn btn-sm btn-outline-primary" @click="viewApplicants(d)">
                  View Applicants
                </button>
                <button v-if="d.status === 'approved'" class="btn btn-sm btn-outline-danger"
                        @click="closeDrive(d.id)">Close</button>
                <button v-if="d.status === 'pending' || d.status === 'rejected'"
                        class="btn btn-sm btn-danger d-flex align-items-center gap-1"
                        @click="deleteOwnDrive(d.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          </div>
          <div v-if="drives.length === 0" class="col text-center py-4 text-muted">
            No drives posted yet.
          </div>
        </div>
      </div>

      <!-- ── Applicants Tab ── -->
      <div v-else-if="activeTab === 'applicants'">
        <div v-if="!selectedDrive">
          <p class="text-muted">Select a drive from "My Drives" to view applicants.</p>
          <!-- Quick drive select -->
          <div class="row g-3">
            <div class="col-md-4" v-for="d in drives.filter(d => d.applicant_count > 0)" :key="d.id">
              <div class="card p-3 bg-white border border-secondary" style="cursor:pointer;" @click="viewApplicants(d)">
                <h6 class="text-dark">{{ d.drive_name }}</h6>
                <p class="text-muted small mb-0">{{ d.applicant_count }} applicant(s)</p>
              </div>
            </div>
          </div>
        </div>

        <div v-else>
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="text-dark">Applicants — {{ selectedDrive.drive_name }}</h5>
            <button class="btn btn-sm btn-outline-secondary" @click="selectedDrive = null">← Back</button>
          </div>
          <div class="table-responsive">
            <table class="table table-striped table-hover align-middle border bg-white">
              <thead><tr>
                <th>Name</th><th>Dept</th><th>Status</th><th>Actions</th>
              </tr></thead>
              <tbody>
                <tr v-for="app in applicants" :key="app.id">
                  <td class="text-dark">{{ app.student_name }}</td>
                  <td class="text-muted small">{{ app.student_department }}</td>
                  <td><span class="badge" :class="`badge-${app.status}`">{{ app.status }}</span></td>
                  <td>
                    <div class="d-flex gap-1 align-items-center">
                      <button class="btn btn-sm btn-outline-secondary" @click="showDetail('Applicant / Application Detail', app)">Show</button>
                      <select class="form-select form-select-sm border-secondary"
                              style="width:auto;"
                              @change="updateStatus(app.id, $event.target.value)">
                        <option value="">Change...</option>
                        <option v-for="s in ['applied','shortlisted','selected','rejected','waiting']"
                                :value="s" :key="s">{{ s }}</option>
                      </select>
                    </div>
                  </td>
                </tr>
                <tr v-if="applicants.length === 0">
                  <td colspan="4" class="text-center text-muted">No applicants yet</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ── Details Modal Overlay ── -->
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api.js'
import { clearUser } from '../store.js'

const router = useRouter()

// State
const loading      = ref(true)
const company      = ref(null)
const dashData     = ref(null)
const drives       = ref([])
const activeTab    = ref('overview')
const showCreateForm = ref(false)
const creating     = ref(false)
const selectedDrive = ref(null)
const applicants   = ref([])
const error        = ref('')
const successMsg   = ref('')
const csvLoading   = ref(false)   // for the download CSV button

// Detail Modal state
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

// Drive creation form fields
const driveForm = ref({
  drive_name: '', job_title: '', job_description: '',
  salary: '', location: '', interview_type: 'In-person',
  min_cgpa: 0, application_deadline: ''
})
const branchesInput  = ref('')  // comma-separated branch string
const gradYearsInput = ref('')  // comma-separated year string

// Load dashboard on mount
onMounted(async () => {
  try {
    const data  = await api.getCompanyDashboard()
    company.value  = data.company
    dashData.value = data
    drives.value   = data.drives
  } catch (e) {
    error.value = 'Failed to load dashboard.'
  } finally {
    loading.value = false
  }
})

// Tab switching
async function switchTab(tab) {
  activeTab.value = tab
  if (tab === 'drives') {
    drives.value = await api.getCompanyDrives()
  }
}

// Create a new drive
async function createDrive() {
  creating.value = true
  error.value    = ''
  try {
    // Parse branch and grad year inputs
    const payload = {
      ...driveForm.value,
      branches: branchesInput.value ? branchesInput.value.split(',').map(s => s.trim()) : [],
      grad_years: gradYearsInput.value ? gradYearsInput.value.split(',').map(s => parseInt(s.trim())) : [],
    }
    await api.createDrive(payload)
    successMsg.value = 'Drive submitted for admin approval!'
    showCreateForm.value = false
    drives.value = await api.getCompanyDrives()
    setTimeout(() => { successMsg.value = '' }, 4000)
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to create drive.'
  } finally {
    creating.value = false
  }
}

// Close a drive
async function closeDrive(driveId) {
  await api.closeDrive(driveId)
  drives.value = await api.getCompanyDrives()
}

// Delete own drive (company DELETE drive action)
async function deleteOwnDrive(driveId) {
  if (!confirm('Are you sure you want to delete this drive?')) return
  error.value = ''
  successMsg.value = ''
  try {
    await api.deleteOwnDrive(driveId)
    drives.value = await api.getCompanyDrives()
    successMsg.value = 'Drive deleted successfully!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to delete drive.'
  }
}

// View applicants for a specific drive
async function viewApplicants(drive) {
  selectedDrive.value = drive
  activeTab.value = 'applicants'
  const data = await api.getDriveApplications(drive.id)
  applicants.value = data.applications
}

// Update an applicant's status
async function updateStatus(appId, newStatus) {
  if (!newStatus) return
  try {
    await api.updateApplicationStatus(appId, newStatus)
    // Refresh the applicants list
    const data = await api.getDriveApplications(selectedDrive.value.id)
    applicants.value = data.applications
  } catch (e) {
    error.value = 'Failed to update status.'
  }
}

// Download stats CSV
async function downloadStats() {
  csvLoading.value = true
  try {
    await api.downloadCompanyStatsCsv()
    successMsg.value = '✅ CSV downloaded!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (e) {
    error.value = 'Download failed. Please try again.'
  } finally {
    csvLoading.value = false
  }
}

function logout() {
  clearUser()
  router.push('/')
}
</script>
