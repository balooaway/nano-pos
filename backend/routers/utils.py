from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router = APIRouter(prefix="/utils", tags=["utils"])

@router.delete("/reset-all")
def reset_all_data(db: Session = Depends(get_db)):
    """DANGER: Delete all data and reset database"""
    try:
        # Disable foreign key checks
        db.execute(text("SET session_replication_role = 'replica';"))
        
        # Clear all tables
        db.execute(text("DELETE FROM sale_items;"))
        db.execute(text("DELETE FROM sales;"))
        db.execute(text("DELETE FROM stock;"))
        db.execute(text("DELETE FROM products;"))
        
        # Reset auto-increment counters
        db.execute(text("ALTER SEQUENCE products_id_seq RESTART WITH 1;"))
        db.execute(text("ALTER SEQUENCE stock_id_seq RESTART WITH 1;"))
        db.execute(text("ALTER SEQUENCE sales_id_seq RESTART WITH 1;"))
        db.execute(text("ALTER SEQUENCE sale_items_id_seq RESTART WITH 1;"))
        
        # Re-enable foreign key checks
        db.execute(text("SET session_replication_role = 'origin';"))
        
        db.commit()
        
        return {
            "message": "Database reset complete",
            "reset_tables": ["products", "stock", "sales", "sale_items"]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

@router.get("/stats")
def get_database_stats(db: Session = Depends(get_db)):
    """Get record counts for all tables"""
    try:
        product_count = db.execute(text("SELECT COUNT(*) FROM products;")).scalar()
        stock_count = db.execute(text("SELECT COUNT(*) FROM stock;")).scalar()
        sales_count = db.execute(text("SELECT COUNT(*) FROM sales;")).scalar()
        sale_items_count = db.execute(text("SELECT COUNT(*) FROM sale_items;")).scalar()
        
        return {
            "products": product_count,
            "stock_entries": stock_count,
            "sales": sales_count,
            "sale_items": sale_items_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not get stats: {str(e)}")