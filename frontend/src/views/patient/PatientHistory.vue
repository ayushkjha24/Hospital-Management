<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/patient';
import { useRouter } from 'vue-router';

const router = useRouter();
const appointments = ref([]);
const loading = ref(true);
const message = ref('');
const messageClass = ref('alert-success');
const filterStatus = ref('all'); // all, upcoming, past, completed, cancelled

async function loadAppointments() {
  loading.value = true;
  try {
    // Load all appointments
    const res = await api('/patient/appointments');
    let allAppts = (res && res.appointments) ? res.appointments : [];
    
    // Filter by status if needed
    if (filterStatus.value !== 'all') {
      allAppts = allAppts.filter(a => a.status === filterStatus.value);
    }
    
    appointments.value = allAppts;
    console.log('All appointments response', res);
  } catch (err) {
    message.value = err.message;
    messageClass.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
}

async function rescheduleAppointment(apptId) {
  router.push(`/patient/appointment/${apptId}/reschedule`);
}

async function cancelAppointment(apptId) {
  if (!confirm('Are you sure you want to cancel this appointment?')) return;
  try {
    await api(`/patient/appointment/${apptId}/cancel`, 'POST');
    message.value = 'Appointment cancelled successfully';
    messageClass.value = 'alert-success';
    await loadAppointments();
  } catch (err) {
    message.value = err.message;
    messageClass.value = 'alert-danger';
  }
}

function canReschedule(appt) {
  // Only allow rescheduling upcoming appointments
  return ['scheduled', 'confirmed'].includes(appt.status);
}

function canCancel(appt) {
  // Allow cancelling scheduled or confirmed appointments
  return ['scheduled', 'confirmed'].includes(appt.status);
}

onMounted(loadAppointments);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">My Appointments</h3>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <!-- Filter Tabs -->
    <div class="mb-3 d-flex gap-2">
      <button
        @click="filterStatus = 'all'; loadAppointments()"
        :class="['btn', 'btn-sm', filterStatus === 'all' ? 'btn-primary' : 'btn-outline-primary']"
      >
        All
      </button>
      <button
        @click="filterStatus = 'scheduled'; loadAppointments()"
        :class="['btn', 'btn-sm', filterStatus === 'scheduled' ? 'btn-primary' : 'btn-outline-primary']"
      >
        Scheduled
      </button>
      <button
        @click="filterStatus = 'confirmed'; loadAppointments()"
        :class="['btn', 'btn-sm', filterStatus === 'confirmed' ? 'btn-primary' : 'btn-outline-primary']"
      >
        Confirmed
      </button>
      <button
        @click="filterStatus = 'completed'; loadAppointments()"
        :class="['btn', 'btn-sm', filterStatus === 'completed' ? 'btn-primary' : 'btn-outline-primary']"
      >
        Completed
      </button>
      <button
        @click="filterStatus = 'cancelled'; loadAppointments()"
        :class="['btn', 'btn-sm', filterStatus === 'cancelled' ? 'btn-primary' : 'btn-outline-primary']"
      >
        Cancelled
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <table v-if="appointments.length > 0" class="table table-bordered table-hover">
        <thead class="table-primary">
          <tr>
            <th>#</th>
            <th>Doctor</th>
            <th>Specialization</th>
            <th>Date & Time</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(appt, i) in appointments" :key="appt.id">
            <td>{{ i + 1 }}</td>
            <td>{{ appt.doctor }}</td>
            <td>{{ appt.specialization }}</td>
            <td>{{ appt.appointment_time }}</td>
            <td>
              <span
                :class="[
                  'badge',
                  {
                    'bg-warning': appt.status === 'scheduled',
                    'bg-info': appt.status === 'confirmed',
                    'bg-success': appt.status === 'completed',
                    'bg-danger': appt.status === 'cancelled'
                  }
                ]"
              >
                {{ appt.status }}
              </span>
            </td>
            <td>
              <button
                v-if="canReschedule(appt)"
                @click="rescheduleAppointment(appt.id)"
                class="btn btn-sm btn-info me-1"
              >
                Reschedule
              </button>
              <button
                v-if="canCancel(appt)"
                @click="cancelAppointment(appt.id)"
                class="btn btn-sm btn-danger"
              >
                Cancel
              </button>
              <span v-if="!canReschedule(appt) && !canCancel(appt)" class="text-muted">
                No actions
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="alert alert-info">
        No appointments found.
        <RouterLink to="/patient/departments">Browse doctors to book an appointment</RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table-hover tbody tr:hover {
  background-color: #f8f9fa;
}

.btn-sm {
  font-size: 0.85rem;
  padding: 0.4rem 0.6rem;
}
</style>
