<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiPublic } from '@/api/public';
import { api as patientApi } from '@/api/patient';

const route = useRoute();
const router = useRouter();
const doctorId = route.params.id;

const doctor = ref({});
const slots = ref([]); // array of availability slots
const selectedSlot = ref(null);
const loading = ref(true);
const booking = ref(false);
const message = ref('');
const messageClass = ref('alert-success');

async function loadDoctor() {
  loading.value = true;
  try {
    const res = await apiPublic(`/doctors/${doctorId}`);
    doctor.value = {
      name: res.name,
      specialization: res.specialization,
      experience_years: res.experience_years,
      department: res.department
    };
    // normalize slots: ensure date format YYYY-MM-DD and times HH:MM
    slots.value = (res.availability || []).map(s => ({
      id: s.id,
      date: s.date,
      start_time: s.start_time,
      end_time: s.end_time,
      is_available: !!s.is_available
    }));
  } catch (err) {
    message.value = err.message || 'Could not load doctor';
    messageClass.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
}

function selectSlot(slot) {
  if (!slot.is_available) return;
  selectedSlot.value = slot;
}

async function book() {
  if (!selectedSlot.value) {
    message.value = 'Please select an available slot';
    messageClass.value = 'alert-warning';
    return;
  }

  booking.value = true;
  try {
    await patientApi('/patient/book-appointment', 'POST', {
      doctor_id: Number(doctorId),
      date: selectedSlot.value.date,
      start_time: selectedSlot.value.start_time
    });
    message.value = 'Appointment booked successfully';
    messageClass.value = 'alert-success';
    setTimeout(() => router.push('/patient/appointments'), 1200);
  } catch (err) {
    message.value = err.message || 'Booking failed';
    messageClass.value = 'alert-danger';
  } finally {
    booking.value = false;
  }
}

onMounted(loadDoctor);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-3">Book with Dr. {{ doctor.name }}</h3>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
    </div>

    <div v-else>
      <div class="card mb-3">
        <div class="card-body">
          <h5 class="card-title">{{ doctor.name }}</h5>
          <p class="text-muted">{{ doctor.specialization }} — {{ doctor.department }}</p>
          <p class="small">Experience: {{ doctor.experience_years || 'N/A' }} years</p>
        </div>
      </div>

      <div class="mb-3">
        <h5>Next 7 days availability</h5>
        <div v-if="slots.length === 0" class="alert alert-info">No availability published for the next 7 days</div>

        <div v-else class="d-flex flex-wrap gap-2">
          <div
            v-for="slot in slots"
            :key="slot.id"
            class="p-2 border rounded"
            :class="slot.is_available ? (selectedSlot && selectedSlot.id === slot.id ? 'bg-success text-white' : 'bg-light') : 'bg-secondary text-white'"
            style="min-width: 160px; cursor: pointer;"
            @click="selectSlot(slot)"
          >
            <div><strong>{{ slot.date }}</strong></div>
            <div>{{ slot.start_time }} - {{ slot.end_time }}</div>
            <div class="small mt-1">{{ slot.is_available ? 'Available' : 'Unavailable' }}</div>
          </div>
        </div>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-success" @click="book" :disabled="booking">
          {{ booking ? 'Booking...' : 'Book Selected Slot' }}
        </button>
        <RouterLink class="btn btn-secondary" to="/patient/departments">Back</RouterLink>
      </div>
    </div>
  </div>
</template>
