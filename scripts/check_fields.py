from pypdf import PdfReader

reader = PdfReader("data/VoucherPrintingBatch.pdf")
fields = reader.get_fields()
if fields:
    print("Form fields found:")
    for field in fields:
        print(f"{field}: {fields[field]}")
else:
    print("No form fields found.")
