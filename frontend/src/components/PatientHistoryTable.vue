<script setup>
import { computed } from 'vue';

const props = defineProps({
  patient: { type: Object, default: () => ({ id: null, name: 'Unknown', doctor_name: '', department: '' }) },
  history: { type: Array, default: () => [] }, // array of { id, visit_no, visit_type, tests_done, diagnosis, prescription, medicines }
  role: { type: String, default: 'patient' }, // 'patient' | 'doctor' | 'admin'
  showBack: { type: Boolean, default: true }
});

const emit = defineEmits(['back', 'edit', 'view']);

const rows = computed(() =>
  props.history.map((h, idx) => ({
    ...h,
    visit_no: h.visit_no ?? idx + 1,
    medicines_text: Array.isArray(h.medicines) ? h.medicines.join('\n') : (h.medicines || '')
  }))
);
</script>

<template>
  <div class="patient-history card p-3">
    <div class="d-flex justify-content-between align-items-start mb-3">
      <div>
        <h5 class="mb-1">Patient History</h5>
        <div class="small text-muted">
          <div><strong>Patient:</strong> {{ patient.name }}</div>
          <div v-if="patient.doctor_name"><strong>Doctor:</strong> {{ patient.doctor_name }}</div>
          <div v-if="patient.department"><strong>Department:</strong> {{ patient.department }}</div>
        </div>
      </div>
      <div>
        <button v-if="showBack" class="btn btn-outline-secondary btn-sm" @click="$emit('back')">Back</button>
      </div>
    </div>

    <div class="table-responsive">
      <table class="table table-sm table-bordered mb-0">
        <thead class="table-light">
          <tr>
            <th style="width:64px">Visit No.</th>
            <th>Visit Type</th>
            <th>Tests Done</th>
            <th>Diagnosis</th>
            <th>Prescription</th>
            <th>Medicines</th>
            <th v-if="role !== 'patient'" style="width:120px">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id || row.visit_no">
            <td class="align-middle text-center">{{ row.visit_no }}</td>
            <td class="align-middle">{{ row.visit_type || '—' }}</td>
            <td class="align-middle">{{ row.tests_done || '—' }}</td>
            <td class="align-middle" style="white-space:pre-line;">{{ row.diagnosis || '—' }}</td>
            <td class="align-middle" style="white-space:pre-line;">{{ row.prescription || '—' }}</td>
            <td class="align-middle"><pre class="mb-0 small meds">{{ row.medicines_text || '—' }}</pre></td>
            <td v-if="role !== 'patient'" class="align-middle text-center">
              <button v-if="role === 'doctor'" class="btn btn-sm btn-info me-1" @click="$emit('edit', row)">Update</button>
              <button v-if="role === 'admin'" class="btn btn-sm btn-primary" @click="$emit('view', row)">View</button>
            </td>
          </tr>

          <tr v-if="rows.length === 0">
            <td colspan="7" class="text-center text-muted py-4">No history available</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.patient-history { border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.04); background: #fff; }
.meds { font-family: inherit; white-space: pre-wrap; }
.table thead th { font-weight: 600; }
</style>