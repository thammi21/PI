from src.generator import generate_verified_invoice
from src.models import InvoiceData, InvoiceItem
import os

data = InvoiceData(
    invoice_number="INV-TEST-001",
    invoice_date="2025-11-27",
    customer_name="Test Customer Ltd",
    job_reference="JOB-123",
    currency="USD",
    total_amount=1234.56,
    items=[
        InvoiceItem(description="Test Item 1", quantity=1, unit_price=1000.00, amount=1000.00),
        InvoiceItem(description="Test Item 2", quantity=2, unit_price=117.28, amount=234.56)
    ]
)

output_path = "output/verified_invoice_test.pdf"
if os.path.exists(output_path):
    os.remove(output_path)

try:
    generate_verified_invoice(data, output_path)
    print(f"Successfully generated {output_path}")
except Exception as e:
    print(f"Failed to generate invoice: {e}")
