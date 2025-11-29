<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { apiPublic } from '@/api/public';

const router = useRouter();
const departments = ref([]);
const selectedDeptId = ref(null);
const doctors = ref([]);
const loading = ref(true);
const message = ref('');

async function loadDepartments() {
  try {
    const res = await apiPublic('/departments');
    departments.value = res.departments || [];
  } catch (err) {
    message.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function selectDepartment(deptId) {
  selectedDeptId.value = deptId;
  try {
    const res = await apiPublic(`/doctors?department_id=${deptId}`);
    doctors.value = res.doctors || [];
  } catch (err) {
    message.value = err.message;
  }
}

function viewDoctor(doctorId) {
  router.push(`/patient/doctor/${doctorId}/availability`);
}

onMounted(loadDepartments);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">Browse Doctors by Department</h3>

    <div v-if="message" class="alert alert-danger">{{ message }}</div>

    <div class="row">
      <div class="col-md-3">
        <div class="list-group">
          <button
            v-for="dep in departments"
            :key="dep.id"
            @click="selectDepartment(dep.id)"
            :class="['list-group-item', 'list-group-item-action', selectedDeptId === dep.id ? 'active' : '']"
          >
            {{ dep.name }}
          </button>
        </div>
      </div>

      <div class="col-md-9">
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status"></div>
        </div>

        <div v-else>
          <div v-if="doctors.length === 0" class="alert alert-info">
            Select a department to view doctors
          </div>

          <div class="row">
            <div v-for="doc in doctors" :key="doc.id" class="col-md-6 mb-3">
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">{{ doc.name }}</h5>
                  <p class="card-text text-muted">{{ doc.specialization }}</p>
                  <p class="small"><strong>Experience:</strong> {{ doc.experience_years || 'N/A' }} years</p>
                  <button @click="viewDoctor(doc.id)" class="btn btn-primary btn-sm w-100">
                    View Availability & Book
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
