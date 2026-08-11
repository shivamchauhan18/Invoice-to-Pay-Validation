from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


class InvoiceItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[str] = None
    unit_price: Optional[str] = None
    amount: Optional[str] = None


class Invoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    vendor_name: Optional[str] = None
    po_number: Optional[str] = None
    currency: Optional[str] = None

    subtotal: Optional[str] = None
    tax: Optional[str] = None
    total: Optional[str] = None

    items: List[InvoiceItem] = []


class POItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[str] = None
    unit_price: Optional[str] = None
    amount: Optional[str] = None


class PurchaseOrder(BaseModel):
    po_number: Optional[str] = None
    po_date: Optional[str] = None
    vendor_name: Optional[str] = None
    currency: Optional[str] = None

    total: Optional[str] = None

    items: List[POItem] = []


class ValidationResult(BaseModel):
    status: Literal["MATCH", "MISMATCH", "REVIEW"]

    html_table: str