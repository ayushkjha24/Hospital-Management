<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/admin";

const patients = ref([]);

async function load() {
  patients.value = await api("/admin/patients");
}

async function del(id) {
  await api(`/admin/patients/${id}`, "DELETE");
  load();
}

async function blacklist(id) {
  await api(`/admin/patients/${id}/blacklist`, "POST");
  load();
}

onMounted(load);
</script>

<template>
  <div class="container py-4">
    <h3 class="mb-3">Registered Patients</h3>

    <table class="table table-bordered">
      <tbody>
        <tr v-for="p in patients" :key="p.id">
          <td>{{ p.name }}</td>
          <td class="text-end">
            <RouterLink :to="`/admin/patients/history/${p.id}`" class="btn btn-primary btn-sm me-2">history</RouterLink>
            <button @click="del(p.id)" class="btn btn-danger btn-sm me-2">delete</button>
            <button @click="blacklist(p.id)" class="btn btn-dark btn-sm">blacklist</button>
          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>
