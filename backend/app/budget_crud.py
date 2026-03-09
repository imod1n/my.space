import os
import uuid
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from .database import get_collection
from .budget_models import (
    AccountCreate, AccountUpdate,
    AdvanceAdd, BalanceSet, IncomeCreate, TransferCreate,
)

SESSION_TTL_HOURS = 24


# ── Helpers ───────────────────────────────────────────────────────────────────

def _id(doc: dict) -> str:
    return str(doc["_id"])


def _get_budget_users() -> list[dict]:
    """Load budget users from Render env vars (never exposed to frontend)."""
    users, i = [], 1
    while True:
        name = os.getenv(f"BUDGET_USER{i}_NAME")
        hash_ = os.getenv(f"BUDGET_USER{i}_HASH")
        if not name or not hash_:
            break
        users.append({"id": name.lower(), "name": name, "hash": hash_})
        i += 1
    return users


# ── Indexes (called at startup) ───────────────────────────────────────────────

async def ensure_budget_indexes():
    sessions  = get_collection("budget_sessions")
    accounts  = get_collection("budget_accounts")
    periods   = get_collection("budget_periods")
    balances  = get_collection("budget_balances")
    income    = get_collection("budget_income")
    transfers = get_collection("budget_transfers")

    # TTL index removes expired sessions automatically
    await sessions.create_index("expires_at", expireAfterSeconds=0)
    await sessions.create_index("token")

    await accounts.create_index([("user_id", 1), ("sort_order", 1)])

    await periods.create_index([("user_id", 1), ("start_date", -1)])
    await periods.create_index([("user_id", 1), ("is_active", 1)])

    await balances.create_index(
        [("user_id", 1), ("period_id", 1), ("account_id", 1)],
        unique=True,
    )

    await income.create_index([("user_id", 1), ("period_id", 1)])
    await transfers.create_index([("user_id", 1), ("period_id", 1)])


# ── Auth ──────────────────────────────────────────────────────────────────────

async def authenticate(user_id: str, pin_hash: str) -> dict | None:
    users = _get_budget_users()
    user = next(
        (u for u in users if u["id"] == user_id and u["hash"] == pin_hash),
        None,
    )
    if not user:
        return None

    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS)

    await get_collection("budget_sessions").insert_one({
        "token":      token,
        "user_id":    user_id,
        "created_at": datetime.now(timezone.utc),
        "expires_at": expires_at,
    })
    return {"token": token, "user_id": user_id, "name": user["name"]}


async def validate_token(token: str) -> str | None:
    session = await get_collection("budget_sessions").find_one({
        "token":      token,
        "expires_at": {"$gt": datetime.now(timezone.utc)},
    })
    return session["user_id"] if session else None


# ── Accounts ──────────────────────────────────────────────────────────────────

def _fmt_account(doc: dict) -> dict:
    return {
        "id":         _id(doc),
        "user_id":    doc["user_id"],
        "name":       doc["name"],
        "type":       doc["type"],
        "sort_order": doc["sort_order"],
        "is_active":  doc["is_active"],
    }


async def get_accounts(user_id: str) -> list:
    cursor = get_collection("budget_accounts").find(
        {"user_id": user_id, "is_active": True}
    ).sort("sort_order", 1)
    return [_fmt_account(d) async for d in cursor]


async def create_account(user_id: str, data: AccountCreate) -> dict:
    col = get_collection("budget_accounts")
    doc = {
        "user_id":    user_id,
        "name":       data.name,
        "type":       data.type,
        "sort_order": data.sort_order,
        "is_active":  True,
    }
    result = await col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _fmt_account(doc)


async def update_account(account_id: str, data: AccountUpdate) -> dict | None:
    col = get_collection("budget_accounts")
    update = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    if not update:
        return None
    await col.update_one({"_id": ObjectId(account_id)}, {"$set": update})
    doc = await col.find_one({"_id": ObjectId(account_id)})
    return _fmt_account(doc) if doc else None


async def delete_account(account_id: str) -> bool:
    result = await get_collection("budget_accounts").update_one(
        {"_id": ObjectId(account_id)},
        {"$set": {"is_active": False}},
    )
    return result.modified_count > 0


# ── Periods ───────────────────────────────────────────────────────────────────

def _fmt_period(doc: dict) -> dict:
    return {
        "id":         _id(doc),
        "user_id":    doc["user_id"],
        "start_date": doc["start_date"],
        "end_date":   doc.get("end_date"),
        "is_active":  doc["is_active"],
    }


async def get_periods(user_id: str) -> list:
    cursor = get_collection("budget_periods").find(
        {"user_id": user_id}
    ).sort("start_date", -1)
    return [_fmt_period(d) async for d in cursor]


async def get_active_period(user_id: str) -> dict | None:
    doc = await get_collection("budget_periods").find_one(
        {"user_id": user_id, "is_active": True}
    )
    return _fmt_period(doc) if doc else None


async def create_period(user_id: str, start_date: str) -> dict:
    periods  = get_collection("budget_periods")
    balances = get_collection("budget_balances")
    now      = datetime.now(timezone.utc)

    # Close current active period and compute end_date
    current = await periods.find_one({"user_id": user_id, "is_active": True})
    old_bal_map: dict[str, float] = {}

    if current:
        start_dt = datetime.fromisoformat(start_date)
        end_dt   = start_dt - timedelta(days=1)
        end_date = end_dt.strftime("%Y-%m-%d")

        await periods.update_one(
            {"_id": current["_id"]},
            {"$set": {"is_active": False, "end_date": end_date}},
        )

        # Collect final balances to carry over
        old_bals = await balances.find(
            {"user_id": user_id, "period_id": str(current["_id"])}
        ).to_list(length=1000)
        old_bal_map = {b["account_id"]: b["balance_current"] for b in old_bals}

    # Create new period
    new_doc = {
        "user_id":    user_id,
        "start_date": start_date,
        "end_date":   None,
        "is_active":  True,
        "created_at": now,
    }
    result = await periods.insert_one(new_doc)
    new_period_id = str(result.inserted_id)

    # Create balance records for every active account (carry over balances)
    accounts = await get_accounts(user_id)
    for acc in accounts:
        carried = old_bal_map.get(acc["id"], 0.0)
        await balances.insert_one({
            "user_id":         user_id,
            "account_id":      acc["id"],
            "period_id":       new_period_id,
            "balance_start":   carried,
            "balance_current": carried,
            "updated_at":      now.isoformat(),
        })

    new_doc["_id"] = result.inserted_id
    return _fmt_period(new_doc)


async def delete_period(user_id: str, period_id: str) -> dict | None:
    """Delete the active period and reactivate the previous one. Returns restored period."""
    periods   = get_collection("budget_periods")
    balances  = get_collection("budget_balances")
    income    = get_collection("budget_income")
    transfers = get_collection("budget_transfers")

    period = await periods.find_one({"_id": ObjectId(period_id), "user_id": user_id})
    if not period:
        return None

    # Delete all data for this period
    await balances.delete_many({"user_id": user_id, "period_id": period_id})
    await income.delete_many({"user_id": user_id, "period_id": period_id})
    await transfers.delete_many({"user_id": user_id, "period_id": period_id})
    await periods.delete_one({"_id": ObjectId(period_id)})

    # Restore previous period as active
    prev = await periods.find_one(
        {"user_id": user_id},
        sort=[("start_date", -1)],
    )
    if prev:
        await periods.update_one(
            {"_id": prev["_id"]},
            {"$set": {"is_active": True, "end_date": None}},
        )
        prev["is_active"] = True
        prev["end_date"]  = None
        return _fmt_period(prev)
    return None


# ── Balances ──────────────────────────────────────────────────────────────────

def _fmt_balance(doc: dict) -> dict:
    return {
        "id":              _id(doc),
        "account_id":      doc["account_id"],
        "period_id":       doc["period_id"],
        "balance_start":   doc["balance_start"],
        "balance_current": doc["balance_current"],
        "updated_at":      doc["updated_at"],
    }


async def get_balances(user_id: str, period_id: str) -> list:
    cursor = get_collection("budget_balances").find(
        {"user_id": user_id, "period_id": period_id}
    )
    return [_fmt_balance(d) async for d in cursor]


async def upsert_balance(user_id: str, period_id: str, data: BalanceSet) -> dict:
    col     = get_collection("budget_balances")
    now_str = datetime.now(timezone.utc).isoformat()
    query   = {"user_id": user_id, "period_id": period_id, "account_id": data.account_id}

    existing = await col.find_one(query)
    if existing:
        await col.update_one({"_id": existing["_id"]}, {"$set": {
            "balance_start":   data.balance_start,
            "balance_current": data.balance_current,
            "updated_at":      now_str,
        }})
        doc = await col.find_one({"_id": existing["_id"]})
    else:
        new_doc = {
            **query,
            "balance_start":   data.balance_start,
            "balance_current": data.balance_current,
            "updated_at":      now_str,
        }
        result  = await col.insert_one(new_doc)
        doc     = await col.find_one({"_id": result.inserted_id})

    return _fmt_balance(doc)


async def add_advance(user_id: str, period_id: str, data: AdvanceAdd) -> dict:
    col     = get_collection("budget_balances")
    now_str = datetime.now(timezone.utc).isoformat()
    query   = {"user_id": user_id, "period_id": period_id, "account_id": data.account_id}

    existing = await col.find_one(query)
    if existing:
        await col.update_one({"_id": existing["_id"]}, {
            "$inc": {"balance_start": data.amount},
            "$set": {"updated_at": now_str},
        })
        doc = await col.find_one({"_id": existing["_id"]})
    else:
        new_doc = {
            **query,
            "balance_start":   data.amount,
            "balance_current": 0.0,
            "updated_at":      now_str,
        }
        result = await col.insert_one(new_doc)
        doc    = await col.find_one({"_id": result.inserted_id})

    return _fmt_balance(doc)


# ── Income ────────────────────────────────────────────────────────────────────

def _fmt_income(doc: dict) -> dict:
    return {
        "id":        _id(doc),
        "user_id":   doc["user_id"],
        "period_id": doc["period_id"],
        "amount":    doc["amount"],
        "date":      doc["date"],
        "category":  doc["category"],
        "note":      doc.get("note", ""),
    }


async def get_income(user_id: str, period_id: str) -> list:
    cursor = get_collection("budget_income").find(
        {"user_id": user_id, "period_id": period_id}
    ).sort("date", -1)
    return [_fmt_income(d) async for d in cursor]


async def create_income(user_id: str, period_id: str, data: IncomeCreate) -> dict:
    col = get_collection("budget_income")
    doc = {
        "user_id":   user_id,
        "period_id": period_id,
        "amount":    data.amount,
        "date":      data.date,
        "category":  data.category,
        "note":      data.note,
    }
    result  = await col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _fmt_income(doc)


async def delete_income(income_id: str) -> bool:
    result = await get_collection("budget_income").delete_one(
        {"_id": ObjectId(income_id)}
    )
    return result.deleted_count > 0


# ── Transfers ─────────────────────────────────────────────────────────────────

def _fmt_transfer(doc: dict) -> dict:
    return {
        "id":              _id(doc),
        "user_id":         doc["user_id"],
        "period_id":       doc["period_id"],
        "from_account_id": doc["from_account_id"],
        "to_account_id":   doc["to_account_id"],
        "amount":          doc["amount"],
        "date":            doc["date"],
    }


async def get_transfers(user_id: str, period_id: str) -> list:
    cursor = get_collection("budget_transfers").find(
        {"user_id": user_id, "period_id": period_id}
    ).sort("date", -1)
    return [_fmt_transfer(d) async for d in cursor]


async def create_transfer(user_id: str, period_id: str, data: TransferCreate) -> dict:
    transfers = get_collection("budget_transfers")
    balances  = get_collection("budget_balances")
    now       = datetime.now(timezone.utc)
    now_str   = now.isoformat()

    doc = {
        "user_id":         user_id,
        "period_id":       period_id,
        "from_account_id": data.from_account_id,
        "to_account_id":   data.to_account_id,
        "amount":          data.amount,
        "date":            now.strftime("%Y-%m-%d"),
        "created_at":      now,
    }
    result = await transfers.insert_one(doc)
    doc["_id"] = result.inserted_id

    # Adjust balance_current for both accounts
    bal_query_base = {"user_id": user_id, "period_id": period_id}
    await balances.update_one(
        {**bal_query_base, "account_id": data.from_account_id},
        {"$inc": {"balance_current": -data.amount}, "$set": {"updated_at": now_str}},
    )
    await balances.update_one(
        {**bal_query_base, "account_id": data.to_account_id},
        {"$inc": {"balance_current": data.amount}, "$set": {"updated_at": now_str}},
    )

    return _fmt_transfer(doc)


async def delete_transfer(transfer_id: str) -> bool:
    transfers = get_collection("budget_transfers")
    balances  = get_collection("budget_balances")

    transfer = await transfers.find_one({"_id": ObjectId(transfer_id)})
    if not transfer:
        return False

    now_str       = datetime.now(timezone.utc).isoformat()
    bal_query_base = {
        "user_id":   transfer["user_id"],
        "period_id": transfer["period_id"],
    }

    # Revert balance changes
    await balances.update_one(
        {**bal_query_base, "account_id": transfer["from_account_id"]},
        {"$inc": {"balance_current": transfer["amount"]}, "$set": {"updated_at": now_str}},
    )
    await balances.update_one(
        {**bal_query_base, "account_id": transfer["to_account_id"]},
        {"$inc": {"balance_current": -transfer["amount"]}, "$set": {"updated_at": now_str}},
    )

    result = await transfers.delete_one({"_id": ObjectId(transfer_id)})
    return result.deleted_count > 0
