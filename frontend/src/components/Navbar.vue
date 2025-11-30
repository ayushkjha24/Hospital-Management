<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary px-3">
    <!-- LEFT: LOGO -->
    <a class="navbar-brand fw-bold" href="#" @click.prevent="goHome">
      Medisphere
    </a>

    <!-- WELCOME TEXT right after logo -->
    <span v-if="role" class="text-white ms-3 fw-semibold">
      Welcome {{ welcomeName }}
    </span>

    <!-- RIGHT SIDE BUTTONS -->
    <div class="ms-auto d-flex align-items-center gap-3">

      <!-- ADMIN VIEW -->
      <template v-if="role === 'admin'">
        <input
          v-model="searchQuery"
          type="text"
          class="form-control form-control-sm"
          placeholder="Search..."
          style="width: 200px;"
        />
        <button class="btn btn-light btn-sm" @click="submitSearch">Search</button>
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
const username = computed(() => auth.username);

const searchQuery = ref("");

// Intelligent fallback so we NEVER see "undefined"
const welcomeName = computed(() => {
  if (role.value === "admin") return "Admin";
  if (role.value === "doctor") return username.value || "Doctor";
  if (role.value === "patient") return username.value || "Patient";
  return "";
});

const goHome = () => {
  router.push("/");
};

const logout = () => {
  auth.logout();
  router.push("/login");
};

const submitSearch = () => {
  console.log("Search:", searchQuery.value);
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
