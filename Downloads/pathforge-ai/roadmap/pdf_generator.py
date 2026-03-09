# pdf_generator.py

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os


# =====================================================
# GLOBAL STYLES
# =====================================================

def get_custom_styles():

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#1F4E79"),
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        name="HeadingStyle",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#2E75B6"),
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        name="NormalStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        spaceAfter=6
    )

    return title_style, heading_style, normal_style


# =====================================================
# ROADMAP PDF
# =====================================================

def generate_roadmap_pdf(filename, roadmap_data, role):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    title_style, heading_style, normal_style = get_custom_styles()

    elements.append(Paragraph(f"{role} Career Roadmap", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    for week in roadmap_data:

        elements.append(
            Paragraph(
                f"Week {week.get('week_number')} - {week.get('title')}",
                heading_style
            )
        )

        elements.append(Paragraph("<b>Concepts:</b>", normal_style))
        concept_list = [
            ListItem(Paragraph(c, normal_style))
            for c in week.get("concepts", [])
        ]
        elements.append(ListFlowable(concept_list, bulletType="bullet"))

        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph("<b>Resources:</b>", normal_style))
        resource_list = [
            ListItem(Paragraph(r, normal_style))
            for r in week.get("learning_resources", [])
        ]
        elements.append(ListFlowable(resource_list, bulletType="bullet"))

        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph("<b>Project:</b>", normal_style))
        elements.append(Paragraph(week.get("project", ""), normal_style))

        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph("<b>Outcome:</b>", normal_style))
        elements.append(Paragraph(week.get("outcome", ""), normal_style))

        elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)
    
def generate_pdf(text):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.cell(0, 8, txt=line, ln=True)

    pdf.output("roadmap.pdf")

    with open("roadmap.pdf", "rb") as f:
        return f.read()


pdf_data = generate_pdf(roadmap_text)

st.download_button(
    "📄 Download Roadmap as PDF",
    pdf_data,
    file_name="AI_Career_Roadmap.pdf"
)


# =====================================================
# RESUME PDF
# =====================================================

def generate_resume_pdf(filename, resume_text):

    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    title_style, heading_style, normal_style = get_custom_styles()

    elements.append(Paragraph("Professional Resume", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    paragraphs = resume_text.split("\n")

    for line in paragraphs:

        if line.strip() == "":
            elements.append(Spacer(1, 0.2 * inch))
            continue

        # Bold section headings
        if line.isupper():
            elements.append(Paragraph(line, heading_style))
        else:
            elements.append(Paragraph(line, normal_style))

    doc.build(elements)