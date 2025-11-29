<template>
  <div class="auth-wrapper d-flex align-items-center justify-content-center">
    <div class="auth-card card shadow-sm">
      <div class="card-body p-4">
        <h2 class="text-center mb-4 fw-bold">Create an Account</h2>

        <form @submit.prevent="registerUser">
          
          <!-- Name -->
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input
              type="text"
              class="form-control form-control-lg"
              v-model="name"
              required
            />
          </div>

          <!-- Email -->
          <div class="mb-3">
            <label class="form-label">Email Address</label>
            <input
              type="email"
              class="form-control form-control-lg"
              @input="checkEmail"
              v-model="email"
              required
            />
            <p v-if="emailError" class="text-danger mt-1 small">
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
              @input="validatePassword"
            />
            <p v-if="passwordError" class="text-danger mt-1 small">
              {{ passwordError }}
            </p>
          </div>

          <!-- Confirm Password -->
          <div class="mb-3">
            <label class="form-label">Confirm Password</label>
            <input
              type="password"
              class="form-control form-control-lg"
              v-model="confirmPassword"
              required
              @input="matchPassword"
            />
            <p v-if="matchingPasswordError" class="text-danger mt-1 small">
              {{ matchingPasswordError }}
            </p>
          </div>

          <button class="btn btn-primary w-100 btn-lg mt-2">
            Register
          </button>

          <p class="text-center text-muted mt-3">
            Already have an account?
            <RouterLink to="/login" class="fw-semibold">Login</RouterLink>
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

const router = useRouter();

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const emailError = ref('')
const passwordError = ref('')
const matchingPasswordError = ref('')

const validatePassword = () => {
  if (password.value.length < 6) {
    passwordError.value = 'Password must be at least 6 characters long.'
    return false
  }
  passwordError.value = ''
  return true
}

const matchPassword = () => {
  if (password.value != confirmPassword.value) {
    matchingPasswordError.value = 'Passwords do not match'
    return false
  }
  matchingPasswordError.value = ''
  return true
}

async function checkEmail() {
  emailError.value = ''

  if (!email.value) return

  const response = await fetch("http://127.0.0.1:5000/check_email", {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.value })
  })

  const data = await response.json()

  if (data.exists) {
    emailError.value = 'Email already exists. Please use a different one.'
  }
}

async function registerUser() {

  if (!validatePassword()) return

  if (emailError.value) return

  const response = await fetch("http://127.0.0.1:5000/register", {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: name.value,
      email: email.value,
      password: password.value
    })
  })

  if (response.status === 201) {
    alert('Registration successful! Please login.')
    router.push('/login')
  } else if (response.status === 409) {
    emailError.value = 'Email already exists.'
  } else {
    alert('Registration failed. Try again later.')
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
