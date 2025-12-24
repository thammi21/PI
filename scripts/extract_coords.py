from pypdf import PdfReader

def visitor_body(text, cm, tm, fontDict, fontSize):
    x = tm[4]
    y = tm[5]
    if text and text.strip():
        with open("coords.txt", "a", encoding="utf-8") as f:
            f.write(f"Text: '{text.strip()}' at x={x}, y={y}\n")

# Clear file
with open("coords.txt", "w") as f:
    pass

reader = PdfReader("data/VoucherPrintingBatch.pdf")
page = reader.pages[0]
page.extract_text(visitor_text=visitor_body)
