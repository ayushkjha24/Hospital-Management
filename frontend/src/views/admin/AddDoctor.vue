<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/admin";
import { useRouter } from "vue-router";
import { useMessagesStore } from '@/stores/messages';

const message_store = useMessagesStore();

const name = ref("");
const email = ref("");
const password = ref("");
const experience_years = ref("");
const department_id = ref("");

const departments = ref([]); // <-- store dropdown items
const router = useRouter();

async function loadDepartments() {
  // If you already have an endpoint /admin/departments, use that.
  const res = await api("/admin/departments");
  departments.value = res || [];
}

onMounted(loadDepartments);

async function submit() {
  const selected = departments.value.find(d => d.id == department_id.value);

  const res = await api("/admin/add-doctor", "POST", {
    name: name.value,
    email: email.value,
    password: password.value,
    specialization: selected ? selected.name : "", 
    experience_years: Number(experience_years.value),
    department_id: Number(department_id.value)
  });

  message_store.addMessage("Doctor added successfully!");
  router.push("/admin/dashboard");
}

</script>


<template>
  <div class="container py-4">
    <h3 class="mb-3">Add a new Doctor</h3>

    <div class="card p-4">

      <input class="form-control mb-3" placeholder="Fullname" v-model="name" />

      <!-- Department Dropdown -->
      <select class="form-control mb-3" v-model="department_id">
        <option value="">Select Department</option>

        <option 
          v-for="d in departments" 
          :key="d.id" 
          :value="d.id"
        >
          {{ d.name }}
        </option>
      </select>

      <input class="form-control mb-3" placeholder="Experience (years)" type="number" v-model="experience_years" />

      <input class="form-control mb-3" placeholder="Email" v-model="email" />

      <input class="form-control mb-3" placeholder="Password" type="password" v-model="password" />

      <button class="btn btn-success" @click="submit">create</button>
    </div>
  </div>
</template>

