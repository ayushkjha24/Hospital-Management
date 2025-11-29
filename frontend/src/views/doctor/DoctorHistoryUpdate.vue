<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/api/doctor";

const route = useRoute();
const router = useRouter();
const appointmentId = route.params.appointmentId;

const form = ref({
  diagnosis: "",
  prescription: "",
  notes: "",
  next_visit: null
});

async function save() {
  await api(`/doctor/patient/${route.params.patientId}/add-history`, {
    method: "POST",
    body: {
      appointment_id: Number(appointmentId),
      diagnosis: form.value.diagnosis,
      prescription: form.value.prescription,
      notes: form.value.notes,
      next_visit: form.value.next_visit
    }
  });

  router.push("/doctor/dashboard");
}
</script>

<template>
  <div class="container py-4">

    <h3>Update Patient History</h3>

    <div class="card p-4 mt-3">

      <label>Diagnosis</label>
      <input class="form-control" v-model="form.diagnosis" />

      <label class="mt-3">Prescription</label>
      <input class="form-control" v-model="form.prescription" />

      <label class="mt-3">Notes</label>
      <textarea class="form-control" v-model="form.notes"></textarea>

      <label class="mt-3">Next Visit (optional)</label>
      <input type="datetime-local" v-model="form.next_visit" class="form-control" />

      <button class="btn btn-success mt-3" @click="save">save</button>

    </div>
  </div>
</template>
