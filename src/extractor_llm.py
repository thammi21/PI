import sys
import os
import time
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# --- PATH FIX: Add project root to sys.path to allow 'src' imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import InvoiceData

# Load env vars early
load_dotenv()

logger = logging.getLogger(__name__)

def extract_invoice_data_llm(file_path: str) -> InvoiceData:
    """
    Extracts structured invoice data from a PDF file using Gemini's native
    multimodal capabilities (File API). This performs 'Visual Extraction' 
    which is equivalent to, and often better than, traditional OCR.
    
    It supports scanned PDFs and images associated with the PDF.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    # Configure the Gemini SDK
    genai.configure(api_key=api_key)

    logger.info(f"Uploading {file_path} to Gemini for processing...")
    
    try:
        # Upload the file to Google's GenAI File API
        # This allows Gemini to 'view' the PDF directly.
        sample_file = genai.upload_file(path=file_path, display_name="Invoice Document")
        
        # Wait for the file to be processed (usually very fast)
        while sample_file.state.name == "PROCESSING":
            time.sleep(1)
            sample_file = genai.get_file(sample_file.name)
            
        if sample_file.state.name == "FAILED":
            raise ValueError(f"File upload failed with state: {sample_file.state.name}")
            
        logger.info("File processed successfully. invoking Gemini 2.0 Flash...")

        # Initialize the model
        # Using gemini-2.0-flash as per available models
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0,
                "response_mime_type": "application/json",
                "response_schema": InvoiceData
            }
        )

        prompt = """You are an expert data extraction assistant specialized in Logistics and Freight Forwarding invoices.

    Your task is to analyze the provided document and extract specific fields into a structured JSON format.

    Strictly extract ONLY the following fields. If a field is not found, return null (None).

    EXTRACTION RULES:

    1. Header Information:
    - Supplier: Identify the full legal name of the company issuing the invoice. 
      * Note regarding LOGOS: Logos often only show a short name or acronym. Look for the FULL name, often found in text format at the very top of the document, above the main address blocks, or in the footer.
      * You can search if the full name is available by using the name explicitly found in the logo.
      * Do NOT use the logo text if a more complete legal name is available nearby.
      * Do not confuse this with the "Shipper".
    - Supplier Inv No: Look for labels like "Invoice No", "Inv #", "Tax Invoice No", or "Bill No".
    - Supplier Inv Date: The date the invoice was issued. Standardize to YYYY-MM-DD format if possible.
    - Due Date: The date payment is due. Look for explicit headers like "Due Date", "Payment Due", or "Maturity Date". 
      * CRITICAL: Do NOT confuse this with the "Invoice Date" or "Date". 
      * If a date is located near the "Supplier Inv No" and is NOT explicitly labeled "Due Date", it is likely the Invoice Date. Do NOT extract it as Due Date.
      * If no specific Due Date is found, return null. Standardize to YYYY-MM-DD.
    - Job No: Look for "Job No", "File Ref", "Our Ref", "Booking Ref", or "Job Reference". This is the internal tracking number for the shipment.
    - Currency: Identify the currency code (e.g., USD, EUR, AED, GBP) used for the totals.
    - Total Amount: The final invoice total including all taxes, VAT, and charges. This is usually found at the bottom right of the page properly labeled as "Total", "Grand Total", or "Invoice Total". Check for the largest amount on the page that matches the sum of line items.

    2. Customer (Bill To) Logic:
    - Customer Name: Identify the entity responsible for paying the invoice.
    - Heuristics:
        * Look specifically for the "Bill To" section.
        * Look for "To:" followed by a company name.
        * Look for the field 'Customer'.
        * If no explicit label exists, look for a company address block located on the right-hand side of the header (distinct from the Supplier on the left/center).
        * Critical: Do not confuse the "Customer" with the "Consignee" or "Shipper". If a field says "Consignee", ignore it for this specific field unless it is explicitly inside the "Bill To" box.

    3. Line Items Table:
    Extract all billable items into an array called line_items.
    For each item, extract:
    - description: The name of the service or charge (e.g., "Ocean Freight", "Terminal Handling").
    - quantity: The number of units (if blank, default to 1).
    - unit_price: The cost per unit.
    - amount: The total line amount (Quantity × Unit Price).

    Return the output as valid JSON only. Do not include markdown formatting.
    """

        # Generate content using the uploaded file and the prompt
        response = model.generate_content([sample_file, prompt])

        # Validate and parse the response into our Pydantic model
        if not response.text:
             raise ValueError("Empty response from Gemini.")
             
        result = InvoiceData.model_validate_json(response.text)
        
        logger.info(f"Extraction successful. Invoice Number: {result.supplier_inv_no}")
        
        # Clean up: Delete the uploaded file to avoid clutter in the cloud storage
        # (Optional but recommended for privacy/hygiene)
        try:
            genai.delete_file(sample_file.name)
        except Exception:
            pass # Non-critical if delete fails

        return result

    except Exception as e:
        logger.error(f"Gemini Native extraction failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    sample_pdf = r"C:\Users\Thameem\Desktop\Thammi\Zybo\invoice-matcher-service\PI\data\sample_invoices\3 A2S Logistics.pdf"
    
    if len(sys.argv) > 1:
        sample_pdf = sys.argv[1]
        
    if not os.path.exists(sample_pdf):
        print(f"Error: File not found at {sample_pdf}")
    else:
        print(f"Running OCR-enabled extraction on: {sample_pdf}")
        # Fix for Windows console encoding
        if sys.stdout.encoding != 'utf-8':
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass

        try:
            result = extract_invoice_data_llm(sample_pdf)
            print("\n--- Extracted Data ---")
            print(result.model_dump_json(indent=2))
        except Exception as e:
            print(f"Extraction failed: {e}")
