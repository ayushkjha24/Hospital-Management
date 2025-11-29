const BASE_URL = 'http://localhost:5000';

export async function api(endpoint, method = 'GET', body = null) {
  const token = localStorage.getItem('token') || '';
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  };
  if (body && ['POST', 'PUT', 'PATCH'].includes(method)) options.body = JSON.stringify(body);

  const res = await fetch(`${BASE_URL}${endpoint}`, options);
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) throw new Error(data?.error || data?.message || `HTTP ${res.status}`);
  return data;
}

export function getDashboard() {
  return api('/patient/dashboard', 'GET');
}
export function getUpcomingAppointments() {
  return api('/patient/appointments/upcoming', 'GET');
}
export function bookAppointment(doctorId, date, startTime) {
  return api('/patient/appointment/book', 'POST', { doctor_id: doctorId, date, start_time: startTime });
}
export function cancelAppointment(appointmentId) {
  return api(`/patient/appointment/${appointmentId}/cancel`, 'POST');
}
export function getProfile() {
  return api('/patient/profile', 'GET');
}
export function updateProfile(data) {
  return api('/patient/profile', 'PUT', data);
}
export function rescheduleAppointment(apptId, date, startTime) {
  return api(`/patient/appointment/${apptId}/reschedule`, 'POST', { date, start_time: startTime });
}
