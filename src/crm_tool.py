from langchain_community.utilities import SQLDatabase
import logging

logger = logging.getLogger(__name__)

def fetch_crm_data(invoice_number: str, db_path: str = "data/crm.db") -> dict:
    """
    Fetches invoice data from the CRM SQL database.
    """
    # SQLAlchemy connection string for SQLite
    uri = f"sqlite:///{db_path}"
    
    try:
        db = SQLDatabase.from_uri(uri)
        query = "SELECT * FROM crm_invoices WHERE invoice_number = :invoice_number"
        
        # Execute query
        # Note: SQLDatabase.run returns a string representation, but we might want raw results.
        # For better control, we can use the underlying engine or just parse the result if simple.
        # However, LangChain's SQLDatabase is often used with agents. 
        # Here we just need a direct lookup.
        
        # Using SQLAlchemy engine directly for cleaner dict return
        from sqlalchemy import text
        with db._engine.connect() as connection:
            result = connection.execute(text(query), {"invoice_number": invoice_number}).mappings().one_or_none()
            
        if result:
            logger.info(f"Found CRM data for invoice {invoice_number}")
            return dict(result)
        else:
            logger.warning(f"No CRM data found for invoice {invoice_number}")
            return {}
            
    except Exception as e:
        logger.error(f"Error fetching CRM data: {e}")
        return {}
