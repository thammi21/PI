from src.generator import generate_verified_invoice
from src.models import InvoiceData, InvoiceItem
from datetime import date

def test_generation():
    data = InvoiceData(
        invoice_number="INV-2024-001",
        invoice_date="2024-12-04", # Changed to string as per model definition
        currency="USD",
        total_amount=1500.00,
        customer_name="TEST CUSTOMER",
        shipper="TEST SHIPPER\nAddress Line 1",
        consignee="TEST CONSIGNEE\nAddress Line 1",
        items=[
            InvoiceItem(description="Test Item 1", amount=500.00),
            InvoiceItem(description="Test Item 2", amount=1000.00)
        ]
    )
    
    output_path = "output/test_layout.pdf"
    generate_verified_invoice(data, output_path)
    print(f"Generated invoice at {output_path}")

if __name__ == "__main__":
    test_generation()
