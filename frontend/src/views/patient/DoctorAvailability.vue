<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { patientAPI } from "@/api/patient";

const route = useRoute();
const doctorId = route.params.doctorId;
const days = ref([]); // [{ date, start, end }]
const selected = ref({ date: null, start: null, end: null });

onMounted(async () => {
  const res = await patientAPI.availability(doctorId);
  // res is an array of slots (date,start,end). Group by date for UI
  const grouped = {};
  res.forEach(s => {
    grouped[s.date] = grouped[s.date] || [];
    grouped[s.date].push(s);
  });
  days.value = Object.keys(grouped).map(d => ({ date: d, slots: grouped[d] }));
});

function pickSlot(slot) {
  selected.value = { date: slot.date, start: slot.start, end: slot.end };
}

async function book() {
  if (!selected.value.date) return alert("Select a slot first");
  await patientAPI.bookAppointment({
    doctor_id: Number(doctorId),
    date: selected.value.date,
    start_time: selected.value.start
  });
  alert("Booked — check Upcoming Appointments");
}
</script>

<template>
  <div class="container py-4">
    <button class="btn btn-link mb-2" @click="$router.back()">← Back</button>
    <h3>Doctor's Availability</h3>

    <div class="row g-3 mt-3">
      <div v-for="d in days" :key="d.date" class="col-12">
        <div class="d-flex align-items-center">
          <div style="width:160px" class="me-3 btn btn-light">{{ d.date }}</div>
          <div class="d-flex gap-2">
            <button
              v-for="s in d.slots"
              :key="s.start + s.end"
              :class="['btn', selected.date===d.date && selected.start===s.start ? 'btn-success' : 'btn-outline-success']"
              @click="pickSlot({date:d.date, start:s.start, end:s.end})"
            >
              {{ s.start }} - {{ s.end }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-4">
      <button class="btn btn-primary" @click="book">book</button>
    </div>
  </div>
</template>
