import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

http.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  response => response,   
  async error => {
    const original = error.config

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          
          const res = await axios.post('/api/auth/refresh', {}, {
            headers: { 'Authorization': `Bearer ${refreshToken}` }
          })
          localStorage.setItem('access_token', res.data.access_token)
          
          original.headers['Authorization'] = `Bearer ${res.data.access_token}`
          return http(original)
        } catch (refreshError) {
          
          localStorage.clear()
          window.location.href = '/'
        }
      }
    }

    return Promise.reject(error)
  }
)

const api = {
  
  login(credentials) {
    return http.post('/auth/login', credentials).then(r => r.data)
  },

  register(userData) {
    return http.post('/auth/register', userData).then(r => r.data)
  },

  getMe() {
    return http.get('/auth/me').then(r => r.data)
  },

  getAdminDashboard() {
    return http.get('/admin/dashboard').then(r => r.data)
  },

  getCompanies(search = '') {
    return http.get('/admin/companies', { params: { search } }).then(r => r.data)
  },
  approveCompany(id, action) {
    return http.patch(`/admin/companies/${id}/approve`, { action }).then(r => r.data)
  },
  blacklistCompany(id, blacklist) {
    return http.patch(`/admin/companies/${id}/blacklist`, { blacklist }).then(r => r.data)
  },
  deleteCompany(id) {
    return http.delete(`/admin/companies/${id}`).then(r => r.data)
  },

  getStudents(search = '') {
    return http.get('/admin/students', { params: { search } }).then(r => r.data)
  },
  blacklistStudent(id, blacklist) {
    return http.patch(`/admin/students/${id}/blacklist`, { blacklist }).then(r => r.data)
  },
  deleteStudent(id) {
    return http.delete(`/admin/students/${id}`).then(r => r.data)
  },

  getAdminDrives(status = '', search = '') {
    return http.get('/admin/drives', { params: { status, search } }).then(r => r.data)
  },
  approveDrive(id, action) {
    return http.patch(`/admin/drives/${id}/approve`, { action }).then(r => r.data)
  },
  deleteDrive(id) {
    return http.delete(`/admin/drives/${id}`).then(r => r.data)
  },

  getAdminApplications() {
    return http.get('/admin/applications').then(r => r.data)
  },
  deleteApplication(id) {
    return http.delete(`/admin/applications/${id}`).then(r => r.data)
  },

  getCompanyDashboard() {
    return http.get('/company/dashboard').then(r => r.data)
  },
  getCompanyProfile() {
    return http.get('/company/profile').then(r => r.data)
  },
  updateCompanyProfile(data) {
    return http.put('/company/profile', data).then(r => r.data)
  },
  createDrive(data) {
    return http.post('/company/drives', data).then(r => r.data)
  },
  deleteOwnDrive(id) {
    return http.delete(`/company/drives/${id}`).then(r => r.data)
  },
  getCompanyDrives() {
    return http.get('/company/drives').then(r => r.data)
  },
  closeDrive(id) {
    return http.patch(`/company/drives/${id}/close`).then(r => r.data)
  },
  getDriveApplications(driveId) {
    return http.get(`/company/drives/${driveId}/applications`).then(r => r.data)
  },
  updateApplicationStatus(appId, status) {
    return http.patch(`/company/applications/${appId}/status`, { status }).then(r => r.data)
  },

  getStudentDashboard() {
    return http.get('/student/dashboard').then(r => r.data)
  },
  getStudentProfile() {
    return http.get('/student/profile').then(r => r.data)
  },
  updateStudentProfile(data) {
    return http.put('/student/profile', data).then(r => r.data)
  },
  uploadResume(formData) {
    
    return http.post('/student/profile/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(r => r.data)
  },
  getDrives(search = '', eligibleOnly = false) {
    return http.get('/student/drives', { params: { search, eligible_only: eligibleOnly } }).then(r => r.data)
  },
  applyToDrive(driveId) {
    return http.post(`/student/drives/${driveId}/apply`).then(r => r.data)
  },
  getMyApplications() {
    return http.get('/student/applications').then(r => r.data)
  },
  withdrawApplication(appId) {
    return http.delete(`/student/applications/${appId}`).then(r => r.data)
  },
  getHistory() {
    return http.get('/student/history').then(r => r.data)
  },
  exportCsv() {
    return http.post('/student/export/csv').then(r => r.data)
  },

  getExportStatus(taskId) {
    return http.get(`/student/export/status/${taskId}`).then(r => r.data)
  },

  getExportDownloadUrl(filename) {
    return `/api/student/export/download/${filename}`
  },

  getStudentDirectCsvUrl() {
    const token = localStorage.getItem('access_token')
    return `/api/student/export/direct-csv?token=${token}`
  },

  downloadWithAuth(url, filename) {
    const token = localStorage.getItem('access_token')
    return fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.blob())
      .then(blob => {
        const a = document.createElement('a')
        a.href  = URL.createObjectURL(blob)
        a.download = filename
        a.click()
        URL.revokeObjectURL(a.href)
      })
  },

  downloadAdminStatsCsv() {
    return this.downloadWithAuth('/api/admin/export/stats', `admin_stats_${new Date().toISOString().slice(0,10)}.csv`)
  },

  triggerDailyReminders() {
    return http.post('/admin/jobs/send-reminders').then(r => r.data)
  },

  triggerMonthlyReport() {
    return http.post('/admin/jobs/monthly-report').then(r => r.data)
  },

  downloadCompanyStatsCsv() {
    return this.downloadWithAuth('/api/company/export/stats', `company_stats_${new Date().toISOString().slice(0,10)}.csv`)
  },

  downloadStudentCsvDirect() {
    return this.downloadWithAuth('/api/student/export/direct-csv', `my_applications_${new Date().toISOString().slice(0,10)}.csv`)
  },
}

export default api