<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary px-3">
      <a class="navbar-brand fw-bold" href="#" @click.prevent="goHome">Medisphere</a>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <!-- LEFT SIDE - ROLE-BASED MENUS -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <!-- Admin Links -->
          <template v-if="role === 'admin'">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/dashboard">Dashboard</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/doctors">Doctors</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/patients">Patients</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/admin/appointments">Appointments</RouterLink>
            </li>
          </template>

          <!-- Doctor Links -->
          <template v-if="role === 'doctor'">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/doctor/dashboard">Dashboard</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/doctor/availability">Availability</RouterLink>
            </li>
          </template>

          <!-- Patient Links -->
          <template v-if="role === 'patient'">
            <li class="nav-item">
              <RouterLink class="nav-link" to="/patient/dashboard">Dashboard</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/patient/departments">Browse Doctors</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/patient/appointments">My Appointments</RouterLink>
            </li>
          </template>
        </ul>

        <!-- RIGHT SIDE -->
        <ul class="navbar-nav ms-auto">
          <!-- If NOT logged in → Login button -->
          <li v-if="!role" class="nav-item">
            <RouterLink class="btn btn-light text-primary" to="/login">Login</RouterLink>
          </li>

          <!-- If logged in → Username dropdown -->
          <li v-else class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="userMenu" role="button" data-bs-toggle="dropdown">
              {{ username }}
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <RouterLink class="dropdown-item" to="/patient/profile" v-if="role === 'patient'">
                  Edit Profile
                </RouterLink>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <button class="dropdown-item text-danger" @click="logout">Logout</button>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';
import Navbar from '@/components/Navbar.vue';

const auth = useAuthStore();

// Use computed to get reactive values
const role = computed(() => auth.role);
const username = computed(() => auth.username);

const goHome = () => {
  router.push('/');
};

const logout = () => {
  auth.logout();
  router.push('/login');
};
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
}
</style>


