import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false }
  },

  // Admin routes
  {
    path: '/admin',
    redirect: { name: 'AdminDashboard' }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/doctors',
    name: 'AdminDoctors',
    component: () => import('@/views/admin/AdminDoctors.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/doctors/add',
    name: 'AddDoctor',
    component: () => import('@/views/admin/AddDoctor.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/add-department',
    name: 'AddDepartment',
    component: () => import('@/views/admin/AddDepartment.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/doctors/edit/:id',
    name: 'EditDoctor',
    component: () => import('@/views/admin/AddDoctor.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/patients',
    name: 'AdminPatients',
    component: () => import('@/views/admin/AdminPatients.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/edit-patient/:id',
    name: 'EditPatient',
    component: () => import('@/views/admin/AdminPatients.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/appointments',
    name: 'AdminAppointments',
    component: () => import('@/views/admin/UpcomingAppointments.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/admin/patient-history/:id',
    name: 'AdminPatientHistory',
    component: () => import('@/views/admin/PatientHistory.vue'),
    meta: { requiresAuth: true, roles: ['admin'] }
  },

  // Doctor routes
  {
    path: '/doctor',
    redirect: { name: 'DoctorDashboard' }
  },
  {
    path: '/doctor/dashboard',
    name: 'DoctorDashboard',
    component: () => import('@/views/doctor/DoctorDashboard.vue'),
    meta: { requiresAuth: true, roles: ['doctor'] }
  },
  {
    path: '/doctor/availability',
    name: 'DoctorAvailability',
    component: () => import('@/views/doctor/DoctorAvailability.vue'),
    meta: { requiresAuth: true, roles: ['doctor'] }
  },
  {
    path: '/doctor/history/:id',
    name: 'DoctorPatientHistory',
    component: () => import('@/views/doctor/DoctorPatientHistory.vue'),
    meta: { requiresAuth: true, roles: ['doctor'] }
  },
  {
    path: '/doctor/history/update/:id',
    name: 'DoctorHistoryUpdate',
    component: () => import('@/views/doctor/DoctorHistoryUpdate.vue'),
    meta: { requiresAuth: true, roles: ['doctor'] }
  },
  {
    path: '/doctor/patient/:patientId/appointment/:appointmentId/update-history',
    name: 'DoctorUpdateHistory',
    component: () => import('@/views/doctor/DoctorHistoryUpdate.vue'),
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
  path: '/doctor/patient/:patientId/history',
  name: 'DoctorPatientHistory',
  component: () => import('@/views/doctor/DoctorPatientHistory.vue')
}
  ,

  // Patient routes
  {
    path: '/patient',
    redirect: { name: 'PatientDashboard' }
  },
  {
    path: '/patient/dashboard',
    name: 'PatientDashboard',
    component: () => import('@/views/patient/PatientDashboard.vue'),
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/patient/profile',
    name: 'PatientProfile',
    component: () => import('@/views/patient/PatientProfile.vue'),
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/patient/departments',
    name: 'PatientDepartments',
    component: () => import('@/views/patient/DepartmentDetails.vue'),
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/patient/doctors/:specialization',
    name: 'PatientDoctors',
    component: () => import('@/views/patient/DoctorDetails.vue'),
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/patient/doctor/:id/availability',
    name: 'DoctorAvailabilityView',
    component: () => import('@/views/patient/DoctorAvailability.vue'),
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/patient/appointments',
    name: 'PatientAppointments',
    component: () => import('@/views/patient/PatientHistory.vue'),
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/patient/appointment/:id/reschedule',
    name: 'PatientRescheduleAppointment',
    component: () => import('@/views/patient/RescheduleAppointment.vue'),
    meta: { requiresAuth: true, role: 'patient' }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  const auth = useAuthStore();

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'Login' });
  } else if (to.meta.roles && !to.meta.roles.includes(auth.role)) {
    next({ name: 'Home' });
  } else {
    next();
  }
});

export default router;
