import { useState } from "react";
import * as api from "../api.js";
import { dateFmt, money, useLoad } from "../hooks.js";
import { useToast } from "../components/Toast.jsx";
import DataTable from "../components/DataTable.jsx";
import Modal from "../components/Modal.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

const STATUSES = ["pending", "paid", "shipped", "delivered", "cancelled"];
const NEXT = { pending: ["paid", "cancelled"], paid: ["shipped", "cancelled"], shipped: ["delivered"], delivered: [], cancelled: [] };

function NewOrderForm({ customers, products, onSaved, onClose }) {
  const toast = useToast();
  const [customerId, setCustomerId] = useState("");
  const [lines, setLines] = useState([{ product_id: "", quantity: 1 }]);
  const [busy, setBusy] = useState(false);
  const priceOf = (id) => Number(products.find((p) => String(p.id) === String(id))?.price || 0);
  const total = lines.reduce((s, l) => s + priceOf(l.product_id) * (Number(l.quantity) || 0), 0);
  const setLine = (i, patch) => setLines(lines.map((l, j) => (j === i ? { ...l, ...patch } : l)));

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.orders.create({
        customer_id: Number(customerId),
        items: lines.map((l) => ({ product_id: Number(l.product_id), quantity: Number(l.quantity) })),
      });
      toast.success("Order created");
      onSaved();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="form">
      <label>Customer
        <select required value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
          <option value="">Select customer…</option>
          {customers.map((c) => <option key={c.id} value={c.id}>{c.name} ({c.email})</option>)}
        </select>
      </label>
      <fieldset className="lines">
        <legend>Items</legend>
        {lines.map((l, i) => (
          <div className="line" key={i}>
            <select required aria-label="Product" value={l.product_id} onChange={(e) => setLine(i, { product_id: e.target.value })}>
              <option value="">Select product…</option>
              {products.map((p) => (
                <option key={p.id} value={p.id} disabled={p.stock === 0}>
                  {p.name} — {money(p.price)} ({p.stock} in stock)
                </option>
              ))}
            </select>
            <input required aria-label="Quantity" type="number" min="1" step="1" value={l.quantity}
              onChange={(e) => setLine(i, { quantity: e.target.value })} />
            <button type="button" className="icon-btn" aria-label="Remove line" disabled={lines.length === 1}
              onClick={() => setLines(lines.filter((_, j) => j !== i))}>×</button>
          </div>
        ))}
        <button type="button" className="btn btn-sm" onClick={() => setLines([...lines, { product_id: "", quantity: 1 }])}>
          + Add item
        </button>
      </fieldset>
      <div className="total-row">Total <strong>{money(total)}</strong></div>
      <div className="form-actions">
        <button type="button" className="btn" onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" disabled={busy}>{busy ? "Placing…" : "Place order"}</button>
      </div>
    </form>
  );
}

function OrderDetail({ order }) {
  return (
    <div>
      <p className="muted">{order.customer_name} · {dateFmt(order.created_at)} · <StatusBadge status={order.status} /></p>
      <DataTable rows={order.items}
        columns={[
          { label: "Product", render: (i) => i.product_name },
          { label: "Qty", className: "num", key: "quantity" },
          { label: "Unit price", className: "num", render: (i) => money(i.unit_price) },
          { label: "Subtotal", className: "num", render: (i) => money(i.unit_price * i.quantity) },
        ]} />
      <div className="total-row">Total <strong>{money(order.total)}</strong></div>
    </div>
  );
}

export default function Orders() {
  const toast = useToast();
  const [status, setStatus] = useState("");
  const { data, loading, reload } = useLoad(() => api.orders.list({ status }), [status]);
  const [creating, setCreating] = useState(false);
  const [viewing, setViewing] = useState(null);
  const customers = useLoad(() => api.customers.list({ limit: 500 }));
  const products = useLoad(() => api.products.list({ limit: 200 }), [creating]);

  async function act(fn, ok) {
    try {
      await fn();
      toast.success(ok);
      reload();
      products.reload();
    } catch (e) {
      toast.error(e.message);
    }
  }

  const columns = [
    { label: "Order", render: (o) => <strong>#{o.id}</strong> },
    { label: "Customer", key: "customer_name" },
    { label: "Date", render: (o) => dateFmt(o.created_at) },
    { label: "Items", className: "num", render: (o) => o.items.reduce((s, i) => s + i.quantity, 0) },
    { label: "Total", className: "num", render: (o) => money(o.total) },
    { label: "Status", render: (o) => <StatusBadge status={o.status} /> },
    {
      label: "", className: "actions",
      render: (o) => (
        <>
          <button className="btn btn-sm" onClick={() => setViewing(o)}>View</button>
          {NEXT[o.status].map((s) => (
            <button key={s} className={`btn btn-sm ${s === "cancelled" ? "btn-danger" : "btn-primary"}`}
              onClick={() => act(() => api.orders.setStatus(o.id, s), `Order #${o.id} → ${s}`)}>
              {s === "cancelled" ? "Cancel" : `Mark ${s}`}
            </button>
          ))}
          {o.status === "cancelled" && (
            <button className="btn btn-sm btn-danger"
              onClick={() => confirm(`Delete order #${o.id}?`) && act(() => api.orders.remove(o.id), "Order deleted")}>
              Delete
            </button>
          )}
        </>
      ),
    },
  ];

  return (
    <>
      <PageHeader title="Orders">
        <select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filter by status">
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <button className="btn btn-primary" onClick={() => setCreating(true)}>+ New order</button>
      </PageHeader>
      <div className="card">
        <DataTable columns={columns} rows={data} loading={loading} empty="No orders found." />
      </div>
      {creating && (
        <Modal title="New order" wide onClose={() => setCreating(false)}>
          <NewOrderForm customers={customers.data || []} products={(products.data?.items || []).filter((p) => p.is_active)}
            onClose={() => setCreating(false)} onSaved={() => { setCreating(false); reload(); }} />
        </Modal>
      )}
      {viewing && (
        <Modal title={`Order #${viewing.id}`} wide onClose={() => setViewing(null)}>
          <OrderDetail order={viewing} />
        </Modal>
      )}
    </>
  );
}
