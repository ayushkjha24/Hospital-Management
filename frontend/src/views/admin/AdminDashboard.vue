<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/admin';
import { useRouter } from 'vue-router';
import PatientHistoryTable from '@/components/PatientHistoryTable.vue';

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
const searchType = ref('doctor'); 
const searchResults = ref([]);
const showSearchResults = ref(false);

// UI State
const message = ref('');
const messageClass = ref('alert-success');

// Patient history modal state
const showHistoryModal = ref(false);
const historyPatient = ref({ id: null, name: '', doctor_name: '', department: '' });
const historyData = ref([]); // pass to PatientHistoryTable
const historyRole = ref('patient'); // show list only (no action buttons)

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

// Show patient history for an appointment (open modal)
async function viewAppointmentHistory(apptOrPatient) {
  // apptOrPatient can be an appointment (with patient/patient_id) or a patient object (with id,name)
  try {
    showHistoryModal.value = false;
    historyData.value = [];
    historyPatient.value = { id: null, name: '', doctor_name: '', department: '' };

    if (!apptOrPatient) {
      showMessage('No patient/appointment provided', true);
      return;
    }

    // normalize id and name
    let pid = null;
    let pname = '';
    // patient object (has id and name/email/phone)
    if (apptOrPatient.id != null && (apptOrPatient.name || apptOrPatient.email || apptOrPatient.phone)) {
      pid = apptOrPatient.id;
      pname = apptOrPatient.name || '';
    } else if (apptOrPatient.patient_id != null) {
      // appointment object with patient_id
      pid = apptOrPatient.patient_id;
      pname = apptOrPatient.patient || '';
    } else if (apptOrPatient.patient) {
      // appointment object with only patient name
      pname = apptOrPatient.patient;
    } else if (apptOrPatient.name) {
      // fallback
      pname = apptOrPatient.name;
    }

    // try search by name if no id
    if (!pid && pname) {
      try {
        const sres = await api(`/admin/search/patients?q=${encodeURIComponent(pname)}`);
        // support both response shapes: array or { patients: [...] }
        let found = null;
        if (Array.isArray(sres) && sres.length > 0) {
          found = sres[0];
        } else if (sres && Array.isArray(sres.patients) && sres.patients.length > 0) {
          found = sres.patients[0];
        }
        if (found) {
          pid = found.id ?? found.patient_id ?? null;
          pname = found.name ?? found.patient ?? pname;
        }
      } catch (e) {
        // ignore search failure, we'll show lightweight modal below
      }
    }

    historyPatient.value = {
      id: pid,
      name: pname || (apptOrPatient.name || apptOrPatient.patient || 'Unknown'),
      doctor_name: apptOrPatient.doctor || apptOrPatient.doctor_name || '',
      department: apptOrPatient.department || ''
    };

    // if still no id, show modal with basic info and do not call API
    if (!pid) {
      historyData.value = [];
      showHistoryModal.value = true;
      return;
    }

    // fetch history (admin endpoint preferred, fallback to doctor)
    let res;
    try {
      res = await api(`/admin/patients/${pid}/history`);
    } catch (err) {
      res = await api(`/doctor/patient/${pid}/history`);
    }

    if (res?.patient) {
      historyPatient.value = {
        id: res.patient.id ?? pid,
        name: res.patient.name ?? historyPatient.value.name,
        doctor_name: res.patient.doctor_name ?? historyPatient.value.doctor_name,
        department: res.patient.department ?? historyPatient.value.department
      };
    }

    const arr = Array.isArray(res?.history) ? res.history : Array.isArray(res?.appointments) ? res.appointments : [];
    historyData.value = arr.map((h, idx) => ({
      id: h.id ?? idx + 1,
      visit_no: idx + 1,
      visit_type: h.visit_type || h.type || 'In-person',
      tests_done: h.tests_done || h.test_done || '',
      diagnosis: h.diagnosis || h.notes || '',
      prescription: h.prescription || '',
      medicines: h.medicines || h.medicines_text || []
    }));

    showHistoryModal.value = true;
  } catch (err) {
    showMessage('Could not load patient history: ' + (err?.message || err), true);
  }
}

// handler from PatientHistoryTable events
function onHistoryBack() {
  showHistoryModal.value = false;
}

function onHistoryView(row) {
  // admin clicked view on a specific visit row - navigate to detailed admin patient view if exists
  if (historyPatient.value.id) {
    router.push(`/admin/patients/${historyPatient.value.id}/history/${row.id}`);
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
    let res;

    if (searchType.value === 'doctor') {
      res = await api(`/search/doctors?q=${encodeURIComponent(searchQuery.value)}`);
      console.log("Doctor search res:", res);

      // backend returns a plain array
      searchResults.value = Array.isArray(res) ? res : (res.doctors || []);
    } 
    else {
      res = await api(`/admin/search/patients?q=${encodeURIComponent(searchQuery.value)}`);

      searchResults.value = Array.isArray(res) ? res : (res.patients || []);
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
        <div class="input-group" style="max-width: 500px;">
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
            <option value="department">Department</option>
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
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in searchResults" :key="item.id">
                <td>{{ item.name }}</td>
                <td>{{ item.email }}</td>
                <td v-if="searchType === 'doctor'">{{ item.specialization }}</td>
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
                  <button @click="viewAppointmentHistory(patient)" class="btn btn-sm btn-info me-1">
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
                  <button class="btn btn-sm btn-primary" @click="viewAppointmentHistory(appt)">View</button>
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

    <!-- Patient history modal -->
    <div v-if="showHistoryModal" class="modal-backdrop" style="position:fixed;inset:0;z-index:1050;display:flex;align-items:center;justify-content:center;padding:1rem;">
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
              @back="onHistoryBack"
            />
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showHistoryModal = false">Close</button>
            <button v-if="historyPatient.id" class="btn btn-primary" @click="router.push(`/admin/patients/${historyPatient.id}/history`)">Open full record</button>
          </div>
        </div>
      </div>
    </div>
    <!-- /.modal -->
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

/* simple modal backdrop styling */
.modal-backdrop .modal-content {
  max-height: 80vh;
  overflow: auto;
}
</style>
