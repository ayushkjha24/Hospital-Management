import { defineStore } from "pinia"
import { ref, computed } from "vue"

export const useAuthStore = defineStore("auth", () => {
  const role = ref(localStorage.getItem("role"))
  const username = ref(localStorage.getItem("username"))

  function setAuth(token, userRole, userName) {
    localStorage.setItem("access_token", token)
    localStorage.setItem("role", userRole)
    localStorage.setItem("username", userName)

    role.value = userRole
    username.value = userName
  }

  function logout() {
    localStorage.clear()
    role.value = null
    username.value = null
  }

  return { role, username, setAuth, logout }
})
