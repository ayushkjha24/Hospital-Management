<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/patient";
import { useRouter } from "vue-router";

const router = useRouter();
const form = ref({
  name: "",
  email: "",
  phone: "",
  medical_history: ""
});

onMounted(async () => {
  const res = await api("/patient/profile");
  form.value = res;
});

async function save() {
  await api("/patient/profile", "PUT", form.value);
  alert("Profile updated");
  router.push("/");
}
</script>

<template>
  <div class="container py-4">
    <h3>Edit Profile</h3>
    <div class="card p-4">
      <div class="mb-3">
        <label>Name</label>
        <input class="form-control" v-model="form.name" />
      </div>
      <div class="mb-3">
        <label>Email</label>
        <input class="form-control" v-model="form.email" disabled />
      </div>
      <div class="mb-3">
        <label>Phone</label>
        <input class="form-control" v-model="form.phone" />
      </div>
      <div class="mb-3">
        <label>Medical History</label>
        <textarea class="form-control" v-model="form.medical_history"></textarea>
      </div>
      <button class="btn btn-success" @click="save">Save</button>
    </div>
  </div>
</template>