<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary px-3">
    <a class="navbar-brand fw-bold" href="#" @click.prevent="goHome">Medisphere</a>

    <button
      class="navbar-toggler"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#navbarContent"
    >
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarContent">

      <!-- LEFT SIDE - ROLE-BASED MENUS -->
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">

        <!-- Admin Links -->
        <template v-if="role === 'admin'">
          <li class="nav-item"><RouterLink class="nav-link" to="/admin/doctors">Doctors</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/admin/patients">Patients</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/admin/appointments">Appointments</RouterLink></li>
        </template>

        <!-- Doctor Links -->
        <template v-if="role === 'doctor'">
          <li class="nav-item"><RouterLink class="nav-link" to="/doctor/appointments">Appointments</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/doctor/patients">My Patients</RouterLink></li>
        </template>

        <!-- Patient Links -->
        <template v-if="role === 'patient'">
          <li class="nav-item"><RouterLink class="nav-link" to="/patient/departments">Departments</RouterLink></li>
          <li class="nav-item"><RouterLink class="nav-link" to="/patient/appointments">My Appointments</RouterLink></li>
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
          <RouterLink
            class="nav-link dropdown-toggle"
            to="#"
            id="userMenu"
            role="button"
            data-bs-toggle="dropdown"
          >
            {{ username }}
          </RouterLink>

          <ul class="dropdown-menu dropdown-menu-end">
            <li v-if="role === 'patient'"><RouterLink class="dropdown-item" to="/patient/profile">Edit Profile</RouterLink></li>
            <li v-if="role === 'patient'"><RouterLink class="dropdown-item" to="/patient/history">History</RouterLink></li>

            <li><hr class="dropdown-divider" /></li>

            <li>
              <button class="dropdown-item text-danger" @click="logout">
                Logout
              </button>
            </li>
          </ul>
        </li>

      </ul>
    </div>
  </nav>
<Messages/>
  <RouterView />
</template>

<script setup>
import { useAuthStore } from "@/stores/auth.js";
import Messages from "@/components/Messages.vue";
import { computed } from "vue";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const role = auth.role;
const username = auth.username;

const goHome = () => {
  router.push("/");
};

const logout = () => {
  auth.logout();
  router.push("/login");
};
</script>


