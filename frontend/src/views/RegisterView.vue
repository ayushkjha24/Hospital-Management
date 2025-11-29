<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-body p-4">
            <h2 class="text-center mb-4 fw-bold">Register</h2>

            <div v-if="message" :class="['alert', messageClass]">{{ message }}</div>

            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="name" type="text" class="form-control" required />
              </div>

              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="email" type="email" class="form-control" required />
              </div>

              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input v-model="phone" type="tel" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control" required />
              </div>

              <button type="submit" class="btn btn-success w-100" :disabled="loading">
                {{ loading ? 'Registering...' : 'Register' }}
              </button>
            </form>

            <hr />

            <p class="text-center">
              Already have an account?
              <RouterLink to="/login" class="text-decoration-none">Login here</RouterLink>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const name = ref('');
const email = ref('');
const password = ref('');
const phone = ref('');
const loading = ref(false);
const message = ref('');
const messageClass = ref('alert-success');

async function handleRegister() {
  loading.value = true;
  try {
    const res = await fetch('http://localhost:5000/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name.value,
        email: email.value,
        password: password.value,
        phone: phone.value
      })
    });

    const data = await res.json();
    if (!res.ok) {
      message.value = data.error || data.message || 'Registration failed';
      messageClass.value = 'alert-danger';
      return;
    }

    message.value = 'Registration successful! Redirecting to login...';
    messageClass.value = 'alert-success';

    setTimeout(() => {
      router.push('/login');
    }, 1500);
  } catch (err) {
    message.value = err.message;
    messageClass.value = 'alert-danger';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-wrapper {
  height: 100vh;
}

.auth-card {
  width: 50%;
  min-width: 380px;
  max-width: 550px;
}
</style>
