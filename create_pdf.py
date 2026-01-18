from reportlab.pdfgen import canvas

c = canvas.Canvas("test_doc.pdf")
c.drawString(100, 750, "Hello world. This is a test PDF for the RAG system ingestion pipeline.")
c.drawString(100, 730, "It should be split into chunks correctly.")
c.showPage()
c.save()
print("PDF Created")
