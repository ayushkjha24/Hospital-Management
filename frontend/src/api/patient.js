import { api } from "@/api/admin";

export const patientAPI = {
  dashboard: () => api("/patient/dashboard"),
  departments: () => api("/patient/departments"),
  departmentDetails: (id) => api(`/patient/department/${id}`),
  doctorDetails: (id) => api(`/patient/doctor/${id}`),
  availability: (id) => api(`/patient/doctor/${id}/availability`),
  book: (data) => api("/patient/appointment/book", "POST", data),
  cancelAppt: (id) => api(`/patient/appointment/${id}/cancel`, "DELETE"),
  history: () => api("/patient/history"),
  exportCSV: () => api("/patient/history/export"),
};
