import { useState } from "react";
import * as api from "../api.js";
import { dateFmt, useLoad } from "../hooks.js";
import { useToast } from "../components/Toast.jsx";
import DataTable from "../components/DataTable.jsx";
import Modal from "../components/Modal.jsx";
import PageHeader from "../components/PageHeader.jsx";

function CustomerForm({ initial, onSaved, onClose }) {
  const toast = useToast();
  const [form, setForm] = useState({
    name: initial?.name ?? "", email: initial?.email ?? "", phone: initial?.phone ?? "",
  });
  const [busy, setBusy] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      const body = { name: form.name.trim(), email: form.email.trim(), phone: form.phone.trim() || null };
      initial ? await api.customers.update(initial.id, body) : await api.customers.create(body);
      toast.success(initial ? "Customer updated" : "Customer created");
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
      <label>Email<input required type="email" value={form.email} onChange={set("email")} /></label>
      <label>Phone<input value={form.phone} maxLength={32} onChange={set("phone")} /></label>
      <div className="form-actions">
        <button type="button" className="btn" onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : "Save"}</button>
      </div>
    </form>
  );
}

export default function Customers() {
  const toast = useToast();
  const [q, setQ] = useState("");
  const { data, loading, reload } = useLoad(() => api.customers.list({ q }), [q]);
  const [editing, setEditing] = useState(null);

  async function remove(c) {
    if (!confirm(`Delete customer "${c.name}"?`)) return;
    try {
      await api.customers.remove(c.id);
      toast.success("Customer deleted");
      reload();
    } catch (e) {
      toast.error(e.message);
    }
  }

  const columns = [
    { label: "Name", key: "name" },
    { label: "Email", key: "email" },
    { label: "Phone", render: (c) => c.phone || "—" },
    { label: "Joined", render: (c) => dateFmt(c.created_at) },
    {
      label: "", className: "actions",
      render: (c) => (
        <>
          <button className="btn btn-sm" onClick={() => setEditing(c)}>Edit</button>
          <button className="btn btn-sm btn-danger" onClick={() => remove(c)}>Delete</button>
        </>
      ),
    },
  ];

  return (
    <>
      <PageHeader title="Customers">
        <input className="search" type="search" placeholder="Search name or email…" value={q}
          onChange={(e) => setQ(e.target.value)} />
        <button className="btn btn-primary" onClick={() => setEditing({})}>+ New customer</button>
      </PageHeader>
      <div className="card">
        <DataTable columns={columns} rows={data} loading={loading} empty="No customers found." />
      </div>
      {editing && (
        <Modal title={editing.id ? "Edit customer" : "New customer"} onClose={() => setEditing(null)}>
          <CustomerForm initial={editing.id ? editing : null} onClose={() => setEditing(null)}
            onSaved={() => { setEditing(null); reload(); }} />
        </Modal>
      )}
    </>
  );
}
