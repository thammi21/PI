from jinja2 import Environment, FileSystemLoader
from fpdf import FPDF
import os
import logging
from src.models import InvoiceData

logger = logging.getLogger(__name__)

def generate_verified_invoice(data: InvoiceData, output_path: str):
    """
    Generates a verified invoice PDF using FPDF.
    """
    try:
        logger.info(f"Generating verified invoice at {output_path}")
        
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "VERIFIED INVOICE", ln=True, align="C")
        pdf.ln(10)
        
        # Invoice Details
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Invoice Number: {data.invoice_number}", ln=True)
        pdf.cell(0, 10, f"Date: {data.invoice_date}", ln=True)
        pdf.cell(0, 10, f"Customer: {data.customer_name}", ln=True)
        pdf.ln(10)
        
        # Table Header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 10, "Description", border=1)
        pdf.cell(30, 10, "Quantity", border=1)
        pdf.cell(40, 10, "Unit Price", border=1)
        pdf.cell(40, 10, "Amount", border=1)
        pdf.ln()
        
        # Table Rows
        pdf.set_font("Arial", "", 12)
        for item in data.items:
            pdf.cell(80, 10, str(item.description), border=1)
            pdf.cell(30, 10, str(item.quantity), border=1)
            pdf.cell(40, 10, f"{item.unit_price:.2f}", border=1)
            pdf.cell(40, 10, f"{item.amount:.2f}", border=1)
            pdf.ln()
            
        # Total
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(150, 10, "Total Amount:", align="R")
        pdf.cell(40, 10, f"{data.total_amount:.2f} {data.currency}", border=1, align="C")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        pdf.output(output_path)
        logger.info("PDF generation successful.")
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise
