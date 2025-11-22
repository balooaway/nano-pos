from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, Date
from datetime import datetime, timedelta
from typing import List
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/daily-sales", response_model=List[schemas.DailySalesReport])
def get_daily_sales(from_date: str, to_date: str, db: Session = Depends(get_db)):
    """Get daily sales totals for date range"""
    try:
        start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(to_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Query sales grouped by day
    daily_sales = db.query(
        func.date(models.Sale.created_at).label('sale_date'),
        func.sum(models.Sale.total_amount).label('total_sales'),
        func.count(models.Sale.id).label('sales_count')
    ).filter(
        func.date(models.Sale.created_at) >= start_date,
        func.date(models.Sale.created_at) <= end_date
    ).group_by(
        func.date(models.Sale.created_at)
    ).order_by('sale_date').all()
    
    # Format response
    result = []
    for day in daily_sales:
        total_sales = float(day.total_sales) if day.total_sales else 0.0
        result.append(schemas.DailySalesReport(
            date=day.sale_date.strftime("%Y-%m-%d"),
            total_sales=total_sales,
            sales_count=day.sales_count or 0
        ))
    
    return result