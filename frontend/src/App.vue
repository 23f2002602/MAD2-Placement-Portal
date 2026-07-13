<template>
  
  <div v-if="store.loading" class="d-flex justify-content-center align-items-center vh-100">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>

  <router-view v-else />
</template>

<script setup>
import { onMounted } from 'vue'
import { store, restoreSession } from './store.js'

onMounted(() => {
  restoreSession()
})
</script>

<style>

body {
  background-color: #f8f9fa;
  color: #212529;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.card {
  background-color: #ffffff !important;
  border: 1px solid #dee2e6 !important;
  color: #212529 !important;
  border-radius: 4px !important;
}

.badge-pending    { background-color: #ffc107; color: #212529; }
.badge-approved   { background-color: #28a745; color: #ffffff; }
.badge-rejected   { background-color: #dc3545; color: #ffffff; }
.badge-closed     { background-color: #6c757d; color: #ffffff; }
.badge-selected   { background-color: #28a745; color: #ffffff; }
.badge-shortlisted { background-color: #17a2b8; color: #ffffff; }
.badge-applied    { background-color: #007bff; color: #ffffff; }
.badge-waiting    { background-color: #ffc107; color: #212529; }
</style>