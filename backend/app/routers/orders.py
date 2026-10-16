from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..db import get_db
from ..models import Customer, Order, OrderItem, OrderStatus, Product
from ..schemas import OrderCreate, OrderOut, OrderStatusUpdate

router = APIRouter(prefix="/api/orders", tags=["orders"])

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.pending: {OrderStatus.paid, OrderStatus.cancelled},
    OrderStatus.paid: {OrderStatus.shipped, OrderStatus.cancelled},
    OrderStatus.shipped: {OrderStatus.delivered},
    OrderStatus.delivered: set(),
    OrderStatus.cancelled: set(),
}

_load = (joinedload(Order.customer), selectinload(Order.items).joinedload(OrderItem.product))


def _get_or_404(db: Session, order_id: int) -> Order:
    order = db.scalar(select(Order).options(*_load).where(Order.id == order_id))
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.get("", response_model=list[OrderOut])
def list_orders(
    status_: OrderStatus | None = Query(None, alias="status"),
    customer_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(Order).options(*_load)
    if status_:
        stmt = stmt.where(Order.status == status_)
    if customer_id is not None:
        stmt = stmt.where(Order.customer_id == customer_id)
    return db.scalars(stmt.order_by(Order.id.desc()).offset(skip).limit(limit)).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, order_id)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    if not db.get(Customer, data.customer_id):
        raise HTTPException(422, "customer_id does not exist")

    # Merge duplicate lines, then lock product rows (ordered by id to avoid deadlocks).
    quantities: dict[int, int] = {}
    for line in data.items:
        quantities[line.product_id] = quantities.get(line.product_id, 0) + line.quantity
    products = {
        p.id: p
        for p in db.scalars(
            select(Product).where(Product.id.in_(quantities)).order_by(Product.id).with_for_update()
        )
    }

    order = Order(customer_id=data.customer_id, status=OrderStatus.pending)
    total = Decimal("0")
    for product_id, qty in quantities.items():
        product = products.get(product_id)
        if not product:
            raise HTTPException(422, f"Product {product_id} does not exist")
        if not product.is_active:
            raise HTTPException(400, f"Product '{product.name}' is not active")
        if product.stock < qty:
            raise HTTPException(
                400, f"Insufficient stock for '{product.name}' (available {product.stock})"
            )
        product.stock -= qty
        total += product.price * qty
        order.items.append(OrderItem(product_id=product_id, quantity=qty, unit_price=product.price))
    order.total = total
    db.add(order)
    db.commit()
    return _get_or_404(db, order.id)


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = _get_or_404(db, order_id)
    if data.status not in ALLOWED_TRANSITIONS[order.status]:
        raise HTTPException(409, f"Cannot move order from {order.status.value} to {data.status.value}")
    if data.status == OrderStatus.cancelled:
        for item in order.items:
            item.product.stock += item.quantity
    order.status = data.status
    db.commit()
    return _get_or_404(db, order_id)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = _get_or_404(db, order_id)
    if order.status != OrderStatus.cancelled:
        raise HTTPException(409, "Only cancelled orders can be deleted")
    db.delete(order)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
