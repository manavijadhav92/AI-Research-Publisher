# services/formatter.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import textwrap

def make_pdf(title, summary, limitations, innovations, filename="paper.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, title); y -= 28
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Generated: {datetime.utcnow().isoformat()} UTC"); y -= 20
    # Summary
    c.setFont("Helvetica-Bold", 12); c.drawString(margin, y, "Abstract:"); y -= 18
    c.setFont("Helvetica", 10)
    for line in textwrap.wrap(summary, 100):
        c.drawString(margin, y, line); y -= 14
    y -= 8
    # Limitations
    c.setFont("Helvetica-Bold", 12); c.drawString(margin, y, "Limitations:"); y -= 16
    c.setFont("Helvetica", 10)
    for lim in limitations:
        for line in textwrap.wrap("- " + lim, 100):
            c.drawString(margin, y, line); y -= 14
        y -= 4
    y -= 8
    # Innovations
    c.setFont("Helvetica-Bold", 12); c.drawString(margin, y, "Proposed Innovations:"); y -= 16
    c.setFont("Helvetica", 10)
    for inv in innovations:
        title_line = inv.get("title", "")
        summary_line = inv.get("summary","")
        c.drawString(margin, y, f"• {title_line}"); y -= 14
        for line in textwrap.wrap("   " + summary_line, 100):
            c.drawString(margin, y, line); y -= 12
        y -= 6
    c.save()
    return filename
