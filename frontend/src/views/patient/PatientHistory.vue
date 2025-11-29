<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/patient';
import { useRouter } from 'vue-router';

const router = useRouter();
const appointments = ref([]);
const loading = ref(true);
const message = ref('');

async function loadAppointments() {
  try {
    const res = await api('/patient/appointments/past'); // API returns { appointments: [...] }
    appointments.value = (res && res.appointments) ? res.appointments : [];
    console.log('past appointments response', res);
  } catch (err) {
    message.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function rescheduleAppointment(apptId) {
  // route matches backend: /patient/appointment/<id>/reschedule
  router.push(`/patient/appointment/${apptId}/reschedule`);
}

async function cancelAppointment(apptId) {
  if (!confirm('Are you sure you want to cancel this appointment?')) return;
  try {
    // use patient cancel endpoint
    await api(`/patient/appointment/${apptId}/cancel`, 'POST');
    message.value = 'Appointment cancelled';
    await loadAppointments();
  } catch (err) {
    message.value = err.message;
  }
}

onMounted(loadAppointments);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">My Appointments</h3>

    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <table v-if="appointments.length > 0" class="table table-bordered">
        <thead class="table-primary">
          <tr>
            <th>Doctor</th>
            <th>Specialization</th>
            <th>Date & Time</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="appt in appointments" :key="appt.id">
            <td>{{ appt.doctor }}</td>
            <td>{{ appt.specialization }}</td>
            <td>{{ appt.appointment_time }}</td>
            <td>
              <span class="badge bg-warning">{{ appt.status }}</span>
            </td>
            <td>
              <button
                @click="rescheduleAppointment(appt.id)"
                class="btn btn-sm btn-info me-1"
              >
                Reschedule
              </button>
              <button
                @click="cancelAppointment(appt.id)"
                class="btn btn-sm btn-danger"
              >
                Cancel
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="alert alert-info">
        No appointments found. <RouterLink to="/patient/departments">Browse doctors</RouterLink>
      </div>
    </div>
  </div>
</template>
