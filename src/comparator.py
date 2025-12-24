from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.models import ComparisonResult, InvoiceData
from thefuzz import process, fuzz
import logging
import os
import json

logger = logging.getLogger(__name__)

def calculate_fuzzy_scores(invoice_items: list, crm_line_items: list) -> list:
    """
    Pre-calculates fuzzy match scores between invoice items and CRM line items.
    Returns a list of dictionaries containing match details.
    """
    # Create a dictionary of CRM descriptions to their full objects for easy lookup
    crm_desc_map = {item['description']: item for item in crm_line_items}
    crm_descriptions = list(crm_desc_map.keys())

    if not crm_descriptions:
        return []

    fuzzy_matches = []

    for item in invoice_items:
        # Find best match for invoice item description in CRM descriptions
        result = process.extractOne(item.description, crm_descriptions, scorer=fuzz.token_sort_ratio)
        if result:
            best_match, score = result
        else:
            best_match, score = None, 0
        
        match_details = {
            "invoice_item": item.description,
            "best_crm_match": best_match,
            "similarity_score": score,
            "crm_item_details": crm_desc_map.get(best_match)
        }
        fuzzy_matches.append(match_details)
        
    return fuzzy_matches

def compare_invoice_data(extracted: InvoiceData, crm_data: dict) -> ComparisonResult:
    """
    Compares extracted invoice data with CRM data using a hybrid approach:
    1. Fuzzy Matching for line item descriptions.
    2. LLM for reasoning and final decision making.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    # 1. Perform Fuzzy Matching
    logger.info("Performing fuzzy matching on line items...")
    crm_line_items = crm_data.get("line_items", [])
    fuzzy_results = calculate_fuzzy_scores(extracted.items, crm_line_items)
    logger.info(f"Fuzzy Match Results: {json.dumps(fuzzy_results, indent=2)}")

    # 2. Prepare LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, google_api_key=api_key)
    structured_llm = llm.with_structured_output(ComparisonResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert financial auditor. Your task is to compare data extracted from an Agent Invoice against the Internal Purchase Records (CRM).
        
        You have access to:
        1. Extracted Invoice Data.
        2. Internal CRM Data.
        3. Pre-calculated Fuzzy Match Scores for line items.

        RULES:
        1. Header Check:
           - Compare the following fields between Extracted Data and CRM Data (if present in both):
             * Supplier Name: Check for match (allow minor variations like 'Inc' vs 'Incorporated').
             * Supplier Invoice Number: Verify exact or close match.
             * Due Date: Check if dates match (standardized format).
             * Customer Name: Verify the 'Bill To' entity matches the CRM customer/account name.
             * Currency: Ensure currency codes match.
             * Total Amount: Match total values (allow rounding difference up to 0.05).
        
        2. Line Item Check (Hybrid Approach):
           - Use the provided 'Fuzzy Match Scores' as strong evidence.
           - A score > 80 usually indicates a good match, but use your judgment based on context.
           - If the fuzzy match is high and amounts match, it's a MATCH.
           - If the fuzzy match is low but you can infer a semantic match (e.g. synonyms), it's a MATCH.
           - For each matched item, compare:
             * Description
             * Quantity
             * Amount
        
        3. Analysis:
           - If all amounts match (within tolerance) and line items are accounted for, status is 'MATCH'.
           - If there are discrepancies in amounts or unidentified items, status is 'MISMATCH'.
           - Provide a detailed reasoning for each line item match/mismatch, explicitly mentioning if you relied on fuzzy scores or semantic reasoning.
        
        4. Output:
           - Return the result in the specified JSON structure.
        """),
        ("user", """
        Extracted Agent Invoice Data:
        {extracted_json}
        
        Internal CRM Data:
        {crm_json}
        
        Fuzzy Match Scores:
        {fuzzy_json}
        
        Compare them and provide the status and analysis.
        """)
    ])

    chain = prompt | structured_llm

    logger.info("Invoking LLM for data comparison...")
    try:
        # Convert models/dicts to JSON strings for the prompt
        extracted_json = extracted.model_dump_json(indent=2)
        crm_json = json.dumps(crm_data, default=str, indent=2)
        fuzzy_json = json.dumps(fuzzy_results, indent=2)

        result = chain.invoke({
            "extracted_json": extracted_json,
            "crm_json": crm_json,
            "fuzzy_json": fuzzy_json
        })
         
        if result is None:
            logger.error("LLM returned None. Creating default MISMATCH response.")
            return ComparisonResult(
                status="MISMATCH",
                analysis="LLM comparison failed to return a result.",
                field_level_comparison={"error": "LLM returned None"}
            )
        
        logger.info(f"Comparison complete. Status: {result.status}")
        return result
    except Exception as e:
        logger.error(f"Error during comparison: {e}")
        # Return a default MISMATCH result instead of raising
        return ComparisonResult(
            status="MISMATCH",
            analysis=f"Error during comparison: {str(e)}",
            field_level_comparison={"error": str(e)}
        )
