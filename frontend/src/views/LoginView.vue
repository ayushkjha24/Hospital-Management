<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center">
    <div class="auth-card card shadow-sm">
      <div class="card-body p-4">
        <h2 class="text-center mb-4 fw-bold">Login</h2>

        <form @submit.prevent="login">

          <!-- Email -->
          <div class="mb-3">
            <label class="form-label">Email Address</label>
            <input
              type="email"
              class="form-control form-control-lg"
              v-model="email"
              required
            />
            <p v-if="emailError" class="text-danger small mt-1">
              {{ emailError }}
            </p>
          </div>

          <!-- Password -->
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              type="password"
              class="form-control form-control-lg"
              v-model="password"
              required
            />
            <p v-if="passwordError" class="text-danger small mt-1">
              {{ passwordError }}
            </p>
          </div>

          <!-- Server error -->
          <p v-if="loginError" class="text-danger text-center small mt-2">
            {{ loginError }}
          </p>

          <button class="btn btn-primary w-100 btn-lg mt-2">Login</button>

          <p class="text-center text-muted mt-3">
            Don't have an account?
            <RouterLink to="/register" class="fw-semibold">Register</RouterLink>
          </p>
        </form>
      </div>
    </div>
  </div>

  <RouterView />
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessagesStore } from '@/stores/messages';

const message_store = useMessagesStore();
const router = useRouter();
const email = ref('')
const password = ref('')

const emailError = ref('')
const passwordError = ref('')
const loginError = ref('')

async function login() {
  emailError.value = ''
  passwordError.value = ''
  loginError.value = ''

  if (!email.value) {
    emailError.value = 'Email is required.'
    return
  }
  if (!password.value) {
    passwordError.value = 'Password is required.'
    return
  }

  const response = await fetch("http://127.0.0.1:5000/login", {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: email.value,
      password: password.value
    })
  })

  if (response.status === 200) {
    const data = await response.json()
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('role', data.role)
    localStorage.setItem('username', data.username)
    loginError.value = ''
    //alert('Login successful!')
    message_store.addMessage('Login successful!')

    router.push('/')
  }
  else if (response.status === 401) {
    loginError.value = 'Invalid email or password.'
  }
  else {
    loginError.value = 'Something went wrong. Try again later.'
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
