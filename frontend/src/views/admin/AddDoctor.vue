<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/admin';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const form = ref({
  name: '',
  email: '',
  password: '',  // <-- Add password field
  specialization: '',
  experience_years: 0,
  department_id: null,
  is_approved: false
});

const departments = ref([]);
const loading = ref(false);
const message = ref('');
const messageClass = ref('alert-success');
const isEdit = ref(false);

async function loadDepartments() {
  // Try dedicated endpoint first, fallback to deriving from doctors list
  try {
    const res = await api('/departments');
    // Accept either { departments: [...] } or plain array
    const list = Array.isArray(res) ? res : (res.departments || []);
    departments.value = list.map(d => (typeof d === 'string' ? { id: null, name: d } : d));
  } catch (err) {
    // Fallback: derive departments from doctors endpoint
    try {
      const drs = await api('/admin/doctors');
      const docs = drs.doctors || [];
      const map = new Map();
      docs.forEach(d => {
        const name = d.department || d.specialization || 'General';
        if (!map.has(name)) map.set(name, { id: d.department_id || null, name });
      });
      departments.value = Array.from(map.values());
    } catch (e) {
      departments.value = [];
    }
  }
}

async function loadDoctor() {
  if (route.params.id) {
    isEdit.value = true;
    try {
      const res = await api(`/admin/doctors/${route.params.id}`);
      // map backend response to form shape if needed
      form.value = {
        name: res.name || '',
        email: res.email || '',
        password: '', // <-- Ensure password is empty for edit
        specialization: res.specialization || '',
        experience_years: res.experience_years || 0,
        department_id: res.department_id ?? null,
        is_approved: !!res.is_approved
      };
      // ensure specialization selection aligns with department if department_id present
      if (form.value.department_id && departments.value.length) {
        const dep = departments.value.find(d => d.id === form.value.department_id);
        if (dep) form.value.specialization = dep.name;
      }
    } catch (err) {
      showMessage(err.message, true);
    }
  }
}

function onDepartmentChange(evt) {
  const sel = departments.value.find(d => String(d.id) === String(form.value.department_id) || (d.id === null && d.name === form.value.specialization));
  if (sel) {
    form.value.specialization = sel.name;
    // if department id is null in fallback, keep department_id null
    form.value.department_id = sel.id ?? null;
  } else {
    // nothing selected
    form.value.specialization = '';
    form.value.department_id = null;
  }
}

async function handleSubmit() {
  loading.value = true;
  try {
    if (isEdit.value) {
      await api(`/admin/doctors/${route.params.id}`, 'PUT', form.value);
      showMessage('Doctor updated');
    } else {
      await api('/admin/doctors', 'POST', form.value);  // Ensure password is included
      showMessage('Doctor added');
    }
    setTimeout(() => router.push('/admin/doctors'), 1200);
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    loading.value = false;
  }
}

function showMessage(msg, isError = false) {
  message.value = msg;
  messageClass.value = isError ? 'alert-danger' : 'alert-success';
}

onMounted(async () => {
  await loadDepartments();
  await loadDoctor();
});
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">{{ isEdit ? 'Edit Doctor' : 'Add Doctor' }}</h3>
    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>
    <div class="card p-4">
      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label class="form-label">Name *</label>
          <input v-model="form.name" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Email *</label>
          <input v-model="form.email" type="email" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Password *</label>  <!-- New password field -->
          <input v-model="form.password" type="password" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Specialization (Department) *</label>
          <select v-model="form.department_id" @change="onDepartmentChange" class="form-select" required>
            <option value="">-- Select department --</option>
            <option v-for="dep in departments" :key="dep.name + (dep.id ?? '')" :value="dep.id">
              {{ dep.name }}
            </option>
          </select>
          <input type="hidden" v-model="form.specialization" />
        </div>
        <div class="mb-3">
          <label class="form-label">Experience (years)</label>
          <input v-model.number="form.experience_years" type="number" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-check-label">
            <input v-model="form.is_approved" type="checkbox" class="form-check-input" />
            Approve Doctor
          </label>
        </div>
        <div class="d-flex gap-2">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save' }}
          </button>
          <RouterLink to="/admin/doctors" class="btn btn-secondary">
            Cancel
          </RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>