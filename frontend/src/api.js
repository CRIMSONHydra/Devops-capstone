const BASE = "/api";

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, describe(data) || res.statusText);
  return data;
}

// FastAPI returns {detail: "msg"} or {detail: [{loc, msg}, ...]} for validation errors.
function describe(data) {
  const d = data?.detail;
  if (!d) return null;
  if (typeof d === "string") return d;
  return d.map((e) => `${(e.loc || []).slice(1).join(".")}: ${e.msg}`).join("; ");
}

const qs = (params = {}) => {
  const p = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v !== "" && v != null && v !== false && p.set(k, v));
  const s = p.toString();
  return s ? `?${s}` : "";
};

const crud = (name) => ({
  list: (params) => request("GET", `/${name}${qs(params)}`),
  create: (body) => request("POST", `/${name}`, body),
  update: (id, body) => request("PUT", `/${name}/${id}`, body),
  remove: (id) => request("DELETE", `/${name}/${id}`),
});

export const categories = crud("categories");
export const products = crud("products");
export const customers = crud("customers");
export const orders = {
  list: (params) => request("GET", `/orders${qs(params)}`),
  create: (body) => request("POST", "/orders", body),
  setStatus: (id, status) => request("PATCH", `/orders/${id}/status`, { status }),
  remove: (id) => request("DELETE", `/orders/${id}`),
};
export const dashboard = { stats: () => request("GET", "/dashboard/stats") };
