"""
Database Schemas for the Flash Sales platform (La Réunion)

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name. Example: Brand -> "brand"

These models are used for validation at the edges of the API and document the
shape of the data stored in MongoDB.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# Users and marketing
class Subscriber(BaseModel):
    email: EmailStr = Field(..., description="Subscriber email")
    first_name: Optional[str] = Field(None, description="Optional first name")
    sale_event_id: Optional[str] = Field(None, description="Event the user wants to be notified about")
    source: Optional[str] = Field("landing", description="Acquisition source/tag")
    accepted_marketing: bool = Field(True, description="Consented to receive communications")

# Catalog
class Brand(BaseModel):
    name: str = Field(..., description="Brand name")
    description: Optional[str] = Field(None, description="Short brand description/story")
    logo_url: Optional[str] = Field(None, description="Brand logo URL")
    origin: Optional[str] = Field(None, description="Origin e.g. Réunion, France")
    website: Optional[str] = Field(None, description="Website")

class SaleEvent(BaseModel):
    title: str = Field(..., description="Campaign title")
    subtitle: Optional[str] = Field(None, description="Short teaser line")
    start_at: datetime = Field(..., description="UTC start datetime")
    end_at: datetime = Field(..., description="UTC end datetime")
    banner_url: Optional[str] = Field(None, description="Hero/banner image URL")
    brand_ids: List[str] = Field(default_factory=list, description="Related brand ids")
    categories: List[str] = Field(default_factory=list, description="Tags/categories (mode, terroir, etc.)")
    status: str = Field("scheduled", description="scheduled|live|ended")

class SaleProduct(BaseModel):
    sale_event_id: str = Field(..., description="Associated sale event id")
    brand_id: Optional[str] = Field(None, description="Brand id")
    title: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    images: List[str] = Field(default_factory=list, description="Image URLs")
    price_original: float = Field(..., ge=0)
    price_sale: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    sku: Optional[str] = Field(None)
    attributes: Optional[dict] = Field(default_factory=dict)

class Reservation(BaseModel):
    sale_event_id: str = Field(...)
    product_id: str = Field(...)
    email: EmailStr = Field(...)
    quantity: int = Field(1, ge=1, le=10)
    status: str = Field("held", description="held|confirmed|cancelled")

# Example - keep for reference
class User(BaseModel):
    name: str
    email: EmailStr
    address: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

