from fpdf import FPDF
import os

def create_sample_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    content = [
        "INVOICE",
        "",
        "Invoice Number: INV-2023-001",
        "Date: October 25, 2023",
        "Bill To: Acme Corp",
        "",
        "Description             Quantity    Unit Price    Amount",
        "--------------------------------------------------------",
        "Consulting Services     10          150.00        1500.00",
        "",
        "Total: $1,500.00"
    ]
    
    for line in content:
        pdf.cell(200, 10, txt=line, ln=True)
        
    os.makedirs("data", exist_ok=True)
    output_path = "data/sample_invoice.pdf"
    pdf.output(output_path)
    print(f"Sample invoice created at {output_path}")

if __name__ == "__main__":
    create_sample_pdf()
