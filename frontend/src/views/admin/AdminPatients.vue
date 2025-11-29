<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/admin';
import { useRouter } from 'vue-router';

const router = useRouter();
const patients = ref([]);
const loading = ref(true);
const message = ref('');
const messageClass = ref('alert-success');
const showModal = ref(false);
const editingPatient = ref(null);
const formData = ref({
  name: '',
  email: '',
  phone: '',
  medical_history: ''
});

async function loadPatients() {
  try {
    const res = await api('/admin/patients');
    patients.value = res.patients || [];
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    loading.value = false;
  }
}

async function deletePatient(id) {
  if (!confirm('Are you sure you want to delete this patient? This action cannot be undone.')) return;
  try {
    await api(`/admin/patients/${id}`, 'DELETE');
    showMessage('Patient deleted successfully');
    loadPatients();
  } catch (err) {
    showMessage(err.message, true);
  }
}

async function blacklistPatient(id) {
  if (!confirm('Are you sure you want to blacklist this patient?')) return;
  try {
    await api(`/admin/patients/${id}/blacklist`, 'POST');
    showMessage('Patient blacklisted successfully');
    loadPatients();
  } catch (err) {
    showMessage(err.message, true);
  }
}

async function editPatient(patient) {
  editingPatient.value = patient.id;
  formData.value = {
    name: patient.name,
    email: patient.email,
    phone: patient.phone || '',
    medical_history: patient.medical_history || ''
  };
  showModal.value = true;
}

async function savePatient() {
  try {
    await api(`/admin/patients/${editingPatient.value}`, 'PUT', formData.value);
    showMessage('Patient updated successfully');
    showModal.value = false;
    loadPatients();
  } catch (err) {
    showMessage(err.message, true);
  }
}

function showMessage(msg, isError = false) {
  message.value = msg;
  messageClass.value = isError ? 'alert-danger' : 'alert-success';
  setTimeout(() => (message.value = ''), 4000);
}

onMounted(loadPatients);
</script>

<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-bold">Manage Patients</h3>
    </div>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <div class="table-responsive">
        <table class="table table-bordered table-hover">
          <thead class="table-primary">
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
                <button @click="editPatient(patient)" class="btn btn-sm btn-warning me-1">
                  Edit
                </button>
                <button @click="deletePatient(patient.id)" class="btn btn-sm btn-danger me-1">
                  Delete
                </button>
                <button @click="blacklistPatient(patient.id)" class="btn btn-sm btn-dark">
                  Blacklist
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="patients.length === 0" class="alert alert-info">
        No patients found
      </div>
    </div>
  </div>

  <!-- Edit Modal -->
  <div v-if="showModal" class="modal d-block" style="background: rgba(0, 0, 0, 0.5);">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Patient</h5>
          <button @click="showModal = false" type="button" class="btn-close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Name</label>
            <input v-model="formData.name" type="text" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="formData.email" type="email" class="form-control" disabled />
          </div>
          <div class="mb-3">
            <label class="form-label">Phone</label>
            <input v-model="formData.phone" type="tel" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Medical History</label>
            <textarea v-model="formData.medical_history" class="form-control" rows="4"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showModal = false" type="button" class="btn btn-secondary">
            Close
          </button>
          <button @click="savePatient" type="button" class="btn btn-primary">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}

.modal-dialog {
  width: 500px;
  max-width: 100%;
}
</style>
