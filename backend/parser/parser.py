# import os
# import pymupdf  # PyMuPDF

# # WINDOWS ONLY: Tell your system where Tesseract executable is located
# # Uncomment and update the path below if you are on Windows
# # os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR"

# def ocr_pdf_parser(pdf_path):
#     # Open the scanned document
#     doc = pymupdf.open(pdf_path)
    
#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
        
#         # Runs OCR behind the scenes using Tesseract
#         # Requires 'pytesseract' package to be installed in the environment
#         ocr_text = page.get_text(option="text")
        
#         print(f"--- Extracted Text from Page {page_num + 1} ---")
#         print(ocr_text.strip())
#         print("\n" + "="*40 + "\n")
        
#     doc.close()

# # Run the parser
# ocr_pdf_parser("data/bio.pdf")


from docling.document_converter import DocumentConverter

source = "data/bio.pdf"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]"