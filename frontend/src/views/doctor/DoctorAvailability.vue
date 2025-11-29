<template>
  <div class="container py-4">
    <h3 class="fw-bold">Provide Availability (next 7 days)</h3>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <form @submit.prevent="save" class="mt-3">
      <div v-for="(day, idx) in days" :key="day.date" class="card mb-2">
        <div class="card-body d-flex align-items-center">
          <div class="me-3" style="width:160px">
            <strong>{{ formatDate(day.date) }}</strong>
            <div class="text-muted small">{{ weekday(day.date) }}</div>
          </div>

          <!-- Morning slot -->
          <div class="me-4 d-flex align-items-center">
            <div class="form-check me-2">
              <input class="form-check-input" type="checkbox" v-model="day.morning.active" :id="`m-${idx}`" />
            </div>
            <label class="me-2" :for="`m-${idx}`">Morning</label>
            <input type="time" class="form-control form-control-sm me-2" v-model="day.morning.start_time" style="width:110px" />
            <span class="me-2">→</span>
            <input type="time" class="form-control form-control-sm" v-model="day.morning.end_time" style="width:110px" />
          </div>

          <!-- Evening slot -->
          <div class="me-4 d-flex align-items-center">
            <div class="form-check me-2">
              <input class="form-check-input" type="checkbox" v-model="day.evening.active" :id="`e-${idx}`" />
            </div>
            <label class="me-2" :for="`e-${idx}`">Evening</label>
            <input type="time" class="form-control form-control-sm me-2" v-model="day.evening.start_time" style="width:110px" />
            <span class="me-2">→</span>
            <input type="time" class="form-control form-control-sm" v-model="day.evening.end_time" style="width:110px" />
          </div>

          <div class="ms-auto">
            <button type="button" class="btn btn-outline-secondary btn-sm" @click="clearDay(idx)">Clear</button>
          </div>
        </div>
      </div>

      <div class="mt-3">
        <button class="btn btn-success" type="submit">Save Availability</button>
        <button type="button" class="btn btn-secondary ms-2" @click="load">Reload</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { api } from "@/api/doctor"; // uses your existing api helper

const days = ref([]);
const message = ref(null);
const messageClass = ref("alert-success");

// default times (wireframe): morning 08:00-12:00, evening 16:00-21:00
const DEFAULT_MORNING = { start: "08:00", end: "12:00" };
const DEFAULT_EVENING = { start: "16:00", end: "21:00" };

function makeDays() {
  days.value = [];
  const today = new Date();
  for (let i = 0; i < 7; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() + i);
    const iso = d.toISOString().slice(0, 10);
    days.value.push({
      date: iso,
      morning: { active: false, start_time: DEFAULT_MORNING.start, end_time: DEFAULT_MORNING.end },
      evening: { active: false, start_time: DEFAULT_EVENING.start, end_time: DEFAULT_EVENING.end }
    });
  }
}

function weekday(iso) {
  return new Date(iso).toLocaleDateString(undefined, { weekday: "short" });
}
function formatDate(iso) {
  return new Date(iso).toLocaleDateString();
}

async function load() {
  makeDays();
  message.value = null;
  try {
    // FIX: pass just "/availability" (not "/doctor/availability")
    // because @/api/doctor.js already prefixes "/doctor"
    const resp = await api("/availability");
    // sometimes api returns array or object - handle both
    const slots = Array.isArray(resp) ? resp : (resp.slots || resp);
    if (!slots) return;
    for (const s of slots) {
      const day = days.value.find(d => d.date === s.date);
      if (!day) continue;
      // assign to morning if start before 12:00 else evening
      if (s.start_time < "12:00") {
        day.morning.active = !!s.is_available;
        day.morning.start_time = s.start_time;
        day.morning.end_time = s.end_time;
      } else {
        day.evening.active = !!s.is_available;
        day.evening.start_time = s.start_time;
        day.evening.end_time = s.end_time;
      }
    }
  } catch (err) {
    message.value = "Failed to load availability";
    messageClass.value = "alert-danger";
  }
}

function clearDay(idx) {
  days.value[idx].morning = { active: false, start_time: DEFAULT_MORNING.start, end_time: DEFAULT_MORNING.end };
  days.value[idx].evening = { active: false, start_time: DEFAULT_EVENING.start, end_time: DEFAULT_EVENING.end };
}

function validateSlots(slots) {
  // local validation: times present and start < end
  for (const s of slots) {
    if (!s.start_time || !s.end_time) return `Missing time for ${s.date}`;
    if (s.start_time >= s.end_time) return `Start must be before end for ${s.date}`;
  }
  // simple intra-day overlap check (we only allow morning & evening so unlikely)
  return null;
}

async function save() {
  message.value = null;
  const slots = [];
  for (const d of days.value) {
    if (d.morning.active) slots.push({ date: d.date, start_time: d.morning.start_time, end_time: d.morning.end_time });
    if (d.evening.active) slots.push({ date: d.date, start_time: d.evening.start_time, end_time: d.evening.end_time });
  }
  const err = validateSlots(slots);
  if (err) {
    message.value = err;
    messageClass.value = "alert-danger";
    return;
  }

  try {
    // FIX: pass just "/availability" (not "/doctor/availability")
    // because @/api/doctor.js already prefixes "/doctor"
    await api("/availability", "POST", { slots });
    message.value = "Availability saved";
    messageClass.value = "alert-success";
  } catch (e) {
    message.value = (e && e.message) || "Failed to save availability";
    messageClass.value = "alert-danger";
  }
}

onMounted(load);
</script>

<style scoped>
.card { border-radius: 6px; }
</style>