<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/doctor";

const days = ref([]);
const slots = ref([]);

onMounted(async () => {
  const res = await api("/doctor/availability");
  days.value = res;
});

async function save() {
  const formatted = slots.value.map(s => ({
    date: s.date,
    start_time: s.start,
    end_time: s.end
  }));

  await api("/doctor/availability/publish", {
    method: "POST",
    body: { slots: formatted }
  });
}
</script>

<template>
  <div class="container py-4">

    <h3>Doctor's Availability</h3>

    <table class="table table-bordered mt-3">
      <thead>
        <tr>
          <th>Date</th>
          <th>Start</th>
          <th>End</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="d in days" :key="d.date">
          <td>{{ d.date }}</td>
          <td><input class="form-control" v-model="d.slots[0]?.start_time" /></td>
          <td><input class="form-control" v-model="d.slots[0]?.end_time" /></td>
        </tr>
      </tbody>
    </table>

    <button class="btn btn-success mt-3" @click="save">save</button>
  </div>
</template>