from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from decimal import Decimal
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/sales", tags=["sales"])

@router.post("/checkout", response_model=schemas.SaleResponse)
def checkout(checkout_request: schemas.CheckoutRequest, db: Session = Depends(get_db)):
    """Process sale and update inventory"""
    try:
        # Check for duplicate sale using idempotency key
        if checkout_request.idempotency_key:
            existing_sale = db.query(models.Sale).filter(
                models.Sale.idempotency_key == checkout_request.idempotency_key
            ).first()
            if existing_sale:
                return format_sale_response(existing_sale, db)
        
        # Validate items and calculate total
        subtotal = Decimal('0.00')
        sale_items_data = []
        
        for item in checkout_request.items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            
            stock = db.query(models.Stock).filter(models.Stock.product_id == item.product_id).first()
            if not stock or stock.quantity < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough stock for {product.name}. Available: {stock.quantity if stock else 0}"
                )
            
            # Calculate item total
            item_total = Decimal(str(product.unit_price)) * Decimal(str(item.quantity))
            subtotal += item_total
            
            sale_items_data.append({
                'product': product,
                'quantity': item.quantity,
                'unit_price': float(product.unit_price),
                'stock': stock
            })
        
        # Add 15% VAT (South Africa)
        vat_rate = Decimal('0.15')
        vat_amount = subtotal * vat_rate
        total_amount = subtotal + vat_amount
        
        # Create sale record
        sale = models.Sale(
            total_amount=float(total_amount),
            vat_amount=float(vat_amount),
            idempotency_key=checkout_request.idempotency_key
        )
        db.add(sale)
        db.commit()
        db.refresh(sale)
        
        # Create sale items and reduce stock
        sale_items_response = []
        for item_data in sale_items_data:
            sale_item = models.SaleItem(
                sale_id=sale.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            db.add(sale_item)
            
            # Update inventory
            item_data['stock'].quantity -= item_data['quantity']
            
            sale_items_response.append(schemas.SaleItemResponse(
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                product_name=item_data['product'].name
            ))
        
        db.commit()
        
        return schemas.SaleResponse(
            id=sale.id,
            total_amount=float(sale.total_amount),
            vat_amount=float(sale.vat_amount),
            created_at=sale.created_at,
            items=sale_items_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")

@router.get("/", response_model=List[schemas.SaleResponse])
def list_sales(db: Session = Depends(get_db)):
    """Get all sales"""
    sales = db.query(models.Sale).all()
    result = []
    
    for sale in sales:
        items = db.query(models.SaleItem).filter(models.SaleItem.sale_id == sale.id).all()
        sale_items_response = []
        
        for item in items:
            product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            sale_items_response.append(schemas.SaleItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                product_name=product.name if product else "Unknown"
            ))
        
        result.append(schemas.SaleResponse(
            id=sale.id,
            total_amount=float(sale.total_amount),
            vat_amount=float(sale.vat_amount),
            created_at=sale.created_at,
            items=sale_items_response
        ))
    
    return result

def format_sale_response(sale, db):
    """Helper to format sale with items"""
    items = db.query(models.SaleItem).filter(models.SaleItem.sale_id == sale.id).all()
    sale_items_response = []
    
    for item in items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        sale_items_response.append(schemas.SaleItemResponse(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=float(item.unit_price),
            product_name=product.name if product else "Unknown"
        ))
    
    return schemas.SaleResponse(
        id=sale.id,
        total_amount=float(sale.total_amount),
        vat_amount=float(sale.vat_amount),
        created_at=sale.created_at,
        items=sale_items_response
    )