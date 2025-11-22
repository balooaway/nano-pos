from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.ProductResponse])
def search_products(q: str = "", db: Session = Depends(get_db)):
    """Search products by SKU or name"""
    if not q:
        # Return all products if no search query
        products = db.query(models.Product).all()
    else:
        # Case-insensitive search on SKU or name
        products = db.query(models.Product).filter(
            (models.Product.sku.ilike(f"%{q}%")) | 
            (models.Product.name.ilike(f"%{q}%"))
        ).all()
    
    # Add stock quantity to each product
    result = []
    for product in products:
        product_data = schemas.ProductResponse.from_orm(product)
        stock = db.query(models.Stock).filter(models.Stock.product_id == product.id).first()
        product_data.stock_quantity = stock.quantity if stock else 0
        result.append(product_data)
    
    return result

@router.get("/next-sku")
def get_next_sku(db: Session = Depends(get_db)):
    """Generate next available SKU (PROD001, PROD002, etc.)"""
    products = db.query(models.Product).all()
    max_number = 0
    
    for product in products:
        if product.sku and product.sku.startswith('PROD'):
            # Extract number from PROD### format
            number_part = product.sku[4:]
            if number_part.isdigit():
                current_number = int(number_part)
                if current_number > max_number:
                    max_number = current_number
    
    next_number = max_number + 1
    next_sku = f"PROD{next_number:03d}"  # Format as 3-digit number
    
    return {"next_sku": next_sku}

@router.post("/", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreateManual, db: Session = Depends(get_db)):
    """Create product with manual SKU input"""
    # Check for duplicate SKU
    existing = db.query(models.Product).filter(models.Product.sku == product.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Create empty stock record
    stock = models.Stock(product_id=db_product.id, quantity=0)
    db.add(stock)
    db.commit()
    
    product_response = schemas.ProductResponse.from_orm(db_product)
    product_response.stock_quantity = 0
    return product_response

@router.post("/auto-create", response_model=schemas.ProductResponse)
def auto_create_product(product_data: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Create product with auto-generated SKU"""
    # Auto-generate the SKU
    sku_result = get_next_sku(db)
    auto_sku = sku_result["next_sku"]
    
    db_product = models.Product(
        sku=auto_sku,
        name=product_data.name,
        unit_price=product_data.unit_price,
        colour=product_data.colour or "N/A",  # Default values
        size=product_data.size or "N/A"
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Create empty stock record
    stock = models.Stock(product_id=db_product.id, quantity=0)
    db.add(stock)
    db.commit()
    
    product_response = schemas.ProductResponse.from_orm(db_product)
    product_response.stock_quantity = 0
    return product_response