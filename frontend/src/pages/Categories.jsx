import { useState } from "react";
import * as api from "../api.js";
import { useLoad } from "../hooks.js";
import { useToast } from "../components/Toast.jsx";
import DataTable from "../components/DataTable.jsx";
import Modal from "../components/Modal.jsx";
import PageHeader from "../components/PageHeader.jsx";

function CategoryForm({ initial, onSaved, onClose }) {
  const toast = useToast();
  const [form, setForm] = useState({ name: initial?.name ?? "", description: initial?.description ?? "" });
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      const body = { name: form.name.trim(), description: form.description.trim() || null };
      initial ? await api.categories.update(initial.id, body) : await api.categories.create(body);
      toast.success(initial ? "Category updated" : "Category created");
      onSaved();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="form">
      <label>Name
        <input required maxLength={100} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
      </label>
      <label>Description
        <textarea rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
      </label>
      <div className="form-actions">
        <button type="button" className="btn" onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : "Save"}</button>
      </div>
    </form>
  );
}

export default function Categories() {
  const toast = useToast();
  const { data, loading, reload } = useLoad(() => api.categories.list());
  const [editing, setEditing] = useState(null); // null | {} (new) | category

  async function remove(c) {
    if (!confirm(`Delete category "${c.name}"?`)) return;
    try {
      await api.categories.remove(c.id);
      toast.success("Category deleted");
      reload();
    } catch (e) {
      toast.error(e.message);
    }
  }

  const columns = [
    { label: "Name", key: "name" },
    { label: "Description", render: (c) => c.description || "—" },
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
      <PageHeader title="Categories">
        <button className="btn btn-primary" onClick={() => setEditing({})}>+ New category</button>
      </PageHeader>
      <div className="card">
        <DataTable columns={columns} rows={data} loading={loading} empty="No categories yet." />
      </div>
      {editing && (
        <Modal title={editing.id ? "Edit category" : "New category"} onClose={() => setEditing(null)}>
          <CategoryForm initial={editing.id ? editing : null} onClose={() => setEditing(null)}
            onSaved={() => { setEditing(null); reload(); }} />
        </Modal>
      )}
    </>
  );
}
