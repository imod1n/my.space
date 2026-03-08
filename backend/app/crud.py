from bson import ObjectId
from .database import get_collection


def _fmt(doc) -> dict:
    doc["id"] = str(doc.pop("_id"))
    doc.setdefault("object_name", "")
    doc.setdefault("period", doc.get("date", "")[:7])
    doc.setdefault("note", "")
    return doc


async def create_payment(data) -> dict:
    col = get_collection("payments")
    doc = data.model_dump()
    result = await col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _fmt(doc)


async def get_payments(limit: int = 200) -> list:
    col = get_collection("payments")
    cursor = col.find().sort("date", -1).limit(limit)
    return [_fmt(d) async for d in cursor]


async def delete_payment(payment_id: str) -> bool:
    col = get_collection("payments")
    result = await col.delete_one({"_id": ObjectId(payment_id)})
    return result.deleted_count == 1


async def update_payment(payment_id: str, data) -> dict | None:
    col = get_collection("payments")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        return None
    result = await col.find_one_and_update(
        {"_id": ObjectId(payment_id)},
        {"$set": update_data},
        return_document=True,
    )
    if result is None:
        return None
    return _fmt(result)


async def get_stats_by_period(period: str) -> dict:
    col = get_collection("payments")
    cursor = col.find({"period": period})
    docs = [_fmt(d) async for d in cursor]

    total = sum(d["amount"] for d in docs)

    by_category: dict[str, float] = {}
    by_object: dict[str, list] = {}

    for d in docs:
        by_category[d["category"]] = by_category.get(d["category"], 0) + d["amount"]

        obj = d["object_name"] or "Без объекта"
        if obj not in by_object:
            by_object[obj] = []
        by_object[obj].append({
            "id":       d["id"],
            "category": d["category"],
            "date":     d["date"],
            "period":   d["period"],
            "amount":   d["amount"],
            "note":     d["note"],
        })

    return {
        "period":      period,
        "total":       total,
        "by_category": by_category,
        "by_object":   by_object,
    }


async def delete_all_payments() -> int:
    col = get_collection("payments")
    result = await col.delete_many({})
    return result.deleted_count


async def get_stats_history(months: int = 6) -> list:
    col = get_collection("payments")
    pipeline = [
        {"$group": {
            "_id":   "$period",
            "total": {"$sum": "$amount"},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id": -1}},
        {"$limit": months},
        {"$project": {"period": "$_id", "total": 1, "count": 1, "_id": 0}},
    ]
    cursor = col.aggregate(pipeline)
    return [d async for d in cursor]
