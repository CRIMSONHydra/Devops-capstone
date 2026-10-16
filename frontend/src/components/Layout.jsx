import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

const links = [
  ["/", "Dashboard", "▦"],
  ["/products", "Products", "▣"],
  ["/categories", "Categories", "≡"],
  ["/customers", "Customers", "☺"],
  ["/orders", "Orders", "✉"],
];

export default function Layout() {
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();
  useEffect(() => setOpen(false), [pathname]);

  return (
    <div className={`shell${open ? " nav-open" : ""}`}>
      <header className="topbar">
        <button className="icon-btn menu-btn" onClick={() => setOpen((o) => !o)} aria-label="Toggle menu" aria-expanded={open}>
          ☰
        </button>
        <span className="brand">Shop<b>Admin</b></span>
      </header>
      <aside className="sidebar">
        <div className="brand brand-side">Shop<b>Admin</b></div>
        <nav>
          {links.map(([to, label, icon]) => (
            <NavLink key={to} to={to} end={to === "/"} className="nav-link">
              <span className="nav-icon" aria-hidden="true">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="scrim" onClick={() => setOpen(false)} />
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
