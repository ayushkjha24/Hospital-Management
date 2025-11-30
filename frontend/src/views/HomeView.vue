<script setup>
import { useAuthStore } from "@/stores/auth.js"

import AdminDashboard from "@/views/admin/AdminDashboard.vue"
import DoctorDashboard from "@/views/doctor/DoctorDashboard.vue"
import PatientDashboard from "@/views/patient/PatientDashboard.vue"

const auth = useAuthStore()
</script>

<template>
  <!-- If NOT logged in → Show homepage -->
  <div v-if="!auth.role" class="home-wrapper">

    <!-- Hero Section -->
    <section class="hero-section text-center text-white">
      <div class="container py-5">
        <h1 class="display-4 fw-bold mb-3">Medisphere</h1>
        <p class="lead mb-4">
          Your trusted platform for seamless medical care — anytime, anywhere.
        </p>

        <div class="mt-4">
          <RouterLink to="/login" class="btn btn-primary btn-lg me-2">
            Login
          </RouterLink>
          
          <RouterLink to="/register" class="btn btn-outline-light btn-lg">
            Register
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Highlights Section -->
    <section class="features-section py-5 bg-light">
      <div class="container">
        <div class="row text-center">

          <div class="col-md-4 mb-4">
            <div class="feature-card p-4">
              <i class="bi bi-calendar-check display-5 text-primary"></i>
              <h5 class="fw-bold mt-3">Easy Appointments</h5>
              <p class="text-muted">
                Book and manage appointments effortlessly with the best doctors.
              </p>
            </div>
          </div>

          <div class="col-md-4 mb-4">
            <div class="feature-card p-4">
              <i class="bi bi-people display-5 text-success"></i>
              <h5 class="fw-bold mt-3">Expert Doctors</h5>
              <p class="text-muted">
                Connect with qualified and experienced specialists instantly.
              </p>
            </div>
          </div>

          <div class="col-md-4 mb-4">
            <div class="feature-card p-4">
              <i class="bi bi-shield-check display-5 text-info"></i>
              <h5 class="fw-bold mt-3">Secure Platform</h5>
              <p class="text-muted">
                Your medical history and data remain safe and encrypted.
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  </div>

  <!-- ADMIN Dashboard -->
  <AdminDashboard v-else-if="auth.role === 'admin'" />

  <!-- DOCTOR Dashboard -->
  <DoctorDashboard v-else-if="auth.role === 'doctor'" />

  <!-- PATIENT Dashboard -->
  <PatientDashboard v-else-if="auth.role === 'patient'" />
</template>

<style scoped>
.hero-section {
  background: linear-gradient(
    135deg,
    #007bff 0%,
    #0056d2 50%,
    #003c9e 100%
  );
}

.feature-card {
  background: white;
  border-radius: 12px;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 14px rgba(0,0,0,0.15);
}

.home-wrapper {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
