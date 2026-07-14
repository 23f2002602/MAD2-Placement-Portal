<template>
  <div style="min-height: 100vh; background: #f8f9fa;">

    <nav class="navbar navbar-dark px-4 py-3" style="background: #343a40; border-bottom: 1px solid #495057;">
      <span class="navbar-brand fw-bold d-flex align-items-center gap-2" style="color: #ffffff;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-mortarboard" viewBox="0 0 16 16">
          <path d="M8.211 2.047a.5.5 0 0 0-.422 0l-7.135 3.76a.5.5 0 0 0 0 .882L4 8.386V11a.5.5 0 0 0 .193.398l3.5 2.5a.5.5 0 0 0 .614 0l3.5-2.5A.5.5 0 0 0 12 11V8.386l3.346-1.697a.5.5 0 0 0 0-.882zM11 11.23 8 13.374l-3-2.144V8.892l3 1.523 3-1.523zM1.78 5.75 8 2.472l6.22 3.278L8 9.028z"/>
        </svg>
        PlaceMe
      </span>
      <div class="d-flex align-items-center gap-3">
        <span class="text-light small">Admin</span>
        <button class="btn btn-sm btn-outline-light" @click="logout">Logout</button>
      </div>
    </nav>

    <div class="container-fluid p-4">

      <h4 class="text-dark mb-1">Admin Dashboard</h4>
      <p class="text-muted mb-4">Manage students, companies, and placement drives</p>

      <div class="row g-3 mb-4" v-if="stats">
        <div class="col" v-for="(val, key) in statCards" :key="key">
          <div class="card text-center p-3 bg-white border">
            <div class="fs-3 fw-bold" style="color: #007bff;">{{ stats[val.field] ?? 0 }}</div>
            <div class="text-muted small text-uppercase">{{ val.label }}</div>
          </div>
        </div>
      </div>

      <ul class="nav nav-tabs mb-4" style="border-color: #dee2e6;">
        <li class="nav-item" v-for="tab in tabs" :key="tab.id">
          <button
            class="nav-link"
            :class="activeTab === tab.id ? 'active text-dark fw-bold bg-white border-bottom-0' : 'text-secondary'"
            @click="activeTab = tab.id; loadTab(tab.id)"
          >
            {{ tab.label }}
          </button>
        </li>
      </ul>

      <div v-if="tabLoading" class="text-center py-4">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="activeTab === 'overview'">
        <div class="row g-3">
          <div class="col-md-6">
            <div class="card p-3 bg-white border">
              <h6 class="text-dark mb-3">Quick Actions</h6>
              <button class="btn btn-primary w-100 mb-2" @click="activeTab = 'companies'; loadTab('companies')">
                Manage Companies
              </button>
              <button class="btn btn-outline-secondary w-100 mb-2" @click="activeTab = 'drives'; loadTab('drives')">
                Manage Drives
              </button>
              <button class="btn btn-outline-secondary w-100 mb-2" @click="activeTab = 'students'; loadTab('students')">
                View Students
              </button>
              <button class="btn btn-outline-secondary w-100 mb-2" @click="activeTab = 'applications'; loadTab('applications')">
                All Applications
              </button>
              <button class="btn btn-outline-warning w-100 text-dark" @click="activeTab = 'jobs'; loadTab('jobs')">
                Jobs & Downloads
              </button>
            </div>
          </div>
          <div class="col-md-6">
            <div class="card p-3 bg-white border">
              <h6 class="text-dark mb-3">Pending Reviews</h6>
              <div v-if="stats && (stats.pending_companies > 0 || stats.pending_drives > 0)">
                <div v-if="stats.pending_companies > 0" class="alert alert-warning py-2 mb-2 d-flex align-items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle" viewBox="0 0 16 16">
                    <path d="M7.938 2.016A.13.13 0 0 1 8.002 2a.13.13 0 0 1 .063.016.146.146 0 0 1 .054.057l6.857 11.667c.036.06.035.124.002.183a.163.163 0 0 1-.054.06.116.116 0 0 1-.066.017H1.146a.115.115 0 0 1-.066-.017.163.163 0 0 1-.054-.06.176.176 0 0 1 .002-.183L7.884 2.073a.147.147 0 0 1 .054-.057zm1.044-.45a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566z"/>
                    <path d="M7.002 12a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 5.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/>
                  </svg>
                  {{ stats.pending_companies }} company registrations pending approval
                </div>
                <div v-if="stats.pending_drives > 0" class="alert alert-warning py-2 d-flex align-items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-triangle" viewBox="0 0 16 16">
                    <path d="M7.938 2.016A.13.13 0 0 1 8.002 2a.13.13 0 0 1 .063.016.146.146 0 0 1 .054.057l6.857 11.667c.036.06.035.124.002.183a.163.163 0 0 1-.054.06.116.116 0 0 1-.066.017H1.146a.115.115 0 0 1-.066-.017.163.163 0 0 1-.054-.06.176.176 0 0 1 .002-.183L7.884 2.073a.147.147 0 0 1 .054-.057zm1.044-.45a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566z"/>
                    <path d="M7.002 12a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 5.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/>
                  </svg>
                  {{ stats.pending_drives }} drives pending approval
                </div>
              </div>
              <div v-else class="alert alert-success py-2 d-flex align-items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle-fill text-success" viewBox="0 0 16 16">
                  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0m-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
                </svg>
                No pending reviews — all clear!
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'companies'">
        <div class="d-flex gap-2 mb-3">
          <input v-model="search" type="text" class="form-control border-secondary"
                 placeholder="Search companies..." style="max-width: 300px;"
                 @input="searchCompanies" />
        </div>
        <div class="table-responsive">
          <table class="table table-striped table-hover align-middle border bg-white">
            <thead><tr>
              <th>Company</th><th>Email</th><th>Status</th><th>Blacklisted</th><th>Actions</th>
            </tr></thead>
            <tbody>
              <tr v-for="c in companies" :key="c.id">
                <td class="text-dark">{{ c.company_name }}</td>
                <td class="text-muted small">{{ c.email }}</td>
                <td>
                  <span class="badge" :class="`badge-${c.approval_status}`">
                    {{ c.approval_status }}
                  </span>
                </td>
                <td>
                  <span v-if="c.is_blacklisted" class="badge bg-danger">Blacklisted</span>
                  <span v-else class="text-muted small">No</span>
                </td>
                <td>
                  <div class="d-flex gap-1 flex-wrap">
                    <button class="btn btn-sm btn-outline-secondary" @click="showDetail('Company Profile Detail', c)">Show</button>
                    <button v-if="c.approval_status === 'pending'"
                      class="btn btn-sm btn-success" @click="approveCompany(c.id, 'approved')">Approve</button>
                    <button v-if="c.approval_status === 'pending'"
                      class="btn btn-sm btn-danger" @click="approveCompany(c.id, 'rejected')">Reject</button>
                    <button v-if="!c.is_blacklisted"
                      class="btn btn-sm btn-warning" @click="toggleBlacklist('company', c.id, true)">Blacklist</button>
                    <button v-else
                      class="btn btn-sm btn-outline-success" @click="toggleBlacklist('company', c.id, false)">Reinstate</button>
                    <button class="btn btn-sm btn-danger d-flex align-items-center gap-1" @click="deleteItem('company', c.id)">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                      </svg>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="companies.length === 0">
                <td colspan="5" class="text-center text-muted">No companies found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="activeTab === 'students'">
        <div class="d-flex gap-2 mb-3">
          <input v-model="search" type="text" class="form-control border-secondary"
                 placeholder="Search students..." style="max-width: 300px;"
                 @input="searchStudents" />
        </div>
        <div class="table-responsive">
          <table class="table table-striped table-hover align-middle border bg-white">
            <thead><tr>
              <th>Name</th><th>Department</th><th>CGPA</th><th>Grad Year</th><th>Blacklisted</th><th>Actions</th>
            </tr></thead>
            <tbody>
              <tr v-for="s in students" :key="s.id">
                <td class="text-dark">{{ s.full_name || s.username }}</td>
                <td class="text-muted small">{{ s.department || '—' }}</td>
                <td class="text-dark">{{ s.cgpa }}</td>
                <td class="text-dark">{{ s.graduation_year || '—' }}</td>
                <td>
                  <span v-if="s.is_blacklisted" class="badge bg-danger">Yes</span>
                  <span v-else class="text-muted small">No</span>
                </td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-outline-secondary" @click="showDetail('Student Profile Detail', s)">Show</button>
                    <button v-if="!s.is_blacklisted" class="btn btn-sm btn-warning"
                      @click="toggleBlacklist('student', s.id, true)">Blacklist</button>
                    <button v-else class="btn btn-sm btn-outline-success"
                      @click="toggleBlacklist('student', s.id, false)">Reinstate</button>
                    <button class="btn btn-sm btn-danger d-flex align-items-center gap-1" @click="deleteItem('student', s.id)">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                      </svg>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="students.length === 0">
                <td colspan="6" class="text-center text-muted">No students found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="activeTab === 'drives'">
        <div class="table-responsive">
          <table class="table table-striped table-hover align-middle border bg-white">
            <thead><tr>
              <th>Drive</th><th>Company</th><th>Job Title</th><th>Status</th><th>Actions</th>
            </tr></thead>
            <tbody>
              <tr v-for="d in drives" :key="d.id">
                <td class="text-dark">{{ d.drive_name }}</td>
                <td class="text-muted small">{{ d.company_name }}</td>
                <td class="text-dark">{{ d.job_title }}</td>
                <td>
                  <span class="badge" :class="`badge-${d.status}`">{{ d.status }}</span>
                </td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-outline-secondary" @click="showDetail('Drive Detail', d)">Show</button>
                    <div class="d-flex gap-1" v-if="d.status === 'pending'">
                      <button class="btn btn-sm btn-success" @click="approveDrive(d.id, 'approved')">Approve</button>
                      <button class="btn btn-sm btn-danger"  @click="approveDrive(d.id, 'rejected')">Reject</button>
                    </div>
                    <button class="btn btn-sm btn-danger d-flex align-items-center gap-1" @click="deleteItem('drive', d.id)">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                      </svg>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="drives.length === 0">
                <td colspan="5" class="text-center text-muted">No drives found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else-if="activeTab === 'applications'">
        <div class="table-responsive">
          <table class="table table-striped table-hover align-middle border bg-white">
            <thead><tr>
              <th>Student</th><th>Company</th><th>Drive</th><th>Status</th><th>Applied</th><th>Actions</th>
            </tr></thead>
            <tbody>
              <tr v-for="a in applications" :key="a.id">
                <td class="text-dark">{{ a.student_name }}</td>
                <td class="text-muted small">{{ a.company_name }}</td>
                <td class="text-dark">{{ a.drive_name }}</td>
                <td>
                  <span class="badge" :class="`badge-${a.status}`">{{ a.status }}</span>
                </td>
                <td class="text-muted small">{{ new Date(a.applied_at).toLocaleDateString() }}</td>
                <td>
                  <div class="d-flex gap-1">
                    <button class="btn btn-sm btn-outline-secondary" @click="showDetail('Application Detail', a)">Show</button>
                    <button class="btn btn-sm btn-danger d-flex align-items-center gap-1" @click="deleteItem('application', a.id)">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                      </svg>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="applications.length === 0">
                <td colspan="6" class="text-center text-muted">No applications yet</td>
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

      <div v-else-if="activeTab === 'jobs'">
        <div class="row g-4">

          <div class="col-md-4">
            <div class="card p-4 h-100 bg-white border">
              <h6 class="text-dark mb-1">Send Daily Reminders</h6>
              <p class="text-muted small mb-3">
                Emails all active students about placement drives with deadlines in the next 3 days.
                Students already applied to a drive won't be emailed for it.
              </p>
              
              <div v-if="reminderStatus === 'sent'" class="alert alert-success py-2 mb-2 small">
                Reminder job dispatched! Emails are being sent.
              </div>
              <div v-if="reminderStatus === 'error'" class="alert alert-danger py-2 mb-2 small">
                Failed to trigger. Is Celery running?
              </div>
              <button
                id="btn-send-reminders"
                class="btn btn-primary mt-auto d-flex align-items-center justify-content-center gap-2"
                @click="sendReminders"
                :disabled="reminderLoading"
              >
                <span v-if="reminderLoading" class="spinner-border spinner-border-sm me-2"></span>
                Send Reminders
              </button>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card p-4 h-100 bg-white border">
              <h6 class="text-dark mb-1">Generate Monthly Report</h6>
              <p class="text-muted small mb-3">
                Generates an HTML email report with placement stats (drives, applications,
                selected, shortlisted, rejected) and sends it to the admin email.
              </p>
              <div v-if="reportStatus === 'sent'" class="alert alert-success py-2 mb-2 small">
                Report job dispatched! Check your admin email.
              </div>
              <div v-if="reportStatus === 'error'" class="alert alert-danger py-2 mb-2 small">
                Failed to trigger. Is Celery running?
              </div>
              <button
                id="btn-monthly-report"
                class="btn btn-info mt-auto text-white d-flex align-items-center justify-content-center gap-2"
                @click="generateReport"
                :disabled="reportLoading"
              >
                <span v-if="reportLoading" class="spinner-border spinner-border-sm me-2"></span>
                Generate & Send
              </button>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card p-4 h-100 bg-white border">
              <h6 class="text-dark mb-1">Download Placement Stats CSV</h6>
              <p class="text-muted small mb-3">
                Downloads a full CSV of all placement drives with applicant counts and status
                breakdowns (applied, shortlisted, selected, rejected). Instant — no email needed.
              </p>
              <div v-if="csvMsg" class="alert alert-success py-2 mb-2 small">{{ csvMsg }}</div>
              <button
                id="btn-download-admin-csv"
                class="btn btn-success mt-auto d-flex align-items-center justify-content-center gap-2"
                @click="downloadCsv"
                :disabled="csvLoading"
              >
                <span v-if="csvLoading" class="spinner-border spinner-border-sm me-2"></span>
                Download CSV
              </button>
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

const activeTab  = ref('overview')
const tabLoading = ref(false)

const stats        = ref(null)
const companies    = ref([])
const students     = ref([])
const drives       = ref([])
const applications = ref([])
const search       = ref('')

const reminderLoading = ref(false)
const reminderStatus  = ref('')   
const reportLoading   = ref(false)
const reportStatus    = ref('')   
const csvLoading      = ref(false)
const csvMsg          = ref('')

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

const statCards = [
  { label: 'Students',    icon: '', field: 'total_students'    },
  { label: 'Companies',   icon: '', field: 'total_companies'   },
  { label: 'Drives',      icon: '', field: 'total_drives'      },
  { label: 'Pending Co.', icon: '', field: 'pending_companies' },
  { label: 'Pending Drives', icon: '', field: 'pending_drives' },
  { label: 'Applications', icon: '', field: 'total_applications' },
]

const tabs = [
  { id: 'overview',      label: 'Overview'        },
  { id: 'companies',     label: 'Companies'       },
  { id: 'students',      label: 'Students'        },
  { id: 'drives',        label: 'Drives'          },
  { id: 'applications',  label: 'Applications'    },
  { id: 'jobs',          label: 'Jobs & Downloads' },
]

onMounted(async () => {
  try {
    stats.value = await api.getAdminDashboard()
  } catch (e) {
    console.error('Failed to load dashboard stats', e)
  }
})

async function loadTab(tab) {
  tabLoading.value = true
  try {
    if (tab === 'companies')    companies.value    = await api.getCompanies()
    if (tab === 'students')     students.value     = await api.getStudents()
    if (tab === 'drives')       drives.value       = await api.getAdminDrives()
    if (tab === 'applications') applications.value = await api.getAdminApplications()
    
  } finally {
    tabLoading.value = false
  }
}

async function searchCompanies() {
  companies.value = await api.getCompanies(search.value)
}
async function searchStudents() {
  students.value = await api.getStudents(search.value)
}

async function approveCompany(id, action) {
  await api.approveCompany(id, action)
  companies.value = await api.getCompanies()
  stats.value     = await api.getAdminDashboard()
}

async function approveDrive(id, action) {
  await api.approveDrive(id, action)
  drives.value = await api.getAdminDrives()
  stats.value  = await api.getAdminDashboard()
}

async function toggleBlacklist(type, id, blacklist) {
  if (type === 'company') {
    await api.blacklistCompany(id, blacklist)
    companies.value = await api.getCompanies()
  } else {
    await api.blacklistStudent(id, blacklist)
    students.value = await api.getStudents()
  }
}

async function deleteItem(type, id) {
  if (!confirm(`Are you sure you want to delete this ${type}? This action is permanent.`)) return
  try {
    if (type === 'company') {
      await api.deleteCompany(id)
      companies.value = await api.getCompanies()
    } else if (type === 'student') {
      await api.deleteStudent(id)
      students.value = await api.getStudents()
    } else if (type === 'drive') {
      await api.deleteDrive(id)
      drives.value = await api.getAdminDrives()
    } else if (type === 'application') {
      await api.deleteApplication(id)
      applications.value = await api.getAdminApplications()
    }
    stats.value = await api.getAdminDashboard()
  } catch (e) {
    alert(e.response?.data?.error || `Failed to delete ${type}.`)
  }
}

async function sendReminders() {
  reminderLoading.value = true
  reminderStatus.value  = ''
  try {
    await api.triggerDailyReminders()
    reminderStatus.value = 'sent'
    setTimeout(() => { reminderStatus.value = '' }, 6000)
  } catch (e) {
    reminderStatus.value = 'error'
    setTimeout(() => { reminderStatus.value = '' }, 6000)
  } finally {
    reminderLoading.value = false
  }
}

async function generateReport() {
  reportLoading.value = true
  reportStatus.value  = ''
  try {
    await api.triggerMonthlyReport()
    reportStatus.value = 'sent'
    setTimeout(() => { reportStatus.value = '' }, 6000)
  } catch (e) {
    reportStatus.value = 'error'
    setTimeout(() => { reportStatus.value = '' }, 6000)
  } finally {
    reportLoading.value = false
  }
}

async function downloadCsv() {
  csvLoading.value = true
  csvMsg.value     = ''
  try {
    await api.downloadAdminStatsCsv()
    csvMsg.value = '✅ Download started!'
    setTimeout(() => { csvMsg.value = '' }, 4000)
  } catch (e) {
    csvMsg.value = '❌ Download failed.'
  } finally {
    csvLoading.value = false
  }
}

function logout() {
  clearUser()
  router.push('/')
}
</script>