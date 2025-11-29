<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/admin";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const patientName = ref("");
const doctorName = ref("");
const history = ref([]);

onMounted(async () => {
  const res = await api(`/admin/patients/${route.params.id}/history`);
  patientName.value = res.patient;
  doctorName.value = res.doctor;
  history.value = res.history;
});
</script>

<template>
  <div class="container py-4">

    <button class="btn btn-secondary mb-3" @click="router.back()">back</button>

    <h4>Patient Name: {{ patientName }}</h4>
    <h4>Doctor's Name: {{ doctorName }}</h4>

    <table class="table table-bordered mt-3">
      <thead>
        <tr>
          <th>Visit No.</th>
          <th>Visit Type</th>
          <th>Tests Done</th>
          <th>Diagnosis</th>
          <th>Prescription</th>
          <th>Medicines</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(h,i) in history" :key="i">
          <td>{{ i+1 }}</td>
          <td>{{ h.type }}</td>
          <td>{{ h.tests_done }}</td>
          <td>{{ h.diagnosis }}</td>
          <td>{{ h.prescription }}</td>
          <td>{{ h.medicines }}</td>
        </tr>
      </tbody>
    </table>

  </div>
</template>