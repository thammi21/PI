from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from src.models import InvoiceData
import logging
import os

from langchain_core.output_parsers import PydanticOutputParser

logger = logging.getLogger(__name__)

def extract_invoice_data(invoice_text: str) -> InvoiceData:
    """
    Extracts structured invoice data from raw text using an LLM.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")

    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0, google_api_key=api_key)
    
    parser = PydanticOutputParser(pydantic_object=InvoiceData)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert data extraction assistant. Extract the invoice details from the provided text.\n{format_instructions}"),
        ("user", "Invoice Text:\n{text}")
    ])

    chain = prompt | llm | parser

    logger.info("Invoking LLM for data extraction...")
    try:
        result = chain.invoke({
            "text": invoice_text,
            "format_instructions": parser.get_format_instructions()
        })
        logger.info("Extraction successful.")
        return result
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        raise
