<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/api/doctor";

const route = useRoute();
const router = useRouter();
const history = ref([]);
const patientName = ref("");

onMounted(async () => {
  const res = await api(`/doctor/patient/${route.params.patientId}/history`);
  patientName.value = res.patient;
  history.value = res.history;
});
</script>

<template>
  <div class="container py-4">

    <div class="d-flex justify-content-between">
      <h3>Patient History: {{ patientName }}</h3>
      <button class="btn btn-secondary" @click="router.back()">back</button>
    </div>

    <table class="table mt-3 table-bordered">
      <thead>
        <tr>
          <th>#</th>
          <th>Diagnosis</th>
          <th>Prescription</th>
          <th>Notes</th>
          <th>Visit Date</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(h, i) in history" :key="i">
          <td>{{ i + 1 }}</td>
          <td>{{ h.diagnosis }}</td>
          <td>{{ h.prescription }}</td>
          <td>{{ h.notes }}</td>
          <td>{{ h.visit_date }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
