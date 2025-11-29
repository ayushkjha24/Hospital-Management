export async function api(url, options = {}) {
  const token = localStorage.getItem("token");

  const res = await fetch(import.meta.env.VITE_API_URL + url, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  return await res.json();
}
