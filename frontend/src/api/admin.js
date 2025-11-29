const BASE = "http://127.0.0.1:5000";

export async function api(url, method = "GET", body = null) {
  const token = localStorage.getItem("token");

  const res = await fetch(BASE + url, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: token ? `Bearer ${token}` : ""
    },
    body: body ? JSON.stringify(body) : null
  });

  return res.json ? res.json() : res;
}
