<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/doctor";
import { useRouter } from "vue-router";

const router = useRouter();

const appointments = ref([]);
const patients = ref([]);

onMounted(async () => {
  appointments.value = await api("/doctor/appointments/upcoming");
  patients.value = await api("/doctor/assigned-patients");
});

// mark appointment complete or cancel
async function updateStatus(id, status) {
  await api(`/doctor/appointment/${id}/status`, {
    method: "PATCH",
    body: { status }
  });
  appointments.value = await api("/doctor/appointments/upcoming");
}
</script>

<template>
  <div class="container py-4">

    <h2 class="fw-bold mb-3">Welcome Doctor</h2>

    <!-- Upcoming Appointments -->
    <h4>Upcoming Appointments</h4>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>Sr No</th>
          <th>Patient Name</th>
          <th>History</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(a, i) in appointments" :key="a.id">
          <td>{{ i + 1 }}</td>
          <td>{{ a.patient_name }}</td>
          <td>
            <button
              class="btn btn-primary btn-sm"
              @click="router.push(`/doctor/history/update/${a.id}`)"
            >
              update
            </button>
          </td>

          <td>
            <button class="btn btn-success btn-sm me-2"
              @click="updateStatus(a.id,'completed')">
              mark as complete
            </button>

            <button class="btn btn-danger btn-sm"
              @click="updateStatus(a.id,'cancelled')">
              cancel
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Assigned Patients -->
    <h4>Assigned Patients</h4>
    <table class="table table-bordered">
      <tbody>
        <tr v-for="p in patients" :key="p.id">
          <td>{{ p.name }}</td>
          <td class="text-end">
            <button
              class="btn btn-primary btn-sm"
              @click="router.push(`/doctor/history/${p.id}`)"
            >
              view
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="mt-3">
      <button
        class="btn btn-success"
        @click="router.push('/doctor/availability')"
      >
        Provide Availability
      </button>
    </div>

  </div>
</template>