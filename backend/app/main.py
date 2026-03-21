from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from .database import connect_db, close_db
from .models import PaymentCreate, PaymentUpdate
from . import crud
from . import budget_crud
from .budget_router import router as budget_router

_API_KEY = os.getenv("API_KEY")


async def verify_api_key(x_api_key: str | None = Header(default=None)):
    if _API_KEY and x_api_key != _API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await budget_crud.ensure_budget_indexes()
    yield
    await close_db()


app = FastAPI(title="Kommunalka API", lifespan=lifespan, dependencies=[Depends(verify_api_key)])
app.include_router(budget_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://space-modin.ru",
        "https://www.space-modin.ru",
        "https://imod1n.github.io",
        "http://localhost:5173",
        "http://localhost:4173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/payments", status_code=201)
async def add_payment(data: PaymentCreate):
    return await crud.create_payment(data)


@app.get("/api/payments")
async def list_payments(limit: int = Query(default=200, ge=1, le=1000)):
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
