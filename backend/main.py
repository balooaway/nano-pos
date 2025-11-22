from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from .routers import products, sales, reports, stock, utils
from .services.ai_stub import AIStubService
from .schemas import AIStubRequest
from .database import get_db
from . import models

app = FastAPI(title="POS Nano")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(reports.router)
app.include_router(stock.router)
app.include_router(utils.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "POS Nano API is running"}

@app.post("/ask-pos")
def ask_pos(request: AIStubRequest):
    """Parse natural language sales queries"""
    return AIStubService.parse_query(request.query)

@app.post("/ask-pos-with-summary")
def ask_pos_with_summary(request: AIStubRequest, db: Session = Depends(get_db)):
    """Get sales summary for parsed query"""
    from datetime import datetime
    
    intent = AIStubService.parse_query(request.query)
    
    start_date = datetime.strptime(intent.from_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(intent.to_date, "%Y-%m-%d").date()
    
    sales_data = db.query(models.Sale).filter(
        func.date(models.Sale.created_at) >= start_date,
        func.date(models.Sale.created_at) <= end_date
    ).all()
    
    total_sales = len(sales_data)
    total_revenue = sum(float(sale.total_amount) for sale in sales_data)
    days_count = (end_date - start_date).days + 1
    
    if total_sales == 0:
        response_text = f"No sales in the last {days_count} days."
    else:
        response_text = f"{total_sales} sales, R{total_revenue:,.2f} revenue in {days_count} days."
    
    return {
        "from_date": intent.from_date,
        "to_date": intent.to_date,
        "summary_text": response_text,
        "total_sales": total_sales,
        "total_revenue": total_revenue
    }

# Serve frontend
PROJECT_ROOT = Path(__file__).parent.parent
app.mount("/", StaticFiles(directory=PROJECT_ROOT / "frontend", html=True), name="frontend")