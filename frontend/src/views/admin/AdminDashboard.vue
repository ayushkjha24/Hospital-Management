<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/admin";

const doctors = ref([]);
const patients = ref([]);
const appointments = ref([]);

onMounted(async () => {
  doctors.value = await api("/admin/doctors");
  patients.value = await api("/admin/patients");
  appointments.value = await api("/admin/appointments/upcoming");
});
</script>

<template>
  <div class="container py-4">

    <h2 class="fw-bold mb-3">Welcome Admin</h2>

    <!-- Search Bar -->
    <div class="d-flex mb-4">
      <input class="form-control me-2" placeholder="doctor, patient, department..." />
      <button class="btn btn-primary">search</button>
      <RouterLink to="/admin/doctors/add" class="btn btn-success ms-3">create</RouterLink>
    </div>

    <!-- Registered Doctors -->
    <h4>Registered Doctors</h4>
    <table class="table table-bordered">
      <tbody>
        <tr v-for="d in doctors" :key="d.id">
          <td>{{ d.name }}</td>
          <td class="text-end">
            <RouterLink
              :to="`/admin/doctors/edit/${d.id}`"
              class="btn btn-warning btn-sm me-2"
            >
              edit
            </RouterLink>

            <RouterLink
              :to="`/admin/delete-doctor/${d.id}`"
              class="btn btn-danger btn-sm me-2"
            >
              delete
            </RouterLink>

            <RouterLink
              :to="`/admin/blacklist-doctor/${d.id}`"
              class="btn btn-dark btn-sm"
            >
              blacklist
            </RouterLink>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Registered Patients -->
    <h4>Registered Patients</h4>
    <table class="table table-bordered">
      <tbody>
        <tr v-for="p in patients" :key="p.id">
          <td>{{ p.name }}</td>
          <td class="text-end">

            <RouterLink
              :to="`/admin/edit-patient/${p.id}`"
              class="btn btn-warning btn-sm me-2"
            >
              edit
            </RouterLink>

            <RouterLink
              :to="`/admin/delete-patient/${p.id}`"
              class="btn btn-danger btn-sm me-2"
            >
              delete
            </RouterLink>

            <RouterLink
              :to="`/admin/blacklist-patient/${p.id}`"
              class="btn btn-dark btn-sm"
            >
              blacklist
            </RouterLink>

          </td>
        </tr>
      </tbody>
    </table>

    <!-- Upcoming Appointments -->
    <h4>Upcoming Appointments</h4>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>Sr No</th>
          <th>Patient Name</th>
          <th>Doctor Name</th>
          <th>Department</th>
          <th>Patient History</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(a, i) in appointments" :key="a.id">
          <td>{{ i + 1 }}</td>
          <td>{{ a.patient }}</td>
          <td>{{ a.doctor }}</td>
          <td>{{ a.department }}</td>
          <td>
            <!-- Must pass PATIENT ID, not appointment ID -->
            <RouterLink
              :to="`/admin/patient-history/${a.patient_id}`"
              class="btn btn-primary btn-sm"
            >
              view
            </RouterLink>
          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>
