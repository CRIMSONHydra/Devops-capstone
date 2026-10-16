import { useEffect, useState } from "react";
import * as api from "../api.js";
import { money, useLoad } from "../hooks.js";
import { useToast } from "../components/Toast.jsx";
import DataTable from "../components/DataTable.jsx";
import Modal from "../components/Modal.jsx";
import PageHeader from "../components/PageHeader.jsx";

const PAGE = 10;
const LOW_STOCK = 10;

function ProductForm({ initial, categories, onSaved, onClose }) {
  const toast = useToast();
  const [form, setForm] = useState({
    name: initial?.name ?? "", sku: initial?.sku ?? "", description: initial?.description ?? "",
    price: initial?.price ?? "", stock: initial?.stock ?? 0,
    category_id: initial?.category_id ?? "", is_active: initial?.is_active ?? true,
  });
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      const body = {
        name: form.name.trim(), sku: form.sku.trim(), description: form.description.trim() || null,
        price: String(form.price), stock: Number(form.stock),
        category_id: form.category_id === "" ? null : Number(form.category_id),
        is_active: form.is_active,
      };
      initial ? await api.products.update(initial.id, body) : await api.products.create(body);
      toast.success(initial ? "Product updated" : "Product created");
      onSaved();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="form">
      <label>Name<input required value={form.name} onChange={set("name")} /></label>
      <div className="form-row">
        <label>SKU<input required value={form.sku} maxLength={64} onChange={set("sku")} /></label>
        <label>Category
          <select value={form.category_id} onChange={set("category_id")}>
            <option value="">— none —</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>
      </div>
      <div className="form-row">
        <label>Price (USD)
          <input required type="number" min="0" step="0.01" value={form.price} onChange={set("price")} />
        </label>
        <label>Stock
          <input required type="number" min="0" step="1" value={form.stock} onChange={set("stock")} />
        </label>
      </div>
      <label>Description<textarea rows={3} value={form.description} onChange={set("description")} /></label>
      <label className="check">
        <input type="checkbox" checked={form.is_active}
          onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> Active (available for orders)
      </label>
      <div className="form-actions">
        <button type="button" className="btn" onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : "Save"}</button>
      </div>
    </form>
  );
}

export default function Products() {
  const toast = useToast();
  const [q, setQ] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [lowStock, setLowStock] = useState(false);
  const [page, setPage] = useState(0);
  const [editing, setEditing] = useState(null);
  const cats = useLoad(() => api.categories.list());
  const { data, loading, reload } = useLoad(
    () => api.products.list({ q, category_id: categoryId, low_stock: lowStock, skip: page * PAGE, limit: PAGE }),
    [q, categoryId, lowStock, page]
  );
  useEffect(() => setPage(0), [q, categoryId, lowStock]);

  const total = data?.total ?? 0;
  const pages = Math.max(1, Math.ceil(total / PAGE));

  async function remove(p) {
    if (!confirm(`Delete product "${p.name}"?`)) return;
    try {
      await api.products.remove(p.id);
      toast.success("Product deleted");
      reload();
    } catch (e) {
      toast.error(e.message);
    }
  }

  const columns = [
    { label: "Product", render: (p) => <><strong>{p.name}</strong><div className="muted">{p.sku}</div></> },
    { label: "Category", render: (p) => p.category?.name || "—" },
    { label: "Price", className: "num", render: (p) => money(p.price) },
    {
      label: "Stock", className: "num",
      render: (p) => <span className={p.stock <= LOW_STOCK ? "low" : ""}>{p.stock}</span>,
    },
    { label: "Status", render: (p) => <span className={`badge ${p.is_active ? "badge-paid" : "badge-cancelled"}`}>{p.is_active ? "active" : "inactive"}</span> },
    {
      label: "", className: "actions",
      render: (p) => (
        <>
          <button className="btn btn-sm" onClick={() => setEditing(p)}>Edit</button>
          <button className="btn btn-sm btn-danger" onClick={() => remove(p)}>Delete</button>
        </>
      ),
    },
  ];

  return (
    <>
      <PageHeader title="Products">
        <button className="btn btn-primary" onClick={() => setEditing({})}>+ New product</button>
      </PageHeader>
      <div className="filters">
        <input className="search" type="search" placeholder="Search name or SKU…" value={q}
          onChange={(e) => setQ(e.target.value)} />
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} aria-label="Filter by category">
          <option value="">All categories</option>
          {(cats.data || []).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <label className="check">
          <input type="checkbox" checked={lowStock} onChange={(e) => setLowStock(e.target.checked)} /> Low stock only
        </label>
      </div>
      <div className="card">
        <DataTable columns={columns} rows={data?.items} loading={loading} empty="No products found." />
        <div className="pager">
          <span className="muted">{total} product{total === 1 ? "" : "s"}</span>
          <div>
            <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>‹ Prev</button>
            <span className="pager-pos">{page + 1} / {pages}</span>
            <button className="btn btn-sm" disabled={page + 1 >= pages} onClick={() => setPage(page + 1)}>Next ›</button>
          </div>
        </div>
      </div>
      {editing && (
        <Modal title={editing.id ? "Edit product" : "New product"} onClose={() => setEditing(null)}>
          <ProductForm initial={editing.id ? editing : null} categories={cats.data || []}
            onClose={() => setEditing(null)} onSaved={() => { setEditing(null); reload(); }} />
        </Modal>
      )}
    </>
  );
}
