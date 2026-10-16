from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..config import settings
from ..db import get_db
from ..models import Customer, Order, OrderItem, OrderStatus, Product
from ..schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db)):
    revenue = db.scalar(
        select(func.coalesce(func.sum(Order.total), 0)).where(Order.status != OrderStatus.cancelled)
    )
    by_status = {s.value: 0 for s in OrderStatus}
    for st, count in db.execute(select(Order.status, func.count()).group_by(Order.status)):
        by_status[st.value] = count

    low_stock = db.scalars(
        select(Product)
        .options(joinedload(Product.category))
        .where(Product.is_active, Product.stock <= settings.low_stock_threshold)
        .order_by(Product.stock, Product.id)
        .limit(10)
    ).all()
    recent = db.scalars(
        select(Order)
        .options(joinedload(Order.customer), selectinload(Order.items).joinedload(OrderItem.product))
        .order_by(Order.id.desc())
        .limit(5)
    ).all()
    units = func.sum(OrderItem.quantity).label("units")
    top = db.execute(
        select(Product.id, Product.name, units)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status != OrderStatus.cancelled)
        .group_by(Product.id, Product.name)
        .order_by(units.desc(), Product.id)
        .limit(5)
    ).all()

    return {
        "total_revenue": revenue,
        "total_orders": sum(by_status.values()),
        "total_customers": db.scalar(select(func.count()).select_from(Customer)),
        "total_products": db.scalar(select(func.count()).select_from(Product)),
        "orders_by_status": by_status,
        "low_stock": low_stock,
        "recent_orders": recent,
        "top_products": [
            {"product_id": r.id, "name": r.name, "units_sold": int(r.units)} for r in top
        ],
    }
