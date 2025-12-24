from langchain_community.utilities import SQLDatabase
import logging

logger = logging.getLogger(__name__)

def fetch_crm_data(job_reference: str = None, mbl_no: str = None, hbl_no: str = None, invoice_number: str = None, db_path: str = "data/crm.db") -> dict:
    """
    Fetches invoice data from the CRM SQL database using Job Reference or other fields.
    """
    # SQLAlchemy connection string for SQLite
    uri = f"sqlite:///{db_path}"
    
    try:
        db = SQLDatabase.from_uri(uri)
        
        # Using SQLAlchemy engine directly for cleaner dict return
        from sqlalchemy import text
        with db._engine.connect() as connection:
            # Build query dynamically based on available fields
            conditions = []
            params = {}
            
            if job_reference:
                conditions.append("job_reference = :job_reference")
                params["job_reference"] = job_reference
            if mbl_no:
                conditions.append("mbl_no = :mbl_no")
                params["mbl_no"] = mbl_no
            if hbl_no:
                conditions.append("hbl_no = :hbl_no")
                params["hbl_no"] = hbl_no
            if invoice_number:
                # Assuming invoice_number might match job_reference or some other field if needed, 
                # but usually it matches invoice_number if we had that column. 
                # Current schema doesn't seem to have invoice_number column in crm_invoices?
                # Let's check setup_db.py. It has job_reference, customer_name, mbl, hbl, ports, amount.
                # It does NOT have invoice_number. So we can't match on it unless we add it.
                # For now, let's skip invoice_number matching or assume it might be job_reference.
                pass

            if not conditions:
                logger.warning("No search criteria provided for CRM lookup.")
                return {}

            where_clause = " OR ".join(conditions)
            invoice_query = f"SELECT * FROM crm_invoices WHERE {where_clause} LIMIT 1"
            
            logger.info(f"Executing CRM query: {invoice_query} with params {params}")
            invoice_result = connection.execute(text(invoice_query), params).mappings().one_or_none()
            
            if not invoice_result:
                logger.warning(f"No CRM data found for criteria: {params}")
                return {}
            
            invoice_data = dict(invoice_result)
            
            # Fetch Line Items using the found job_reference (primary key for items)
            found_job_ref = invoice_data.get("job_reference")
            if found_job_ref:
                items_query = "SELECT internal_code, description, amount FROM crm_line_items WHERE job_reference = :job_reference"
                items_result = connection.execute(text(items_query), {"job_reference": found_job_ref}).mappings().all()
                invoice_data['line_items'] = [dict(item) for item in items_result]
            else:
                invoice_data['line_items'] = []
            
            logger.info(f"Found CRM data for Job Reference {found_job_ref}")
            return invoice_data
            
    except Exception as e:
        logger.error(f"Error fetching CRM data: {e}")
        return {}
