import sys
import os
import logging
from typing import Optional, List
from dotenv import load_dotenv

# --- PATH FIX: Add project root to sys.path to allow 'src' imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models import InvoiceData, InvoiceItem
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# Load env vars early
load_dotenv()

logger = logging.getLogger(__name__)

def extract_invoice_data_llm(file_path: str) -> InvoiceData:
    """
    Extracts structured invoice data from a PDF file using Azure Document Intelligence.
    Model ID: PI_Extraction
    """
    endpoint = os.getenv("AZURE_FORM_ENDPOINT")
    key = os.getenv("AZURE_FORM_KEY")
    model_id = "PI_Extraction"

    if not endpoint or not key:
        raise ValueError("Azure credentials (AZURE_FORM_ENDPOINT, AZURE_FORM_KEY) are missing.")

    logger.info(f"Processing PDF (Azure Doc Intelligence): {file_path}")

    try:
        client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
        
        with open(file_path, "rb") as f:
            poller = client.begin_analyze_document(
                model_id=model_id, 
                body=f,
                content_type="application/pdf"
            )
        
        result = poller.result()
        
        if not result.documents:
            raise ValueError("No documents analyzed by Azure.")

        doc = result.documents[0]
        fields = doc.fields

        # Helper to get string value safely
        def get_str(field_name):
            f = fields.get(field_name)
            if f:
                return f.value_string if f.value_string else f.content
            return None

        # Helper for float
        def get_float(field_name, text_value=None):
            val_str = text_value
            if not val_str:
                f = fields.get(field_name)
                if not f: return 0.0
                val_str = f.value_string if f.value_string else f.content
            
            if not val_str: return 0.0
            
            # Clean string
            val_str = val_str.replace(',', '').replace('$', '').strip()
            try:
                return float(val_str)
            except:
                return 0.0

        # Extract Fields
        supplier = get_str("supplier")
        supplier_inv_no = get_str("supplier_inv_no")
        supplier_inv_date = get_str("supplier_inv_date") # You might want to normalize date format if needed
        due_date = get_str("due_date")
        currency = get_str("currency") or "USD"
        
        # Extract Total Amount (try common field names for custom models)
        total_amount = get_float("total_amount")
        if total_amount == 0.0:
             total_amount = get_float("InvoiceTotal") # Fallback to prebuilt model name
        
        # Missing fields in model - explicit None
        job_no = None
        customer_name = None 
        
        # Line Items
        items_data = []
        line_items_field = fields.get("line_items")
        if line_items_field and line_items_field.value_array:
            for item in line_items_field.value_array:
                # item is a DocumentField, likely type 'object', so value_object is the dict
                if item.value_object:
                    item_fields = item.value_object
                    
                    # Extract item properties
                    desc_f = item_fields.get("charge_description")
                    qty_f = item_fields.get("Qty")
                    amt_f = item_fields.get("Amount")
                    
                    desc = desc_f.content if desc_f else "Unknown"
                    
                    # Clean number strings
                    qty_content = qty_f.content if (qty_f and qty_f.content) else "1"
                    qty_str = qty_content.replace(',', '').strip()
                    try:
                        qty = float(qty_str) if qty_str else 1.0
                    except:
                        qty = 1.0

                    amt_content = amt_f.content if (amt_f and amt_f.content) else "0"
                    amt_str = amt_content.replace(',', '').replace('$', '').strip()
                    try:
                        amount = float(amt_str) if amt_str else 0.0
                    except:
                        amount = 0.0
                        
                    # Calculate unit price
                    unit_price = amount / qty if qty != 0 else 0.0

                    items_data.append(InvoiceItem(
                        description=desc,
                        quantity=qty,
                        unit_price=unit_price,
                        amount=amount
                    ))

        extracted_data = InvoiceData(
            supplier=supplier,
            supplier_inv_no=supplier_inv_no,
            supplier_inv_date=supplier_inv_date,
            due_date=due_date,
            job_no=job_no,
            currency=currency,
            total_amount=total_amount,
            customer_name=customer_name,
            items=items_data
        )

        logger.info(f"Extraction successful. Supplier: {extracted_data.supplier}, Inv No: {extracted_data.supplier_inv_no}")
        return extracted_data

    except Exception as e:
        logger.error(f"Azure extraction failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    sample_pdf = r"C:\Users\Thameem\Desktop\Thammi\Zybo\invoice-matcher-service\PI\data\sample_invoices\3 A2S Logistics.pdf"
    
    if len(sys.argv) > 1:
        sample_pdf = sys.argv[1]
        
    if not os.path.exists(sample_pdf):
        print(f"Error: File not found at {sample_pdf}")
    else:
        print(f"Running extraction on: {sample_pdf}")
        try:
            result = extract_invoice_data_llm(sample_pdf)
            print("\n--- Extracted Data ---")
            print(result.model_dump_json(indent=2))
        except Exception as e:
            print(f"Extraction failed: {e}")