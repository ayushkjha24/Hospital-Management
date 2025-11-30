<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/admin';
import { useRouter } from 'vue-router';

const router = useRouter();

// Stats
const stats = ref({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
  upcoming_appointments: 0
});

// Doctors
const doctors = ref([]);
const doctorsLoading = ref(true);

// Patients
const patients = ref([]);
const patientsLoading = ref(true);

// Appointments
const appointments = ref([]);
const appointmentsLoading = ref(true);

// Search & Filter
const searchQuery = ref('');
const searchType = ref('doctor'); // doctor or patient
const searchResults = ref([]);
const showSearchResults = ref(false);

// UI State
const message = ref('');
const messageClass = ref('alert-success');

// ===================== Stats =====================
async function loadStats() {
  try {
    const res = await api('/admin/dashboard');
    stats.value = res;
  } catch (err) {
    showMessage(err.message, true);
  }
}

// ===================== Doctors =====================
async function loadDoctors() {
  doctorsLoading.value = true;
  try {
    const res = await api('/admin/doctors');
    doctors.value = (res && res.doctors) ? res.doctors.slice(0, 5) : [];
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    doctorsLoading.value = false;
  }
}

async function deleteDoctor(id) {
  if (!confirm('Delete this doctor?')) return;
  try {
    await api(`/admin/doctors/${id}`, 'DELETE');
    showMessage('Doctor deleted');
    loadDoctors();
  } catch (err) {
    showMessage(err.message, true);
  }
}

async function blacklistDoctor(id) {
  if (!confirm('Blacklist this doctor?')) return;
  try {
    await api(`/admin/doctors/${id}/blacklist`, 'POST');
    showMessage('Doctor blacklisted');
    loadDoctors();
  } catch (err) {
    showMessage(err.message, true);
  }
}

// ===================== Patients =====================
async function loadPatients() {
  patientsLoading.value = true;
  try {
    const res = await api('/admin/patients');
    patients.value = (res && res.patients) ? res.patients.slice(0, 5) : [];
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    patientsLoading.value = false;
  }
}

async function deletePatient(id) {
  if (!confirm('Are you sure you want to delete this patient?')) return;
  try {
    await api(`/admin/patients/${id}`, 'DELETE');
    showMessage('Patient deleted');
    loadPatients();
  } catch (err) {
    showMessage(err.message, true);
  }
}

async function blacklistPatient(id) {
  if (!confirm('Blacklist this patient?')) return;
  try {
    await api(`/admin/patients/${id}/blacklist`, 'POST');
    showMessage('Patient blacklisted');
    loadPatients();
  } catch (err) {
    showMessage(err.message, true);
  }
}

// ===================== Appointments =====================
async function loadAppointments() {
  appointmentsLoading.value = true;
  try {
    const res = await api('/admin/appointments');
    appointments.value = (res && res.appointments) ? res.appointments.slice(0, 5) : [];
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    appointmentsLoading.value = false;
  }
}

// ===================== Search =====================
async function performSearch() {
  if (!searchQuery.value.trim()) {
    searchResults.value = [];
    showSearchResults.value = false;
    return;
  }

  try {
    if (searchType.value === 'doctor') {
      const res = await api(`/admin/search/doctors?q=${encodeURIComponent(searchQuery.value)}`);
      searchResults.value = (res && res.doctors) ? res.doctors : [];
    } else {
      const res = await api(`/admin/search/patients?q=${encodeURIComponent(searchQuery.value)}`);
      searchResults.value = (res && res.patients) ? res.patients : [];
    }
    showSearchResults.value = true;
  } catch (err) {
    showMessage(err.message, true);
  }
}

// ===================== Utilities =====================
function showMessage(msg, isError = false) {
  message.value = msg;
  messageClass.value = isError ? 'alert-danger' : 'alert-success';
  setTimeout(() => (message.value = ''), 4000);
}

function goToAllDoctors() {
  router.push('/admin/doctors');
}

function goToAllPatients() {
  router.push('/admin/patients');
}

function goToAllAppointments() {
  router.push('/admin/appointments');
}

function viewPatientHistory(patientId) {
  router.push(`/admin/patients/${patientId}/history`);
}

// ===================== Lifecycle =====================
onMounted(async () => {
  await loadStats();
  await loadDoctors();
  await loadPatients();
  await loadAppointments();
});
</script>

<template>
  <div class="container-fluid py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold">Welcome Admin</h2>
      <div class="d-flex gap-2">
        <div class="input-group" style="max-width: 300px;">
          <input
            v-model="searchQuery"
            @keyup.enter="performSearch"
            type="text"
            class="form-control"
            placeholder="Doctor, patient, department..."
          />
          <select v-model="searchType" class="form-select" style="max-width: 120px;">
            <option value="doctor">Doctor</option>
            <option value="patient">Patient</option>
          </select>
          <button @click="performSearch" class="btn btn-outline-primary">Search</button>
        </div>
      </div>
    </div>

    <!-- Message -->
    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

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

    <!-- Search Results -->
    <div v-if="showSearchResults" class="card mb-4">
      <div class="card-header bg-light">
        <h6 class="mb-0">
          Search Results ({{ searchType === 'doctor' ? 'Doctors' : 'Patients' }})
        </h6>
      </div>
      <div class="card-body">
        <div v-if="searchResults.length === 0" class="alert alert-info mb-0">
          No results found
        </div>
        <div v-else class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th v-if="searchType === 'doctor'">Specialization</th>
                <th v-if="searchType === 'doctor'">Department</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in searchResults" :key="item.id">
                <td>{{ item.name }}</td>
                <td>{{ item.email }}</td>
                <td v-if="searchType === 'doctor'">{{ item.specialization }}</td>
                <td v-if="searchType === 'doctor'">{{ item.department || 'N/A' }}</td>
                <td>
                  <RouterLink
                    v-if="searchType === 'doctor'"
                    :to="`/admin/doctors/edit/${item.id}`"
                    class="btn btn-sm btn-warning me-1"
                  >
                    Edit
                  </RouterLink>
                  <RouterLink
                    v-if="searchType === 'patient'"
                    :to="`/admin/patients/${item.id}`"
                    class="btn btn-sm btn-info me-1"
                  >
                    View
                  </RouterLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Registered Doctors Section -->
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center bg-light">
        <h6 class="mb-0">Registered Doctors</h6>
        <RouterLink to="/admin/doctors/add" class="btn btn-sm btn-success">
          + Create
        </RouterLink>
      </div>
      <div class="card-body">
        <div v-if="doctorsLoading" class="text-center">
          <div class="spinner-border spinner-border-sm" role="status"></div>
        </div>
        <div v-else-if="doctors.length === 0" class="alert alert-info mb-0">
          No doctors found
        </div>
        <div v-else class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Specialization</th>
                <th>Experience</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in doctors" :key="doctor.id">
                <td>{{ doctor.name }}</td>
                <td>{{ doctor.email }}</td>
                <td>{{ doctor.specialization }}</td>
                <td>{{ doctor.experience_years }} years</td>
                <td>
                  <span v-if="doctor.is_approved" class="badge bg-success">Approved</span>
                  <span v-else class="badge bg-warning">Pending</span>
                </td>
                <td>
                  <RouterLink :to="`/admin/doctors/edit/${doctor.id}`" class="btn btn-sm btn-warning me-1">
                    Edit
                  </RouterLink>
                  <button @click="blacklistDoctor(doctor.id)" class="btn btn-sm btn-dark me-1">
                    Blacklist
                  </button>
                  <button @click="deleteDoctor(doctor.id)" class="btn btn-sm btn-danger">
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card-footer bg-light text-center">
        <button @click="goToAllDoctors" class="btn btn-sm btn-link">
          View All Doctors →
        </button>
      </div>
    </div>

    <!-- Registered Patients Section -->
    <div class="card mb-4">
      <div class="card-header bg-light">
        <h6 class="mb-0">Registered Patients</h6>
      </div>
      <div class="card-body">
        <div v-if="patientsLoading" class="text-center">
          <div class="spinner-border spinner-border-sm" role="status"></div>
        </div>
        <div v-else-if="patients.length === 0" class="alert alert-info mb-0">
          No patients found
        </div>
        <div v-else class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Appointments</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in patients" :key="patient.id">
                <td>{{ patient.name }}</td>
                <td>{{ patient.email }}</td>
                <td>{{ patient.phone || 'N/A' }}</td>
                <td>
                  <span class="badge bg-info">{{ patient.appointments_count || 0 }}</span>
                </td>
                <td>
                  <button @click="viewPatientHistory(patient.id)" class="btn btn-sm btn-info me-1">
                    View History
                  </button>
                  <button @click="blacklistPatient(patient.id)" class="btn btn-sm btn-dark me-1">
                    Blacklist
                  </button>
                  <button @click="deletePatient(patient.id)" class="btn btn-sm btn-danger">
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card-footer bg-light text-center">
        <button @click="goToAllPatients" class="btn btn-sm btn-link">
          View All Patients →
        </button>
      </div>
    </div>

    <!-- Upcoming Appointments Section -->
    <div class="card">
      <div class="card-header bg-light">
        <h6 class="mb-0">Upcoming Appointments</h6>
      </div>
      <div class="card-body">
        <div v-if="appointmentsLoading" class="text-center">
          <div class="spinner-border spinner-border-sm" role="status"></div>
        </div>
        <div v-else-if="appointments.length === 0" class="alert alert-info mb-0">
          No upcoming appointments
        </div>
        <div v-else class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Sr No.</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Department</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(appt, i) in appointments" :key="appt.id">
                <td>{{ i + 1 }}</td>
                <td>{{ appt.patient }}</td>
                <td>{{ appt.doctor }}</td>
                <td>{{ appt.department }}</td>
                <td>{{ appt.date }}</td>
                <td>{{ appt.time }}</td>
                <td>
                  <span class="badge bg-warning">{{ appt.status }}</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-primary">View</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="card-footer bg-light text-center">
        <button @click="goToAllAppointments" class="btn btn-sm btn-link">
          View All Appointments →
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: none;
  margin-bottom: 1.5rem;
}

.card-header {
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
}

.table-hover tbody tr:hover {
  background-color: #f8f9fa;
}

.btn-sm {
  font-size: 0.85rem;
  padding: 0.4rem 0.6rem;
}

.badge {
  font-size: 0.85rem;
  padding: 0.4rem 0.6rem;
}

.input-group {
  border-radius: 4px;
  overflow: hidden;
}
</style>
