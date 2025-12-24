from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import logging
from dotenv import load_dotenv

from src.extractor_azure import extract_invoice_data_llm
from src.crm_tool import fetch_crm_data
from src.comparator import compare_invoice_data
from src.generator import generate_verified_invoice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

load_dotenv()

app = FastAPI(title="Invoice Matcher Service")

@app.post("/match")
async def match_invoice(file: UploadFile = File(...)):
    """
    Endpoint to process an invoice PDF and match it against CRM data.
    """
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Save uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Processing file: {temp_file_path}")

        # Step 1: Extract Data (Azure handles loading)
        try:
            logger.info("Step 1: Extracting Structured Data using Gemini LLM...")
            extracted_data = extract_invoice_data_llm(temp_file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to extract data: {str(e)}")

        # Step 3: Fetch CRM Data
        crm_data = fetch_crm_data(extracted_data.job_reference)
        if not crm_data:
            return JSONResponse(content={
                "status": "MISMATCH",
                "analysis": f"Job Reference {extracted_data.job_reference} not found in CRM.",
                "differences": {"job_reference": "Not Found"}
            })

        # Step 4: AI Comparison (Hybrid: Fuzzy + LLM)
        comparison_result = compare_invoice_data(extracted_data, crm_data)

        # Step 5: Prepare Response
        response_data = {
            "status": comparison_result.status,
            "analysis": comparison_result.analysis,
            "field_level_comparison": comparison_result.field_level_comparison,
            "extracted": extracted_data.model_dump(),
            "crm": crm_data
        }

        # Generate Verified Invoice if MATCH
        if comparison_result.status == "MATCH":
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_pdf_path = os.path.join(output_dir, f"verified_{file.filename}")
            try:
                generate_verified_invoice(extracted_data, output_pdf_path)
                response_data["verified_invoice_path"] = output_pdf_path
            except Exception as e:
                logger.error(f"Failed to generate verified invoice: {e}")
                response_data["verified_invoice_error"] = str(e)

        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
