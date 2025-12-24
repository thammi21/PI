from pypdf import PdfReader
import re

def verify_pdf():
    pdf_path = "output/verified_invoice.pdf"
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        text = page.extract_text()
        
        # print("--- Extracted Text ---")
        # print(text.encode('utf-8', errors='ignore').decode('utf-8'))
        # print("----------------------")
        
        # Check for new values
        shipper_found = "MARVENTO" in text
        consignee_found = "COMPASS SEA AND AIR CARGO" in text
        
        # Check for old template values (should be masked)
        # Old Shipper: LASSELSBERGER S.R.O.
        # Old Consignee: MBTP SA
        old_shipper_found = "LASSELSBERGER" in text
        old_consignee_found = "MBTP SA" in text
        
        if shipper_found and consignee_found:
            print("\nSUCCESS: New Shipper and Consignee found.")
        else:
            print("\nFAILURE: New values not found.")
            
        if not old_shipper_found and not old_consignee_found:
            print("SUCCESS: Old template values are masked.")
        else:
            print("FAILURE: Old template values are still visible.")
            
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    verify_pdf()
