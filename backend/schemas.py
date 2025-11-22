from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ProductBase(BaseModel):
    name: str
    unit_price: float
    colour: Optional[str] = None
    size: Optional[str] = None

class ProductCreate(ProductBase):
    sku: Optional[str] = None

class ProductCreateManual(ProductBase):
    sku: str

class ProductResponse(ProductBase):
    id: int
    sku: str
    created_at: datetime
    stock_quantity: int = 0

    class Config:
        from_attributes = True

class CartItem(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CartItem]
    idempotency_key: Optional[str] = None

class SaleItemResponse(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    product_name: str

class SaleResponse(BaseModel):
    id: int
    total_amount: float
    vat_amount: float
    created_at: datetime
    items: List[SaleItemResponse]

class DailySalesReport(BaseModel):
    date: str
    total_sales: float
    sales_count: int

class AIStubRequest(BaseModel):
    query: str

class AIStubResponse(BaseModel):
    from_date: str
    to_date: str
    intent: str
    query_type: str