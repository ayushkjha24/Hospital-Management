<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/doctor';
import { useRouter } from 'vue-router';

const router = useRouter();
const appointments = ref([]);
const patients = ref([]);
const stats = ref({ upcoming_appointments: 0, total_patients: 0 });
const loading = ref(true);
const message = ref('');

async function loadData() {
  try {
    stats.value = await api('/dashboard');
    appointments.value = (await api('/appointments/upcoming')) || [];
    patients.value = (await api('/assigned-patients')) || [];
  } catch (err) {
    message.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function updateStatus(apptId, status) {
  try {
    await api(`/appointment/${apptId}/status`, 'PATCH', { status });
    await loadData();
  } catch (err) {
    message.value = err.message;
  }
}

onMounted(loadData);
</script>

<template>
  <div class="container py-4">
    <h2 class="fw-bold mb-4">Welcome Doctor</h2>

    <div v-if="message" class="alert alert-danger">{{ message }}</div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <!-- Stats -->
      <div class="row mb-4">
        <div class="col-md-6">
          <div class="card bg-info text-white">
            <div class="card-body">
              <h6 class="card-title">Upcoming Appointments</h6>
              <h3 class="card-text">{{ stats.upcoming_appointments }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card bg-primary text-white">
            <div class="card-body">
              <h6 class="card-title">Assigned Patients</h6>
              <h3 class="card-text">{{ stats.total_patients }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Appointments -->
      <h4 class="mb-3">Upcoming Appointments</h4>
      <table v-if="appointments.length > 0" class="table table-bordered">
        <thead class="table-primary">
          <tr>
            <th>Patient</th>
            <th>Date & Time</th>
            <th>History</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="appt in appointments" :key="appt.id">
            <td>{{ appt.patient_name }}</td>
            <td>{{ appt.appointment_time }}</td>
            <td><span class="badge bg-warning">{{ appt.status }}</span></td>
            <td>
              <button @click="updateStatus(appt.id, 'completed')" class="btn btn-sm btn-success me-1">
                Complete
              </button>
              <button @click="updateStatus(appt.id, 'cancelled')" class="btn btn-sm btn-danger">
                Cancel
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="alert alert-info">No upcoming appointments</div>

      <!-- Assigned Patients -->
      <h4 class="mb-3 mt-4">Assigned Patients</h4>
      <table v-if="patients.length > 0" class="table table-bordered">
        <thead class="table-primary">
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="patient in patients" :key="patient.id">
            <td>{{ patient.name }}</td>
            <td>{{ patient.email }}</td>
            <td>{{ patient.phone }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else class="alert alert-info">No patients assigned</div>

      <!-- Availability Button -->
      <div class="mt-4">
        <RouterLink to="/doctor/availability" class="btn btn-success">
          Provide Availability
        </RouterLink>
      </div>
    </div>
  </div>
</template>