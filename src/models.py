from typing import List, Optional
from pydantic import BaseModel, Field

class InvoiceItem(BaseModel):
    description: str = Field(..., description="Description of the item or service")
    quantity: float = Field(..., description="Quantity of the item")
    unit_price: float = Field(..., description="Unit price of the item")
    amount: float = Field(..., description="Total amount for the line item")

class InvoiceData(BaseModel):
    invoice_number: str = Field(..., description="The unique invoice identifier")
    invoice_date: str = Field(..., description="Date of the invoice")
    customer_name: str = Field(..., description="Name of the customer or client")
    total_amount: float = Field(..., description="Total amount of the invoice")
    currency: str = Field(default="USD", description="Currency code (e.g., USD, EUR)")
    items: List[InvoiceItem] = Field(default_factory=list, description="List of line items in the invoice")

class FieldComparison(BaseModel):
    status: str = Field(..., description="'MATCH' or 'MISMATCH'")
    reasoning: str = Field(..., description="Explanation for the match or mismatch")

class ComparisonResult(BaseModel):
    status: str = Field(..., description="'MATCH' or 'MISMATCH'")
    analysis: str = Field(..., description="Overall analysis of the comparison")
    field_level_comparison: dict[str, str] = Field(..., description="Key-value pairs of field names and their match status/notes")
