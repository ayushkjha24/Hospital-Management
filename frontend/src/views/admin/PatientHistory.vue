<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '@/api/admin';
import PatientHistoryTable from '@/components/PatientHistoryTable.vue';

const route = useRoute();
const router = useRouter();
// normalize patient id (route param or query)
const patientIdParam = route.params.id;
const patientIdQuery = route.query.id || route.query.patientId;
const patientId = (patientIdParam && patientIdParam !== 'null') ? patientIdParam
  : (patientIdQuery && patientIdQuery !== 'null') ? patientIdQuery
  : null;

const patient = ref(null);
const currentAppointment = ref(null);
const history = ref([]);
const loading = ref(true);
const message = ref('');
const messageClass = ref('alert-danger');

async function loadPatientHistory() {
  loading.value = true;
  message.value = '';
  if (!patientId) {
    message.value = 'No patient selected. Cannot load history.';
    messageClass.value = 'alert-warning';
    loading.value = false;
    return;
  }

  try {
    const patientRes = await api(`/admin/patients/${patientId}`);
    patient.value = patientRes.patient ?? patientRes;

    // admin endpoint now returns current_appointment + history
    let res = await api(`/admin/patients/${patientId}/history`);

    currentAppointment.value = res.current_appointment ?? null;

    if (Array.isArray(res.history)) {
      history.value = res.history.map((h, idx) => ({
        id: h.id ?? idx + 1,
        visit_no: idx + 1,
        visit_type: h.visit_type || 'In-person',
        tests_done: h.tests_done || '',
        diagnosis: h.diagnosis || h.notes || '',
        prescription: h.prescription || '',
        medicines: h.medicines || []
      }));
    } else {
      history.value = [];
    }
  } catch (err) {
    message.value = err?.message || 'Failed to load patient history';
    messageClass.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
}

onMounted(loadPatientHistory);
</script>

<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="fw-bold">Patient History</h3>
    </div>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>
    </div>

    <div v-else-if="patient">
      <div class="row mb-3">
        <div class="col-md-4">
          <div class="card mb-3">
            <div class="card-body">
              <h5 class="card-title">Patient Details</h5>
              <div class="mb-2"><strong>Name:</strong> {{ patient.name }}</div>
              <div class="mb-2"><strong>Email:</strong> {{ patient.email }}</div>
              <div v-if="currentAppointment" class="mt-3">
                <h6 class="mb-1">Next Appointment</h6>
                <div><strong>Doctor:</strong> {{ currentAppointment.doctor_name }}</div>
                <div><strong>Date:</strong> {{ currentAppointment.date }} {{ currentAppointment.time }}</div>
                <div><strong>Status:</strong> {{ currentAppointment.status }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-8">
          <!-- pass role='patient' so no action/view buttons are shown -->
          <PatientHistoryTable
            :patient="{ id: patient.id, name: patient.name }"
            :history="history"
            role="patient"
            :showBack="false"
          />
        </div>
      </div>
    </div>

    <div v-else class="alert alert-info">No patient found.</div>
  </div>
</template>
<style scoped>
.card { box-shadow: 0 2px 4px rgba(0,0,0,0.04); border: none; }
</style>