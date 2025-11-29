<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/admin";

const appts = ref([]);

onMounted(async () => {
  appts.value = await api("/admin/appointments/upcoming");
});
</script>

<template>
  <div class="container py-4">
    <h3>Upcoming Appointments</h3>

    <table class="table table-bordered">
      <thead>
        <tr>
          <th>#</th>
          <th>Patient</th>
          <th>Doctor</th>
          <th>Department</th>
          <th>Time</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(a,i) in appts" :key="a.id">
          <td>{{ i + 1 }}</td>
          <td>{{ a.patient }}</td>
          <td>{{ a.doctor }}</td>
          <td>{{ a.department }}</td>
          <td>{{ a.time }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
