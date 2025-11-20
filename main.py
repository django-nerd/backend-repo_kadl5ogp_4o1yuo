import os
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from database import db, create_document, get_documents
from schemas import Subscriber, SaleEvent, SaleProduct

app = FastAPI(title="RunFlash API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "RunFlash backend ready"}

# ----- Health & Schema -----
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "Unknown"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:120]}"

    return response

# ----- Public API: content for landing/MVP -----
class EventCard(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    banner_url: Optional[str] = None
    start_at: datetime
    end_at: datetime
    status: str
    categories: List[str] = []

@app.get("/api/events", response_model=List[EventCard])
def list_events():
    """Return upcoming and live events (basic projection)"""
    now = datetime.now(timezone.utc)
    docs = get_documents("saleevent", {"end_at": {"$gte": now}}, limit=50)
    events: List[EventCard] = []
    for d in docs:
        events.append(EventCard(
            id=str(d.get("_id")),
            title=d.get("title", ""),
            subtitle=d.get("subtitle"),
            banner_url=d.get("banner_url"),
            start_at=d.get("start_at", now),
            end_at=d.get("end_at", now),
            status=d.get("status", "scheduled"),
            categories=d.get("categories", []),
        ))
    return events

class SubscribePayload(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    sale_event_id: Optional[str] = None
    source: Optional[str] = "landing"
    accepted_marketing: bool = True

@app.post("/api/subscribe")
def subscribe(payload: SubscribePayload):
    sub = Subscriber(**payload.model_dump())
    try:
        inserted_id = create_document("subscriber", sub)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Products for an event (MVP read-only)
class ProductCard(BaseModel):
    id: str
    title: str
    price_original: float
    price_sale: float
    image: Optional[str] = None
    stock: int

@app.get("/api/events/{event_id}/products", response_model=List[ProductCard])
def list_event_products(event_id: str):
    docs = get_documents("saleproduct", {"sale_event_id": event_id}, limit=200)
    items: List[ProductCard] = []
    for d in docs:
        items.append(ProductCard(
            id=str(d.get("_id")),
            title=d.get("title", ""),
            price_original=float(d.get("price_original", 0)),
            price_sale=float(d.get("price_sale", 0)),
            image=(d.get("images") or [None])[0],
            stock=int(d.get("stock", 0)),
        ))
    return items

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
