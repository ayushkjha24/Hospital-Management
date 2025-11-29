<script setup>
import { useMessagesStore } from "@/stores/messages"

const store = useMessagesStore()
</script>

<template>
  <div class="message-container">
    <div
      v-for="(msg, index) in store.messages"
      :key="index"
      class="alert alert-info mt-2"
    >
      {{ msg }}
    </div>
  </div>
</template>

<style>
.message-container {
  position: fixed;
  top: 20px;
  right: 20px;
  width: 280px;
  z-index: 9999;
}
</style>