# main.py - FastAPI application entry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports Store", version="1.0.0")

# CORS øÁ”Ú≈‰÷√
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import customers, products, cart, orders, admin, payments
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(payments.router)


@app.get("/")
def root():
    return {"message": "Sports Store API"}