from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import OrderStatus


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Categories
class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase, ORM):
    id: int


# Products
class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=64)
    description: str | None = None
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    is_active: bool = True
    category_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase, ORM):
    id: int
    created_at: datetime
    category: CategoryOut | None = None


class ProductPage(BaseModel):
    items: list[ProductOut]
    total: int


# Customers
class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)


class CustomerCreate(CustomerBase):
    pass


class CustomerOut(CustomerBase, ORM):
    id: int
    created_at: datetime


# Orders
class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    items: list[OrderItemIn] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemOut(ORM):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    product_name: str | None = None


class OrderOut(ORM):
    id: int
    customer_id: int
    customer_name: str | None = None
    status: OrderStatus
    total: Decimal
    created_at: datetime
    items: list[OrderItemOut] = []


# Dashboard
class TopProduct(BaseModel):
    product_id: int
    name: str
    units_sold: int


class DashboardStats(BaseModel):
    total_revenue: Decimal
    total_orders: int
    total_customers: int
    total_products: int
    orders_by_status: dict[str, int]
    low_stock: list[ProductOut]
    recent_orders: list[OrderOut]
    top_products: list[TopProduct]
