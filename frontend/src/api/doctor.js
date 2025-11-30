const BASE_URL = 'http://localhost:5000';

export async function api(endpoint, method = 'GET', body = null, skipPrefix = false) {
  const token = localStorage.getItem('token') || '';

  // Allow bypassing /doctor prefix
  const fullEndpoint = skipPrefix
    ? endpoint
    : endpoint.startsWith('/doctor')
      ? endpoint
      : `/doctor${endpoint}`;

  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  };

  if (body && ['POST', 'PUT', 'PATCH'].includes(method)) {
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${BASE_URL}${fullEndpoint}`, options);
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    throw new Error(data?.error || data?.message || `HTTP ${res.status}`);
  }
  return data;
}
