<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '@/api/admin';

const route = useRoute();
const router = useRouter();
const patientId = route.params.id;

const patient = ref(null);
const appointments = ref([]);
const loading = ref(true);
const message = ref('');

async function loadPatientHistory() {
  try {
    // Get patient details
    const patientRes = await api(`/admin/patients/${patientId}`);
    patient.value = patientRes;

    // Get patient appointments (you may need to add this endpoint)
    // For now, we'll just show the patient details
  } catch (err) {
    message.value = err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadPatientHistory);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">Patient History</h3>

    <div v-if="message" class="alert alert-danger">{{ message }}</div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="patient" class="row">
      <!-- Patient Details -->
      <div class="col-md-4">
        <div class="card mb-3">
          <div class="card-body">
            <h5 class="card-title">Patient Details</h5>
            <div class="mb-2">
              <strong>Name:</strong> {{ patient.name }}
            </div>
            <div class="mb-2">
              <strong>Email:</strong> {{ patient.email }}
            </div>
            <div class="mb-2">
              <strong>Status:</strong>
              <span v-if="patient.is_active" class="badge bg-success">Active</span>
              <span v-else class="badge bg-danger">Inactive</span>
            </div>
            <div class="mb-2">
              <strong>Medical History:</strong>
              <p class="text-muted small">{{ patient.medical_history || 'No history recorded' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Appointments -->
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Appointments</h5>
            <div class="alert alert-info">
              Appointment history feature coming soon
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>