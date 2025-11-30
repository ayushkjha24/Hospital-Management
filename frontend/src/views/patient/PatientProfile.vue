<script setup>
import { ref, onMounted } from 'vue';
import { api } from '@/api/patient';
import { useRouter } from 'vue-router';

const router = useRouter();
const form = ref({
  name: '',
  email: '',
  phone: '',
  medical_history: ''
});

const loading = ref(true);
const saving = ref(false);
const message = ref('');
const messageClass = ref('alert-success');

async function loadProfile() {
  try {
    const res = await api('/patient/profile');
    form.value = res;
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    loading.value = false;
  }
}

async function saveProfile() {
  saving.value = true;
  try {
    await api('/patient/profile', 'PUT', form.value);
    showMessage('Profile updated successfully');
    router.push('/');
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    saving.value = false;
  }
}

function showMessage(msg, isError = false) {
  message.value = msg;
  messageClass.value = isError ? 'alert-danger' : 'alert-success';
  setTimeout(() => (message.value = ''), 4000);
}

onMounted(loadProfile);
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">Edit Profile</h3>

    <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="card p-4">
      <form @submit.prevent="saveProfile">
        <div class="mb-3">
          <label class="form-label">Name</label>
          <input v-model="form.name" type="text" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-control" disabled />
        </div>

        <div class="mb-3">
          <label class="form-label">Phone</label>
          <input v-model="form.phone" type="tel" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label">Medical History</label>
          <textarea v-model="form.medical_history" class="form-control" rows="4"></textarea>
        </div>

        <div class="d-flex gap-2">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
          <RouterLink to="/" class="btn btn-secondary">Cancel</RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>