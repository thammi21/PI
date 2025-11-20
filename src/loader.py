from langchain_community.document_loaders import PyPDFLoader
import logging

logger = logging.getLogger(__name__)

def load_invoice_pdf(file_path: str) -> str:
    """
    Loads a PDF file and returns the extracted text content.
    """
    try:
        logger.info(f"Loading PDF from: {file_path}")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        full_text = "\n".join([page.page_content for page in pages])
        logger.info(f"Successfully extracted {len(full_text)} characters from PDF.")
        return full_text
    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
        raise
