from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.models import ComparisonResult, InvoiceData
import logging
import os
import json

logger = logging.getLogger(__name__)

def compare_invoice_data(extracted: InvoiceData, crm_data: dict) -> ComparisonResult:
    """
    Compares extracted invoice data with CRM data using an LLM for reasoning.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0, google_api_key=api_key)
    structured_llm = llm.with_structured_output(ComparisonResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert financial auditor. Your task is to compare data extracted from an invoice against the official CRM record.
        
        RULES:
        1. Perform a deep semantic comparison.
        2. DO NOT use fuzzy matching algorithms (like Levenshtein). Use your reasoning capabilities.
        3. Understand date formats (e.g., '2023-10-25' vs 'Oct 25, 2023' are MATCHES).
        4. Understand currency formats (e.g., '$1,500.00' vs '1500' are MATCHES).
        5. Understand naming differences (e.g., 'Acme Corp' vs 'Acme Corporation' are MATCHES).
        6. Detect missing or mismatched fields.
        7. If there is a significant discrepancy (e.g. different amount, different invoice number), mark as MISMATCH.
        8. Return the result in the specified structure.
        """),
        ("user", """
        Extracted Data:
        {extracted_json}
        
        CRM Data:
        {crm_json}
        
        Compare them and provide the status and analysis.
        """)
    ])

    chain = prompt | structured_llm

    logger.info("Invoking LLM for data comparison...")
    try:
        # Convert models/dicts to JSON strings for the prompt
        extracted_json = extracted.model_dump_json()
        crm_json = json.dumps(crm_data, default=str) # default=str to handle dates if any

        result = chain.invoke({
            "extracted_json": extracted_json,
            "crm_json": crm_json
        })
        logger.info(f"Comparison complete. Status: {result.status}")
        return result
    except Exception as e:
        logger.error(f"Error during comparison: {e}")
        raise
