<script setup>
import { ref, onMounted } from "vue";
import { patientAPI } from "@/api/patient";

const history = ref([]);
const patientName = ref("");

onMounted(async () => {
  const res = await patientAPI.history();
  // API returns array; if you return patient name elsewhere adapt here
  history.value = res;
});

async function exportCSV() {
  const resp = await patientAPI.exportHistoryCSV();
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "patient_history.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
}
</script>

<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center">
      <h3>Patient History</h3>
      <div>
        <button class="btn btn-success me-2" @click="exportCSV">export as csv</button>
        <button class="btn btn-secondary" @click="$router.back()">back</button>
      </div>
    </div>

    <table class="table table-bordered mt-3">
      <thead>
        <tr><th>Visit Date</th><th>Doctor</th><th>Department</th><th>Diagnosis</th><th>Prescription</th><th>Notes</th></tr>
      </thead>
      <tbody>
        <tr v-for="(h,i) in history" :key="i">
          <td>{{ h.visit_date }}</td>
          <td>{{ h.doctor }}</td>
          <td>{{ h.department }}</td>
          <td>{{ h.diagnosis }}</td>
          <td>{{ h.prescription }}</td>
          <td>{{ h.notes }}</td>
        </tr>
        <tr v-if="!history.length"><td colspan="6" class="text-center">No history found</td></tr>
      </tbody>
    </table>
  </div>
</template>
