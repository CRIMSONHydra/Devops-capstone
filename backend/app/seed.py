"""Idempotent demo data: `python -m app.seed` (runs only when the DB has no products)."""
from decimal import Decimal

from sqlalchemy import func, select

from .db import SessionLocal
from .models import Category, Customer, Order, OrderItem, OrderStatus, Product

CATEGORIES = ["Electronics", "Apparel", "Home & Kitchen", "Books"]
PRODUCTS = [
    ("Wireless Headphones", "EL-001", "89.99", 40, 0),
    ("Mechanical Keyboard", "EL-002", "119.00", 8, 0),
    ("Running Shoes", "AP-001", "64.50", 25, 1),
    ("Denim Jacket", "AP-002", "79.00", 5, 1),
    ("Espresso Machine", "HK-001", "249.00", 12, 2),
    ("Cast Iron Skillet", "HK-002", "34.95", 60, 2),
    ("Clean Code", "BK-001", "39.99", 100, 3),
    ("Designing Data-Intensive Applications", "BK-002", "54.00", 3, 3),
]
CUSTOMERS = [
    ("Ada Lovelace", "ada@example.com", "+1 555 0100"),
    ("Alan Turing", "alan@example.com", "+1 555 0101"),
    ("Grace Hopper", "grace@example.com", "+1 555 0102"),
]
ORDERS = [  # (customer idx, status, [(product idx, qty)])
    (0, OrderStatus.delivered, [(0, 1), (6, 2)]),
    (1, OrderStatus.shipped, [(4, 1)]),
    (2, OrderStatus.paid, [(2, 2), (3, 1)]),
    (0, OrderStatus.pending, [(5, 3)]),
    (1, OrderStatus.cancelled, [(1, 1)]),
]


def seed() -> bool:
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Product)):
            return False
        cats = [Category(name=n) for n in CATEGORIES]
        prods = [
            Product(name=n, sku=s, price=Decimal(p), stock=st, category=cats[c])
            for n, s, p, st, c in PRODUCTS
        ]
        custs = [Customer(name=n, email=e, phone=p) for n, e, p in CUSTOMERS]
        db.add_all(cats + prods + custs)
        db.flush()
        for ci, status, lines in ORDERS:
            order = Order(customer=custs[ci], status=status)
            total = Decimal(0)
            for pi, qty in lines:
                prod = prods[pi]
                order.items.append(OrderItem(product=prod, quantity=qty, unit_price=prod.price))
                total += prod.price * qty
                if status != OrderStatus.cancelled:
                    prod.stock -= qty
            order.total = total
            db.add(order)
        db.commit()
        return True


if __name__ == "__main__":
    print("seeded demo data" if seed() else "database not empty, skipping seed")
