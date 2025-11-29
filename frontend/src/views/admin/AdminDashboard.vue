<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/admin';
import { useRouter } from 'vue-router';

const router = useRouter();
const stats = ref({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
  upcoming_appointments: 0
});

const loading = ref(true);
const message = ref('');
const messageClass = ref('alert-success');

async function loadStats() {
  try {
    const res = await api('/admin/dashboard');
    stats.value = res;
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    loading.value = false;
  }
}

function showMessage(msg, isError = false) {
  message.value = msg;
  messageClass.value = isError ? 'alert-danger' : 'alert-success';
  setTimeout(() => (message.value = ''), 4000);
}

onMounted(loadStats);
</script>

<template>
  <div class="container py-4">
    <h2 class="fw-bold mb-4">Admin Dashboard</h2>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h6 class="card-title">Total Doctors</h6>
              <h3 class="card-text">{{ stats.total_doctors }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white">
            <div class="card-body">
              <h6 class="card-title">Total Patients</h6>
              <h3 class="card-text">{{ stats.total_patients }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-info text-white">
            <div class="card-body">
              <h6 class="card-title">Total Appointments</h6>
              <h3 class="card-text">{{ stats.total_appointments }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-warning text-white">
            <div class="card-body">
              <h6 class="card-title">Upcoming</h6>
              <h3 class="card-text">{{ stats.upcoming_appointments }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="d-flex gap-2 mb-4">
        <RouterLink to="/admin/doctors" class="btn btn-primary">
          Manage Doctors
        </RouterLink>
        <RouterLink to="/admin/patients" class="btn btn-success">
          Manage Patients
        </RouterLink>
        <RouterLink to="/admin/appointments" class="btn btn-info">
          View Appointments
        </RouterLink>
      </div>
    </div>
  </div>
</template>
