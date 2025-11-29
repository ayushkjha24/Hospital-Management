import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import AdminDashboard from "@/views/admin/AdminDashboard.vue";
import AdminDoctors from "@/views/admin/AdminDoctors.vue";
import AddDoctor from "@/views/admin/AddDoctor.vue";
import AdminPatients from "@/views/admin/AdminPatients.vue";
import PatientHistory from "@/views/admin/PatientHistory.vue";
import UpcomingAppointments from "@/views/admin/UpcomingAppointments.vue";
import DoctorDashboard from "@/views/doctor/DoctorDashboard.vue";
import PatientDashboard from "@/views/patient/PatientDashboard.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },

    {
      path: '/doctor/dashboard',
      name: 'DoctorDashboard',
      component: DoctorDashboard,
    },
    {
      path: '/patient/dashboard',
      name: 'PatientDashboard',
      component: PatientDashboard,
    },

    {
      path: '/login',
      name: 'login',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
      {
    path: "/admin/dashboard",
    name: "AdminDashboard",
    component: AdminDashboard,
  },
  {
    path: "/admin/doctors",
    name: "AdminDoctors",
    component: AdminDoctors,
  },
  {
    path: "/admin/doctors/add",
    name: "AddDoctor",
    component: AddDoctor,
  },
  {
    path: "/admin/patients",
    name: "AdminPatients",
    component: AdminPatients,
  },
  {
    path: "/admin/patients/history/:id",
    name: "PatientHistory",
    component: PatientHistory,
  },
  {
    path: "/admin/appointments",
    name: "UpcomingAppointments",
    component: UpcomingAppointments,
  },

  {
  path: "/doctor/dashboard",
  component: () => import("@/views/doctor/DoctorDashboard.vue")
},
{
  path: "/doctor/history/update/:appointmentId",
  component: () => import("@/views/doctor/DoctorHistoryUpdate.vue")
},
{
  path: "/doctor/history/:patientId",
  component: () => import("@/views/doctor/DoctorPatientHistory.vue")
},
{
  path: "/doctor/availability",
  component: () => import("@/views/doctor/DoctorAvailability.vue")
},
{
  path: "/doctor/patients",
  component: () => import("@/views/doctor/DoctorPatientHistory.vue")
},
{
  path: "/patient",
  children: [
    { path: "dashboard", name: "PatientDashboard", component: () => import("@/views/patient/PatientDashboard.vue") },
    { path: "department/:deptId", name: "DepartmentDetails", component: () => import("@/views/patient/DepartmentDetails.vue") },
    { path: "doctor/:doctorId", name: "DoctorDetails", component: () => import("@/views/patient/DoctorDetails.vue") },
    { path: "doctor/:doctorId/availability", name: "DoctorAvailability", component: () => import("@/views/patient/DoctorAvailability.vue") },
    { path: "history", name: "PatientHistory", component: () => import("@/views/patient/PatientHistory.vue") },
  ]
}
  ],
})

router.beforeEach((to, from, next) => {
  const role = localStorage.getItem("role");
  const token = localStorage.getItem("access_token");

  // Auto redirect when visiting home
  if (to.path === "/") {
    if (!token) return next(); // not logged in → show HomeView

    if (role === "admin") return next("/admin/dashboard");
    if (role === "doctor") return next("/doctor/dashboard");
    if (role === "patient") return next("/patient/dashboard");

    return next();
  }

  // Protect admin routes
  if (to.path.startsWith("/admin") && role !== "admin") {
    return next("/");
  }

  // Protect doctor routes
  if (to.path.startsWith("/doctor") && role !== "doctor") {
    return next("/");
  }

  // Protect patient routes
  if (to.path.startsWith("/patient") && role !== "patient") {
    return next("/");
  }

  next();
});


export default router
