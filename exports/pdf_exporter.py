"""
FILE NAME: pdf_exporter.py

PURPOSE:
Export itinerary/costing to a print-ready A4 PDF.

DEPENDENCIES:
reportlab

LAST UPDATED:
2026-08-02
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

PAGE_MARGIN = 18 * mm

class PDFExporter:

    def export(self, filename, text):

        pdf = SimpleDocTemplate(
            filename,
            pagesize=A4,
            leftMargin=PAGE_MARGIN,
            rightMargin=PAGE_MARGIN,
            topMargin=PAGE_MARGIN,
            bottomMargin=PAGE_MARGIN,
            title="PM Automation Quotation",
            author="Nepal International Travel Services"
        )

        styles = getSampleStyleSheet()

        content = []

        for i, block in enumerate(str(text).split("\n")):
            block = block.strip()

            if not block:
                content.append(Spacer(1, 4 * mm))
            elif block.isupper() and len(block) > 3:
                content.append(Paragraph(
                    block,
                    styles["Heading2"]
                ))
            else:
                content.append(Paragraph(
                    self._escape(block),
                    styles["BodyText"]
                ))

        pdf.build(content)

        return filename

    def _escape(self, text):
        return (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
