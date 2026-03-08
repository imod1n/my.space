from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import connect_db, close_db
from .models import PaymentCreate, PaymentUpdate
from . import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="Kommunalka API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/payments", status_code=201)
async def add_payment(data: PaymentCreate):
    return await crud.create_payment(data)


@app.get("/api/payments")
async def list_payments(limit: int = 200):
    return await crud.get_payments(limit)


@app.put("/api/payments/{payment_id}")
async def edit_payment(payment_id: str, data: PaymentUpdate):
    updated = await crud.update_payment(payment_id, data)
    if not updated:
        raise HTTPException(404, "Payment not found")
    return updated


@app.delete("/api/payments/all")
async def remove_all_payments():
    count = await crud.delete_all_payments()
    return {"deleted": count}


@app.delete("/api/payments/{payment_id}")
async def remove_payment(payment_id: str):
    ok = await crud.delete_payment(payment_id)
    if not ok:
        raise HTTPException(404, "Payment not found")
    return {"deleted": True}


@app.get("/api/stats/{period}")
async def stats_by_period(period: str):
    return await crud.get_stats_by_period(period)


@app.get("/api/stats-history")
async def stats_history(months: int = 6):
    return await crud.get_stats_history(months)
