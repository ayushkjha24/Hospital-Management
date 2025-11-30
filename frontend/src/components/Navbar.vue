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
        <div class="d-flex align-items-center gap-2">
          <input
            v-model="searchQuery"
            @keyup.enter="submitSearch"
            type="text"
            class="form-control form-control-sm"
            placeholder="Search patients, doctors or department..."
            style="width: 220px;"
            aria-label="admin-search"
          />
          <select v-model="searchType" class="form-select form-select-sm" style="width: 150px;">
            <option value="all">All</option>
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
            <option value="department">Department</option>
          </select>
          <button class="btn btn-light btn-sm" @click="submitSearch">Search</button>
        </div>
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
const searchType = ref("all");

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
  const q = (searchQuery.value || "").trim();
  const type = searchType.value || "all";
  if (!q) {
    // if empty, go to admin main page
    router.push({ path: "/admin" });
    return;
  }

  // Navigate to admin dashboard/search route with query params.
  // AdminDashboard (or a dedicated search route) should read these query params
  // and perform the appropriate backend call (patient, doctor or department).
  router.push({
    path: "/admin",
    query: { q, type }
  });
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
