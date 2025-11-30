<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '@/api/doctor';

const route = useRoute();
const router = useRouter();
const patientId = route.params.patientId;
const appointmentId = route.params.appointmentId;

const patient = ref(null);
const appointment = ref(null);
const loading = ref(true);
const saving = ref(false);
const message = ref('');
const messageClass = ref('alert-success');

const form = ref({
  visit_type: 'consultation',
  tests_done: '',
  diagnosis: '',
  medicines: '',
  prescription: '',
  notes: '',
  next_visit: null
});

async function loadData() {
  loading.value = true;
  try {
    const res = await api(`/doctor/patient/${patientId}/history`);
    patient.value = res.patient;
    
    // Find current appointment
    const currentAppt = res.history.find(h => h.id === parseInt(appointmentId));
    if (currentAppt) {
      appointment.value = currentAppt;
    }
  } catch (err) {
    message.value = err.message;
    messageClass.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
}

async function saveHistory() {
  if (!form.value.diagnosis || !form.value.prescription) {
    message.value = 'Diagnosis and Prescription are required';
    messageClass.value = 'alert-warning';
    return;
  }

  saving.value = true;
  try {
  console.log(form.value);
    await api(`/doctor/patient/${patientId}/history`, 'POST', {
      appointment_id: parseInt(appointmentId),
      diagnosis: form.value.diagnosis,
      prescription: form.value.prescription,
      tests_done: form.value.tests_done,
      notes: form.value.notes,
      next_visit: form.value.next_visit
    });
    
    message.value = 'Patient history updated successfully';
    messageClass.value = 'alert-success';
    setTimeout(() => router.push('/doctor/dashboard'), 1500);
  } catch (err) {
    message.value = err.message;
    messageClass.value = 'alert-danger';
  } finally {
    saving.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">Update Patient History</h3>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <!-- Patient & Appointment Info -->
      <div class="row mb-4">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header bg-light">
              <h6 class="mb-0">Patient Information</h6>
            </div>
            <div class="card-body">
              <p class="mb-2"><strong>Name:</strong> {{ patient?.name }}</p>
              <p class="mb-2"><strong>Patient ID:</strong> {{ patient?.id }}</p>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card">
            <div class="card-header bg-light">
              <h6 class="mb-0">Appointment Information</h6>
            </div>
            <div class="card-body">
              <p class="mb-2"><strong>Date:</strong> {{ appointment?.date }}</p>
              <p class="mb-0"><strong>Status:</strong> <span class="badge bg-warning">{{ appointment?.status }}</span></p>
            </div>
          </div>
        </div>
      </div>

      <!-- Treatment History Form -->
      <div class="card">
        <div class="card-header bg-light">
          <h5 class="mb-0">Treatment Details</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Visit Type</label>
                <select v-model="form.visit_type" class="form-select">
                  <option value="consultation">Consultation</option>
                  <option value="follow-up">Follow-up</option>
                  <option value="routine-checkup">Routine Checkup</option>
                  <option value="emergency">Emergency</option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label">Tests Done</label>
                <input
                  v-model="form.tests_done"
                  type="text"
                  class="form-control"
                  placeholder="e.g., ECG, Blood Test, X-Ray"
                />
              </div>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label">
              Diagnosis <span class="text-danger">*</span>
            </label>
            <textarea
              v-model="form.diagnosis"
              class="form-control"
              rows="3"
              placeholder="Enter diagnosis..."
              required
            ></textarea>
          </div>

          <div class="mb-3">
            <label class="form-label">Medicines Prescribed</label>
            <textarea
              v-model="form.medicines"
              class="form-control"
              rows="3"
              placeholder="Medicine 1: Dosage
Medicine 2: Dosage
Medicine 3: Dosage"
            ></textarea>
          </div>

          <div class="mb-3">
            <label class="form-label">
              Prescription <span class="text-danger">*</span>
            </label>
            <textarea
              v-model="form.prescription"
              class="form-control"
              rows="3"
              placeholder="Enter prescription details..."
              required
            ></textarea>
          </div>

          <div class="mb-3">
            <label class="form-label">Doctor Notes</label>
            <textarea
              v-model="form.notes"
              class="form-control"
              rows="3"
              placeholder="Additional notes..."
            ></textarea>
          </div>

          <div class="mb-3">
            <label class="form-label">Next Visit (Optional)</label>
            <input
              v-model="form.next_visit"
              type="datetime-local"
              class="form-control"
            />
          </div>

          <div class="d-flex gap-2">
            <button
              @click="saveHistory"
              :disabled="saving"
              class="btn btn-success"
            >
              {{ saving ? 'Saving...' : 'Save Treatment History' }}
            </button>
            <button @click="() => router.back()" class="btn btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: none;
}

.form-label {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.text-danger {
  color: #dc3545;
}
</style>
