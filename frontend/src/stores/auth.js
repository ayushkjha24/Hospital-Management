import { defineStore } from "pinia"
import { ref, computed } from "vue"

export const useAuthStore = defineStore("auth", () => {

  const token = ref(localStorage.getItem("token") || "")
  const role = ref(localStorage.getItem("role") || "")
  const username = ref(localStorage.getItem("username") || "")
  const email = ref(localStorage.getItem("email") || "")

  const isAuthenticated = computed(() => !!token.value)

  async function login(emailInput, password) {
    try {
      const res = await fetch("http://localhost:5000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: emailInput, password }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.error || "Login failed")
      }

      const data = await res.json()

      token.value = data.access_token
      role.value = data.role

      // Safe fallback (prevents undefined username)
      username.value = data.name || data.username || ""

      email.value = data.email

      localStorage.setItem("token", token.value)
      localStorage.setItem("role", role.value)
      localStorage.setItem("username", username.value)
      localStorage.setItem("email", email.value)

      return true

    } catch (err) {
      console.error("Login error:", err)
      throw err
    }
  }

  async function register(name, emailInput, password) {
    try {
      const res = await fetch("http://localhost:5000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email: emailInput, password }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.error || "Registration failed")
      }

      return true
    } catch (err) {
      console.error("Register error:", err)
      throw err
    }
  }

  function logout() {
    token.value = ""
    role.value = ""
    username.value = ""
    email.value = ""

    localStorage.removeItem("token")
    localStorage.removeItem("role")
    localStorage.removeItem("username")
    localStorage.removeItem("email")
  }

  return {
    token,
    role,
    username,
    email,
    isAuthenticated,
    login,
    register,
    logout,
  }
}, {
  persist: true
})
