<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/admin';
import { useRouter } from 'vue-router';

const router = useRouter();
const doctors = ref([]);
const loading = ref(true);
const message = ref('');
const messageClass = ref('alert-success');

async function loadDoctors() {
  try {
    const res = await api('/admin/doctors');
    doctors.value = res.doctors || [];
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    loading.value = false;
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

function showMessage(msg, isError = false) {
  message.value = msg;
  messageClass.value = isError ? 'alert-danger' : 'alert-success';
  setTimeout(() => (message.value = ''), 4000);
}

onMounted(loadDoctors);
</script>

<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-bold">Manage Doctors</h3>
      <RouterLink to="/admin/doctors/add" class="btn btn-success">
        + Add Doctor
      </RouterLink>
    </div>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <table v-else class="table table-bordered table-hover">
      <thead class="table-primary">
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Specialization</th>
          <th>Experience</th>
          <th>Department</th>
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
          <td>{{ doctor.department || 'N/A' }}</td>
          <td>
            <span v-if="doctor.is_approved" class="badge bg-success">Approved</span>
            <span v-else class="badge bg-warning">Pending</span>
          </td>
          <td>
            <RouterLink :to="`/admin/doctors/edit/${doctor.id}`" class="btn btn-sm btn-warning me-1">
              Edit
            </RouterLink>
            <button @click="deleteDoctor(doctor.id)" class="btn btn-sm btn-danger me-1">
              Delete
            </button>
            <button @click="blacklistDoctor(doctor.id)" class="btn btn-sm btn-dark">
              Blacklist
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && doctors.length === 0" class="alert alert-info">
      No doctors found
    </div>
  </div>
</template>
