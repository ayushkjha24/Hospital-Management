import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useMessagesStore = defineStore('messages', () => {
  const messages = ref([])
  
  function addMessage(message) {
    messages.value.push(message)
    setTimeout(() => {
    messages.value.shift()
  }, 2000)
  }

  return { messages, addMessage }
})