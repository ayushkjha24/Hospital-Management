<script setup>
import { ref } from "vue";
import { api } from "@/api/admin";
import { useRouter } from "vue-router";

const router = useRouter();

const form = ref({
  name: "",
  description: ""
});

const loading = ref(false);
const message = ref("");
const messageClass = ref("alert-success");

function showMessage(msg, isError = false) {
  message.value = msg;
  messageClass.value = isError ? "alert-danger" : "alert-success";
}

async function handleSubmit() {
  loading.value = true;
  try {
    await api("/admin/add-department", "POST", form.value);
    showMessage("Department created successfully");

    setTimeout(() => {
      router.push("/");
    }, 1200);
  } catch (err) {
    showMessage(err.message, true);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">Add Department</h3>

    <div v-if="message" :class="['alert', messageClass]">
      {{ message }}
    </div>

    <div class="card p-4">
      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label class="form-label">Department Name *</label>
          <input v-model="form.name" type="text" class="form-control" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Description</label>
          <textarea
            v-model="form.description"
            class="form-control"
            rows="3"
            placeholder="Optional description"
          ></textarea>
        </div>

        <div class="d-flex gap-2">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? "Saving..." : "Save" }}
          </button>

          <RouterLink to="/" class="btn btn-secondary">
            Cancel
          </RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>