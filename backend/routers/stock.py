from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter(prefix="/stock", tags=["stock"])

@router.put("/{product_id}")
def update_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
    """Update product stock level"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    stock = db.query(models.Stock).filter(models.Stock.product_id == product_id).first()
    if not stock:
        # Create stock record if missing
        stock = models.Stock(product_id=product_id, quantity=quantity)
        db.add(stock)
    else:
        stock.quantity = quantity
    
    db.commit()
    return {"message": "Stock updated", "product_id": product_id, "quantity": quantity}

@router.get("/{product_id}")
def get_stock(product_id: int, db: Session = Depends(get_db)):
    """Get current stock for product"""
    stock = db.query(models.Stock).filter(models.Stock.product_id == product_id).first()
    if not stock:
        return {"product_id": product_id, "quantity": 0}
    
    return {"product_id": product_id, "quantity": stock.quantity}