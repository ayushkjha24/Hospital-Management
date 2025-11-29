<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { patientAPI } from "@/api/patient";

const router = useRouter();
const patientName = ref("");
const departments = ref([]);
const upcoming = ref([]);

async function load() {
  const res = await patientAPI.dashboard();
  patientName.value = res.patient_name || "Patient";
  departments.value = res.departments || [];
  upcoming.value = res.upcoming_appointments || [];
}

onMounted(load);

function goToDepartment(id) {
  router.push({ name: "DepartmentDetails", params: { deptId: id }});
}
function goToHistory() {
  router.push({ name: "PatientHistory" });
}
</script>

<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center">
      <h2>Welcome {{ patientName }}</h2>
      <div>
        <button class="btn btn-link" @click="goToHistory">History</button>
        <RouterLink to="/profile" class="btn btn-link">edit profile</RouterLink>
        <RouterLink to="/logout" class="btn btn-link">logout</RouterLink>
      </div>
    </div>

    <!-- Departments -->
    <section class="mt-4">
      <h4>Departments</h4>
      <div class="list-group">
        <div v-for="d in departments" :key="d.id" class="list-group-item d-flex justify-content-between align-items-center">
          <div>{{ d.name }}</div>
          <div>
            <button class="btn btn-sm btn-outline-primary me-2" @click="goToDepartment(d.id)">view details</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Upcoming Appointments -->
    <section class="mt-4">
      <h4>Upcoming Appointments</h4>
      <table class="table table-bordered">
        <thead>
          <tr><th>Sr No</th><th>Doctor</th><th>Deptt</th><th>Date</th><th>Time</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="(a,i) in upcoming" :key="a.id">
            <td>{{ i+1 }}</td>
            <td>{{ a.doctor }}</td>
            <td>{{ a.department }}</td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
            <td>
              <button class="btn btn-danger btn-sm" @click="patientAPI.cancelAppointment(a.id).then(load)">cancel</button>
            </td>
          </tr>
          <tr v-if="!upcoming.length"><td colspan="6" class="text-center">No upcoming appointments</td></tr>
        </tbody>
      </table>
    </section>
  </div>
</template>
