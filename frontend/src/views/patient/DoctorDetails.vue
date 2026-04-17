<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import * as patientAPI from "@/api/patient";

const route = useRoute();
const router = useRouter();
const doctorId = route.params.doctorId;
const doc = ref({ name: "", specialization: "", experience_years: 0, department: null });

onMounted(async () => {
  doc.value = await patientAPI.doctorDetails(doctorId);
});

function checkAvailability() {
  router.push({ name: "DoctorAvailability", params: { doctorId }});
}
</script>

<template>
  <div class="container py-4">
    <button class="btn btn-link mb-2" @click="$router.back()">← Go Back</button>

    <div class="card p-4">
      <div class="d-flex">
        <div class="flex-grow-1">
          <h4 class="mb-0">{{ doc.name }}</h4>
          <div class="text-muted">{{ doc.specialization }}</div>
          <div class="mt-2">{{ doc.experience_years }} years experience</div>
          <div class="mt-2">Department: {{ doc.department }}</div>
        </div>
        <div class="ms-3">
          <div class="avatar-placeholder rounded-circle" style="width:80px;height:80px;background:#eee"></div>
        </div>
      </div>

      <div class="mt-4">
        <button class="btn btn-primary me-2" @click="checkAvailability">check availability</button>
        <button class="btn btn-secondary" @click="$router.back()">Go Back</button>
      </div>
    </div>
  </div>
</template>
