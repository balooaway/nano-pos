from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String)
    unit_price = Column(Numeric(10, 2))
    colour = Column(String, nullable=True)
    size = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")

class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=0)

    product = relationship("Product", back_populates="stock")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Numeric(10, 2))
    vat_amount = Column(Numeric(10, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    idempotency_key = Column(String, unique=True, nullable=True)

    items = relationship("SaleItem", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")