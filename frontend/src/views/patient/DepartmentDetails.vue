<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { patientAPI } from "@/api/patient";

const route = useRoute();
const router = useRouter();
const deptId = route.params.deptId;
const dept = ref({ name: "", description: "", doctors: [] });

onMounted(async () => {
  const res = await patientAPI.departmentDetails(deptId);
  dept.value = res;
});

function viewDoctor(doctorId) {
  router.push({ name: "DoctorDetails", params: { doctorId }});
}

</script>

<template>
  <div class="container py-4">
    <button class="btn btn-link mb-2" @click="$router.back()">← Back</button>
    <h3>Department of {{ dept.name }}</h3>
    <p>{{ dept.description }}</p>

    <h5 class="mt-4">Doctors' list</h5>
    <div class="list-group">
      <div v-for="doc in dept.doctors" :key="doc.id" class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <div class="fw-bold">{{ doc.name }}</div>
          <small>{{ doc.specialization }} • {{ doc.experience_years }} yrs</small>
        </div>
        <div>
          <button class="btn btn-sm btn-outline-primary me-2" @click="viewDoctor(doc.id)">view details</button>
          <button class="btn btn-sm btn-outline-success" @click="router.push({ name:'DoctorAvailability', params:{ doctorId: doc.id }})">check availability</button>
        </div>
      </div>
    </div>
  </div>
</template>
