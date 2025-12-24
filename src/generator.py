from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
import io
import os
import logging
from src.models import InvoiceData

logger = logging.getLogger(__name__)

def generate_verified_invoice(data: InvoiceData, output_path: str):
    """
    Generates a verified invoice PDF using the VoucherPrintingBatch template.
    """
    try:
        logger.info(f"Generating verified invoice at {output_path}")
        
        # Template path
        template_path = "data/VoucherPrintingBatch.pdf"
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found at {template_path}")

        # Create an overlay PDF
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        # Font settings
        can.setFont("Helvetica", 9)
        
        # --- Masking Old Data (White Rectangles) ---
        # Adjust these coordinates and sizes based on the template layout
        can.setFillColorRGB(1, 1, 1) # White
        can.setStrokeColorRGB(1, 1, 1)
        
        # Mask Header Info
        can.rect(15, 655, 80, 15, fill=1) # Voucher No
        can.rect(100, 655, 80, 15, fill=1) # Voucher Date
        can.rect(100, 620, 40, 15, fill=1) # Currency
        can.rect(240, 620, 150, 15, fill=1) # Payable To
        can.rect(410, 620, 150, 15, fill=1) # Supplier Invoice No
        
        # Mask Totals
        can.rect(480, 360, 80, 15, fill=1) # Sub Total
        can.rect(480, 340, 80, 15, fill=1) # Tax Total
        can.rect(480, 325, 80, 15, fill=1) # Total
        can.rect(480, 310, 80, 15, fill=1) # Amount Due
        can.rect(430, 290, 150, 15, fill=1) # In Words line 1
        can.rect(430, 280, 150, 10, fill=1) # In Words line 2
        can.rect(430, 270, 150, 10, fill=1) # In Words line 3
        
        # Mask Shipper and Consignee Blocks (Name + Address)
        # Shipper: x=64, y=588. Address lines below.
        can.rect(60, 535, 230, 65, fill=1) 
        # Consignee: x=360, y=588. Address lines below.
        can.rect(355, 535, 230, 65, fill=1)

        # Mask Table Rows (Masking a large block for the table body)
        # Assuming table starts around y=490 and goes down
        can.rect(20, 400, 550, 100, fill=1) 

        # --- Drawing New Data ---
        can.setFillColorRGB(0, 0, 0) # Black
        
        # Header Data
        # can.drawString(17, 658, str(data.invoice_number)) # Moved to Supplier Invoice No
        # can.drawString(110, 658, str(data.invoice_date)) # Moved to Supplier Invoice No
        can.drawString(110, 624, str(data.currency))
        can.drawString(243, 624, str(data.customer_name))
        
        # Supplier Invoice No & Date
        supplier_ref = f"{data.invoice_number} / {data.invoice_date}"
        can.drawString(418, 624, supplier_ref)
        
        # Shipper and Consignee
        if data.shipper:
            can.drawString(65, 588, str(data.shipper))
        if data.consignee:
            can.drawString(360, 588, str(data.consignee))
        
        # Table Data
        y_start = 487
        row_height = 15
        y = y_start
        
        for i, item in enumerate(data.items):
            if y < 400: # Stop if we run out of space
                break
            
            can.drawString(28, y, str(i + 1))
            can.drawString(47, y, str(item.description)[:40]) # Truncate if too long
            # can.drawString(193, y, "Job No") 
            can.drawString(457, y, f"{item.amount:.2f}")
            # can.drawString(549, y, "0.00") # Credit
            
            y -= row_height
            
        # Totals
        can.drawString(490, 362, f"{data.currency} {data.total_amount:.2f}") # Sub Total
        can.drawString(490, 345, f"{data.currency} 0.00") # Tax Total
        can.drawString(490, 328, f"{data.currency} {data.total_amount:.2f}") # Total
        can.drawString(490, 311, f"{data.currency} {data.total_amount:.2f}") # Amount Due
        
        can.save()
        
        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)
        
        # Read the existing PDF
        existing_pdf = PdfReader(open(template_path, "rb"))
        output = PdfWriter()
        
        # Merge
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the output
        with open(output_path, "wb") as outputStream:
            output.write(outputStream)
            
        logger.info("PDF generation successful.")

    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise
