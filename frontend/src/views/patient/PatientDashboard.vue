<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getDashboard, cancelAppointment } from "@/api/patient";

const router = useRouter();
const patientName = ref("");
const departments = ref([]);
const upcoming = ref([]);
const stats = ref({ upcoming_appointments: 0, total_departments: 0 });
const loading = ref(true);
const message = ref("");
const messageClass = ref("alert-info");

async function loadDashboard() {
  try {
    const res = await getDashboard();
    patientName.value = res.patient_name || "Patient";
    departments.value = res.departments || [];
    upcoming.value = res.upcoming_appointments || [];
    stats.value = res.stats || { upcoming_appointments: 0, total_departments: 0 };
  } catch (err) {
    message.value = err.message;
    messageClass.value = "alert-danger";
  } finally {
    loading.value = false;
  }
}

async function handleCancelAppointment(appointmentId) {
  if (!confirm("Are you sure you want to cancel this appointment?")) return;
  
  try {
    await cancelAppointment(appointmentId);
    message.value = "Appointment cancelled successfully";
    messageClass.value = "alert-success";
    loadDashboard();
  } catch (err) {
    message.value = err.message;
    messageClass.value = "alert-danger";
  }
}

onMounted(() => {
  loadDashboard();
});

function goToDepartment(id) {
  router.push(`/patient/departments`);
}

function goToHistory() {
  router.push("/patient/appointments");
}
</script>

<template>
  <div class="container py-4">
    <!-- <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold">Welcome, {{ patientName }}</h2>
      <div class="btn-group">
        <RouterLink to="/patient/appointments" class="btn btn-sm btn-outline-secondary">
          History
        </RouterLink>
        <RouterLink to="/patient/profile" class="btn btn-sm btn-outline-secondary">
          Edit Profile
        </RouterLink>
      </div>
    </div> -->

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <!-- Stats Cards -->
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
          <div class="card bg-success text-white">
            <div class="card-body">
              <h6 class="card-title">Available Departments</h6>
              <h3 class="card-text">{{ stats.total_departments }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- Departments Section -->
      <section class="mb-4">
        <h4 class="fw-bold mb-3">Departments</h4>
        <div class="row">
          <div v-for="dept in departments" :key="dept.id" class="col-md-6 mb-3">
            <div class="card">
              <div class="card-body">
                <h5 class="card-title">{{ dept.name }}</h5>
                <p v-if="dept.description" class="card-text text-muted small">{{ dept.description }}</p>
                <RouterLink :to="`/patient/departments`" class="btn btn-sm btn-outline-primary">
                  View Doctors
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
        <div v-if="departments.length === 0" class="alert alert-info">
          No departments available
        </div>
      </section>

      <!-- Upcoming Appointments Section -->
      <section class="mb-4">
        <h4 class="fw-bold mb-3">Upcoming Appointments</h4>
        <div class="table-responsive">
          <table class="table table-hover table-bordered">
            <thead class="table-light">
              <tr>
                <th>#</th>
                <th>Doctor</th>
                <th>Department</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(appt, i) in upcoming" :key="appt.id">
                <td>{{ i + 1 }}</td>
                <td>{{ appt.doctor }}</td>
                <td>{{ appt.department }}</td>
                <td>{{ appt.date }}</td>
                <td>{{ appt.time }}</td>
                <td>
                  <span class="badge bg-warning">{{ appt.status }}</span>
                </td>
                <td>
                  <button 
                    class="btn btn-sm btn-danger" 
                    @click="handleCancelAppointment(appt.id)"
                  >
                    Cancel
                  </button>
                </td>
              </tr>
              <tr v-if="upcoming.length === 0">
                <td colspan="7" class="text-center text-muted">No upcoming appointments</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Quick Actions -->
      <div class="d-flex gap-2">
        <RouterLink to="/patient/departments" class="btn btn-primary">
          <i class="bi bi-search"></i> Browse Doctors
        </RouterLink>
        <RouterLink to="/patient/appointments" class="btn btn-info">
          <i class="bi bi-calendar-check"></i> All Appointments
        </RouterLink>
        <RouterLink to="/patient/profile" class="btn btn-warning">
          <i class="bi bi-person"></i> Edit Profile
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
