<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiPublic } from '@/api/public';
import { api as patientApi } from '@/api/patient';

const route = useRoute();
const router = useRouter();
const apptId = route.params.id;

const appointment = ref(null);
const doctor = ref({});
const slots = ref([]);
const selectedSlot = ref(null);
const loading = ref(true);
const rescheduling = ref(false);
const message = ref('');
const messageClass = ref('alert-success');

async function loadAppointmentAndDoctor() {
  loading.value = true;
  try {
    // Get upcoming appointments to find current appointment
    const appts = await patientApi('/patient/appointments/upcoming');
    const currentAppt = (appts.appointments || []).find(a => a.id === parseInt(apptId));
    
    if (!currentAppt) {
      message.value = 'Appointment not found';
      messageClass.value = 'alert-danger';
      return;
    }

    appointment.value = currentAppt;

    // Extract doctor ID from appointment (you may need to adjust based on your response structure)
    // Assuming the appointment has doctor_id or we fetch doctor list
    const allAppts = await patientApi('/patient/appointments/upcoming');
    
    // We need to get doctor info - let's fetch all doctors and find the right one
    const doctorRes = await apiPublic('/doctors');
    const doctorsList = doctorRes.doctors || [];
    
    // Match doctor by name from current appointment
    const matchedDoctor = doctorsList.find(d => d.name === currentAppt.doctor);
    
    if (!matchedDoctor) {
      message.value = 'Could not find doctor information';
      messageClass.value = 'alert-danger';
      return;
    }

    doctor.value = {
      id: matchedDoctor.id,
      name: matchedDoctor.name,
      specialization: matchedDoctor.specialization,
      experience_years: matchedDoctor.experience_years,
      department: matchedDoctor.department
    };

    // Load 7-day availability for this doctor
    const doctorDetail = await apiPublic(`/doctors/${matchedDoctor.id}`);
    slots.value = (doctorDetail.availability || []).map(s => ({
      id: s.id,
      date: s.date,
      start_time: s.start_time,
      end_time: s.end_time,
      is_available: !!s.is_available
    }));

  } catch (err) {
    message.value = err.message || 'Could not load appointment details';
    messageClass.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
}

function selectSlot(slot) {
  if (!slot.is_available) return;
  selectedSlot.value = slot;
}

async function reschedule() {
  if (!selectedSlot.value) {
    message.value = 'Please select an available slot';
    messageClass.value = 'alert-warning';
    return;
  }

  // Prevent rescheduling to the same time
  if (
    selectedSlot.value.date === appointment.value.date &&
    selectedSlot.value.start_time === appointment.value.time
  ) {
    message.value = 'Please select a different time slot';
    messageClass.value = 'alert-warning';
    return;
  }

  rescheduling.value = true;
  try {
    await patientApi(`/patient/appointment/${apptId}/reschedule`, 'POST', {
      date: selectedSlot.value.date,
      start_time: selectedSlot.value.start_time
    });
    message.value = 'Appointment rescheduled successfully';
    messageClass.value = 'alert-success';
    setTimeout(() => router.push('/patient/appointments'), 1200);
  } catch (err) {
    message.value = err.message || 'Rescheduling failed';
    messageClass.value = 'alert-danger';
  } finally {
    rescheduling.value = false;
  }
}

function cancel() {
  router.back();
}

onMounted(loadAppointmentAndDoctor);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">Reschedule Appointment</h3>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="row">
      <!-- Current Appointment Info -->
      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-header bg-light">
            <h6 class="mb-0">Current Appointment</h6>
          </div>
          <div class="card-body">
            <p class="mb-2">
              <strong>Doctor:</strong> {{ appointment?.doctor }}
            </p>
            <p class="mb-2">
              <strong>Specialization:</strong> {{ appointment?.specialization }}
            </p>
            <p class="mb-2">
              <strong>Date:</strong> {{ appointment?.date }}
            </p>
            <p class="mb-2">
              <strong>Time:</strong> {{ appointment?.time }}
            </p>
            <p class="mb-0">
              <strong>Status:</strong>
              <span class="badge bg-warning">{{ appointment?.status }}</span>
            </p>
          </div>
        </div>

        <div class="card">
          <div class="card-header bg-light">
            <h6 class="mb-0">Doctor Info</h6>
          </div>
          <div class="card-body">
            <p class="mb-2">
              <strong>Name:</strong> {{ doctor.name }}
            </p>
            <p class="mb-2">
              <strong>Specialization:</strong> {{ doctor.specialization }}
            </p>
            <p class="mb-2">
              <strong>Department:</strong> {{ doctor.department }}
            </p>
            <p class="mb-0">
              <strong>Experience:</strong> {{ doctor.experience_years }} years
            </p>
          </div>
        </div>
      </div>

      <!-- Available Slots -->
      <div class="col-md-8">
        <div class="card">
          <div class="card-header bg-light">
            <h6 class="mb-0">Select New Slot (Next 7 Days)</h6>
          </div>
          <div class="card-body">
            <div v-if="slots.length === 0" class="alert alert-info">
              No availability published for the next 7 days
            </div>

            <div v-else>
              <!-- Organize slots by date -->
              <div class="row">
                <div
                  v-for="slot in slots"
                  :key="slot.id"
                  class="col-md-6 col-lg-4 mb-3"
                >
                  <div
                    class="p-3 border rounded text-center"
                    :class="[
                      slot.is_available
                        ? selectedSlot && selectedSlot.id === slot.id
                          ? 'bg-success text-white'
                          : 'bg-light border-success cursor-pointer'
                        : 'bg-secondary text-white opacity-50',
                    ]"
                    @click="selectSlot(slot)"
                    style="cursor: pointer; transition: all 0.2s;"
                  >
                    <div class="fw-bold mb-1">{{ slot.date }}</div>
                    <div class="small">{{ slot.start_time }} - {{ slot.end_time }}</div>
                    <div class="small mt-2">
                      {{
                        slot.is_available ? '✓ Available' : '✗ Booked'
                      }}
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="selectedSlot" class="mt-4 p-3 bg-light rounded">
                <p class="mb-2">
                  <strong>Selected Slot:</strong>
                </p>
                <p class="mb-0">
                  {{ selectedSlot.date }} at {{ selectedSlot.start_time }}
                </p>
              </div>
            </div>
          </div>

          <div class="card-footer bg-light d-flex gap-2">
            <button
              @click="reschedule"
              :disabled="rescheduling || !selectedSlot"
              class="btn btn-success"
            >
              {{
                rescheduling ? 'Rescheduling...' : 'Confirm Reschedule'
              }}
            </button>
            <button @click="cancel" class="btn btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: none;
}

.card-header {
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
}

.opacity-50 {
  opacity: 0.5;
}
</style>