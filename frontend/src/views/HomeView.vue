<script setup>
import { useAuthStore } from "@/stores/auth.js"

import AdminDashboard from "@/views/admin/AdminDashboard.vue"
import DoctorDashboard from "@/views/doctor/DoctorDashboard.vue"
import PatientDashboard from "@/views/patient/PatientDashboard.vue"

const auth = useAuthStore()
</script>

<template>
  <!-- Not logged in → Show public homepage -->
  <div v-if="!auth.role">
    <h1>Welcome to Medisphere</h1>
    <p>Public content here…</p>
  </div>

  <!-- Admin Dashboard -->
  <AdminDashboard v-else-if="auth.role === 'admin'" />

  <!-- Doctor Dashboard -->
  <DoctorDashboard v-else-if="auth.role === 'doctor'" />

  <!-- Patient Dashboard -->
  <PatientDashboard v-else-if="auth.role === 'patient'" />
</template>

