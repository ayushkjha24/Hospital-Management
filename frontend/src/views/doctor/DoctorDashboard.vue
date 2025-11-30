<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/doctor';
import { useRouter } from 'vue-router';
import PatientHistoryTable from '@/components/PatientHistoryTable.vue';

const router = useRouter();
const appointments = ref([]);
const patients = ref([]);
const stats = ref({ upcoming_appointments: 0, total_patients: 0 });
const loading = ref(true);
const message = ref('');
const messageClass = ref('alert-success');

// Patient history modal
const showHistoryModal = ref(false);
const historyPatient = ref({ id: null, name: '' });
const historyData = ref([]);
const historyRole = ref('doctor');

async function loadData() {
  loading.value = true;
  try {
    const dashRes = await api('/dashboard');
    stats.value = dashRes;

    const apptsRes = await api('/appointments/upcoming');
    appointments.value = apptsRes?.appointments || [];

    const patientsRes = await api('/assigned-patients');
    patients.value = patientsRes?.patients || [];

  } catch (err) {
    message.value = err.message;
    messageClass.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
}

async function updateStatus(apptId, status) {
  try {
    await api(`/appointment/${apptId}/status`, 'POST', { status });
    message.value = `Appointment marked as ${status}`;
    messageClass.value = 'alert-success';
    await loadData();
  } catch (err) {
    message.value = err.message;
    messageClass.value = 'alert-danger';
  }
}

async function viewHistory(patient) {
  try {
    showHistoryModal.value = false;
    historyData.value = [];

    const pid = patient.id || patient.patient_id;
    const pname = patient.name || patient.patient_name || "Unknown";

    historyPatient.value = { id: pid, name: pname };

    if (!pid) {
      message.value = "Patient ID missing";
      messageClass.value = "alert-danger";
      return;
    }

    // Access admin endpoint using skipPrefix = true
    const res = await api(`/admin/patients/${pid}/history`, 'GET', null, true);
    const arr = Array.isArray(res?.history) ? res.history : [];

    historyData.value = arr.map((h, idx) => ({
      id: h.id ?? idx + 1,
      visit_no: idx + 1,
      visit_type: h.visit_type || h.type || "In-person",
      tests_done: h.tests_done || "",
      diagnosis: h.diagnosis || "",
      prescription: h.prescription || "",
      medicines: h.medicines || []
    }));

    showHistoryModal.value = true;
  } catch (err) {
    message.value = "Failed to load history: " + (err.message || err);
    messageClass.value = "alert-danger";
  }
}

function goToUpdateHistory(appointmentId, patientId) {
  router.push(`/doctor/patient/${patientId}/appointment/${appointmentId}/update-history`);
}

onMounted(loadData);
</script>

<template>
  <div class="container py-4">

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center py-5">
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
      <div class="card mb-4">
        <div class="card-header bg-light">
          <h5 class="mb-0">Upcoming Appointments</h5>
        </div>
        <div class="card-body">
          <div v-if="appointments.length === 0" class="alert alert-info mb-0">
            No upcoming appointments
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover table-bordered mb-0">
              <thead class="table-primary">
                <tr>
                  <th>Sr No.</th>
                  <th>Patient Name</th>
                  <th>Date & Time</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(appt, i) in appointments" :key="appt.id">
                  <td>{{ i + 1 }}</td>
                  <td>{{ appt.patient_name }}</td>
                  <td>{{ appt.appointment_time }}</td>
                  <td>
                    <span class="badge bg-warning">{{ appt.status }}</span>
                  </td>
                  <td>
                    <button
                      @click="goToUpdateHistory(appt.id, appt.patient_id)"
                      class="btn btn-sm btn-info me-1"
                    >
                      Update History
                    </button>
                    <button
                      @click="updateStatus(appt.id, 'completed')"
                      class="btn btn-sm btn-success me-1"
                    >
                      Complete
                    </button>
                    <button
                      @click="updateStatus(appt.id, 'cancelled')"
                      class="btn btn-sm btn-danger"
                    >
                      Cancel
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Assigned Patients -->
      <div class="card mb-4">
        <div class="card-header bg-light">
          <h5 class="mb-0">Assigned Patients</h5>
        </div>
        <div class="card-body">
          <div v-if="patients.length === 0" class="alert alert-info mb-0">
            No patients assigned
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover table-bordered mb-0">
              <thead class="table-primary">
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="patient in patients" :key="patient.id">
                  <td>{{ patient.name }}</td>
                  <td>{{ patient.email }}</td>
                  <td>{{ patient.phone }}</td>
                  <td>
                    <button
                      @click="viewHistory(patient)"
                      class="btn btn-sm btn-primary"
                    >
                      View History
                    </button>

                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Availability Button -->
      <RouterLink to="/doctor/availability" class="btn btn-success btn-lg">
        + Provide Availability for 7 Days
      </RouterLink>
    </div>

    <!-- Patient History Modal -->
    <div
      v-if="showHistoryModal"
      class="modal-backdrop"
      style="position:fixed;inset:0;z-index:1050;display:flex;align-items:center;justify-content:center;padding:1rem;"
    >
      <div class="modal-dialog modal-lg" style="max-width:1000px;">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient History — {{ historyPatient.name }}</h5>
            <button type="button" class="btn-close" @click="showHistoryModal = false"></button>
          </div>

          <div class="modal-body">
            <PatientHistoryTable
              :patient="historyPatient"
              :history="historyData"
              :role="historyRole"
              :showBack="false"
            />
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showHistoryModal = false">
              Close
            </button>

            <RouterLink
              v-if="historyPatient.id"
              :to="`/doctor/patient/${historyPatient.id}/history`"
              class="btn btn-primary"
            >
              Open Full Record
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: none;
}

.table-hover tbody tr:hover {
  background-color: #f8f9fa;
}

.btn-sm {
  font-size: 0.85rem;
  padding: 0.4rem 0.6rem;
}
</style>
