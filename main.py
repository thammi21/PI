import os
import logging
import argparse
import json
from dotenv import load_dotenv

# Import components
from src.loader import load_invoice_pdf
from src.extractor import extract_invoice_data
from src.crm_tool import fetch_crm_data
from src.comparator import compare_invoice_data
from src.generator import generate_verified_invoice

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MainPipeline")

def main(pdf_path: str):
    load_dotenv()
    
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return

    logger.info("=== Starting Invoice Processing Pipeline ===")

    # Step 1: Load Invoice
    logger.info("Step 1: Loading Invoice PDF...")
    try:
        invoice_text = load_invoice_pdf(pdf_path)
    except Exception as e:
        logger.error(f"Failed to load PDF: {e}")
        return

    # Step 2: Extract Data
    logger.info("Step 2: Extracting Structured Data...")
    try:
        extracted_data = extract_invoice_data(invoice_text)
        logger.info(f"Extracted Data: {extracted_data.model_dump_json(indent=2)}")
    except Exception as e:
        logger.error(f"Failed to extract data: {e}")
        return

    # Step 3: Fetch CRM Data
    logger.info("Step 3: Fetching CRM Data...")
    crm_data = fetch_crm_data(extracted_data.invoice_number)
    if not crm_data:
        logger.warning("Invoice not found in CRM. Stopping pipeline.")
        print(json.dumps({
            "status": "MISMATCH",
            "analysis": "Invoice number not found in CRM.",
            "differences": {"invoice_number": "Not Found"}
        }, indent=2))
        return
    logger.info(f"CRM Data: {json.dumps(crm_data, indent=2, default=str)}")

    # Step 4: AI Comparison
    logger.info("Step 4: Performing AI Comparison...")
    comparison_result = compare_invoice_data(extracted_data, crm_data)
    logger.info(f"Comparison Result: {comparison_result.model_dump_json(indent=2)}")

    # Step 5 & 6: Generate Output
    output_result = {
        "status": comparison_result.status,
        "analysis": comparison_result.analysis,
        "field_level_comparison": comparison_result.field_level_comparison,
        "extracted": extracted_data.model_dump(),
        "crm": crm_data
    }

    if comparison_result.status == "MATCH":
        logger.info("Step 5: Generating Verified Invoice...")
        output_pdf_path = "output/verified_invoice.pdf"
        try:
            generate_verified_invoice(extracted_data, output_pdf_path)
            output_result["verified_invoice_path"] = output_pdf_path
            logger.info(f"Verified invoice saved to {output_pdf_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
    else:
        logger.info("Status is MISMATCH. Skipping PDF generation.")

    # Final Output
    print("\n=== FINAL OUTPUT ===\n")
    print(json.dumps(output_result, indent=2, default=str))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Invoice Processing Pipeline")
    parser.add_argument("pdf_path", help="Path to the invoice PDF file")
    args = parser.parse_args()
    
    main(args.pdf_path)
