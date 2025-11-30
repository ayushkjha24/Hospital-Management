<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary px-3">
    <!-- LEFT: LOGO -->
    <a class="navbar-brand fw-bold" href="#" @click.prevent="goHome">
      Medisphere
    </a>
    <!-- RIGHT SIDE BUTTONS -->
    <div class="ms-auto d-flex align-items-center gap-3">

      <!-- ADMIN VIEW -->
      <template v-if="role === 'admin'"> 
        <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
      </template>

      <!-- DOCTOR VIEW -->
      <template v-else-if="role === 'doctor'">
        <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
      </template>

      <!-- PATIENT VIEW -->
      <template v-else-if="role === 'patient'">
        <RouterLink class="btn btn-light btn-sm" to="/patient/profile">Edit</RouterLink>
        <RouterLink class="btn btn-light btn-sm" to="/patient/appointments">History</RouterLink>
        <button class="btn btn-danger btn-sm" @click="logout">Logout</button>
      </template>

      <!-- GUEST VIEW -->
      <template v-else>
        <RouterLink class="btn btn-light btn-sm" to="/register">Register</RouterLink>
        <RouterLink class="btn btn-light btn-sm" to="/login">Login</RouterLink>
      </template>

    </div>
  </nav>
</template>

<script setup>
import { RouterLink, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { computed, ref } from 'vue';

const auth = useAuthStore();
const router = useRouter();

const role = computed(() => auth.role);
const goHome = () => {
  router.push("/");
};

const logout = () => {
  auth.logout();
  router.push("/login");
};
</script>

<style scoped>
.navbar-brand {
  cursor: pointer;
}
.gap-3 > * {
  margin-left: 10px;
}
</style>
