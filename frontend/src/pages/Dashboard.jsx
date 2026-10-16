import * as api from "../api.js";
import { dateFmt, money, useLoad } from "../hooks.js";
import DataTable from "../components/DataTable.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

const Stat = ({ label, value }) => (
  <div className="card stat">
    <div className="stat-label">{label}</div>
    <div className="stat-value">{value}</div>
  </div>
);

export default function Dashboard() {
  const { data: s, loading, reload } = useLoad(() => api.dashboard.stats());
  if (!s) return <div className="empty">{loading ? "Loading…" : "Could not load dashboard."}</div>;
  const maxStatus = Math.max(1, ...Object.values(s.orders_by_status));

  return (
    <>
      <PageHeader title="Dashboard">
        <button className="btn" onClick={reload}>Refresh</button>
      </PageHeader>

      <div className="grid stats">
        <Stat label="Revenue" value={money(s.total_revenue)} />
        <Stat label="Orders" value={s.total_orders} />
        <Stat label="Customers" value={s.total_customers} />
        <Stat label="Products" value={s.total_products} />
      </div>

      <div className="grid two">
        <section className="card">
          <h2>Orders by status</h2>
          <ul className="bars">
            {Object.entries(s.orders_by_status).map(([k, v]) => (
              <li key={k}>
                <span className="bar-label"><StatusBadge status={k} /></span>
                <span className="bar-track"><span className={`bar-fill bar-${k}`} style={{ width: `${(v / maxStatus) * 100}%` }} /></span>
                <span className="bar-num">{v}</span>
              </li>
            ))}
          </ul>
        </section>
        <section className="card">
          <h2>Top selling products</h2>
          <DataTable rows={s.top_products} rowKey="product_id" empty="No sales yet."
            columns={[
              { label: "Product", key: "name" },
              { label: "Units sold", className: "num", key: "units_sold" },
            ]} />
        </section>
      </div>

      <div className="grid two">
        <section className="card">
          <h2>Recent orders</h2>
          <DataTable rows={s.recent_orders} empty="No orders yet."
            columns={[
              { label: "Order", render: (o) => `#${o.id}` },
              { label: "Customer", key: "customer_name" },
              { label: "Date", render: (o) => dateFmt(o.created_at) },
              { label: "Total", className: "num", render: (o) => money(o.total) },
              { label: "Status", render: (o) => <StatusBadge status={o.status} /> },
            ]} />
        </section>
        <section className="card">
          <h2>Low stock</h2>
          <DataTable rows={s.low_stock} empty="All products are well stocked."
            columns={[
              { label: "Product", render: (p) => <>{p.name} <span className="muted">{p.sku}</span></> },
              { label: "Stock", className: "num", render: (p) => <span className="low">{p.stock}</span> },
            ]} />
        </section>
      </div>
    </>
  );
}
