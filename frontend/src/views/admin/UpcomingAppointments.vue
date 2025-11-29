<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/admin";

const appts = ref([]);
const loading = ref(true);
const message = ref("");

async function loadAppointments() {
  try {
    const res = await api("/admin/appointments");
    // backend returns { appointments: [...] }
    appts.value = (res && res.appointments) ? res.appointments : [];
    console.log("Appointments loaded:", appts.value);
  } catch (err) {
    message.value = err.message || "Failed to load appointments";
  } finally {
    loading.value = false;
  }
}

onMounted(loadAppointments);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">Upcoming Appointments</h3>

    <div v-if="message" class="alert alert-danger">{{ message }}</div>

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
              <th>#</th>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Department</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(a, i) in appts" :key="a.id">
              <td>{{ i + 1 }}</td>
              <td>{{ a.patient }}</td>
              <td>{{ a.doctor }}</td>
              <td>{{ a.department }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td>
                <span class="badge bg-warning">{{ a.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="appts.length === 0" class="alert alert-info">
        No upcoming appointments
      </div>
    </div>
  </div>
</template>
