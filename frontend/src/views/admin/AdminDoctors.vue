<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/admin";

const doctors = ref([]);

async function load() {
  doctors.value = await api("/admin/doctors");
}

async function del(id) {
  await api(`/admin/doctors/${id}`, "DELETE");
  load();
}

async function blacklist(id) {
  await api(`/admin/doctors/${id}/blacklist`, "POST");
  load();
}

onMounted(load);
</script>

<template>
  <div class="container py-4">
    <h3 class="mb-3">Doctors</h3>

    <table class="table table-bordered">
      <tbody>
        <tr v-for="d in doctors" :key="d.id">
          <td>{{ d.name }}</td>
          <td>{{ d.specialization }}</td>
          <td class="text-end">
            <RouterLink :to="`/admin/doctors/edit/${d.id}`" class="btn btn-warning btn-sm me-2">edit</RouterLink>
            <button class="btn btn-danger btn-sm me-2" @click="del(d.id)">delete</button>
            <button class="btn btn-dark btn-sm" @click="blacklist(d.id)">blacklist</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
