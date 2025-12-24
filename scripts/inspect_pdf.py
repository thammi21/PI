from pypdf import PdfReader

reader = PdfReader("data/VoucherPrintingBatch.pdf")
page = reader.pages[0]
print(page.extract_text())
