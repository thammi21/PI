from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# --- Extraction Models (Existing) ---
class InvoiceItem(BaseModel):
    description: str = Field(..., description="The name of the service or charge (e.g., 'Ocean Freight', 'Terminal Handling')")
    quantity: Optional[float] = Field(default=1.0, description="The number of units")
    unit_price: Optional[float] = Field(default=None, description="The cost per unit")
    amount: float = Field(..., description="The total line amount (Quantity × Unit Price)")

class InvoiceData(BaseModel):
    # Header Information
    supplier: Optional[str] = Field(default=None, description="The company issuing the invoice")
    supplier_inv_no: Optional[str] = Field(default=None, description="The unique invoice identifier (e.g., Invoice No, Inv #)")
    supplier_inv_date: Optional[str] = Field(default=None, description="Date the invoice was issued (YYYY-MM-DD)")
    due_date: Optional[str] = Field(default=None, description="Date payment is due (YYYY-MM-DD)")
    job_no: Optional[str] = Field(default=None, description="Internal job tracking number (e.g., Job No, Ref)")
    currency: str = Field(default="USD", description="Currency code (e.g., USD, EUR)")
    
    # Customer Logic
    customer_name: Optional[str] = Field(default=None, description="The entity responsible for paying the invoice (Bill To)")

    # Line Items
    items: List[InvoiceItem] = Field(default_factory=list, description="List of billable line items")

# --- Internal Database Models (New) ---
class InternalInvoiceData(BaseModel):
    """
    Represents the 'Truth' data coming from your internal database via API.
    Matches the JSON structure provided by the Integration Team.
    """
    invoice_number: str = Field(..., alias="invoice_number") # Using alias to match JSON key
    supplier_name: str
    invoice_date: Optional[str] = None
    total_amount: float
    currency: str
    job_reference: Optional[str] = None
    status: Optional[str] = "Pending"
    
    # Optional: If the API returns line items too
    line_items: List[Dict[str, Any]] = Field(default_factory=list)

class FieldComparison(BaseModel):
    status: str = Field(..., description="'MATCH' or 'MISMATCH'")
    reasoning: str = Field(..., description="Explanation for the match or mismatch")

class ComparisonResult(BaseModel):
    status: str = Field(..., description="'MATCH' or 'MISMATCH'")
    analysis: str = Field(..., description="Overall analysis of the comparison")
    field_level_comparison: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs of field names and their match status/notes")