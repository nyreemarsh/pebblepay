"""
PDF Generator for Contracts
Creates professional, well-formatted legal document PDF contracts.
"""
import io
from datetime import datetime
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Custom canvas to add page numbers in footer."""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 9)
        page_num = self._pageNumber
        text = f"Page {page_num} of {page_count}"
        self.drawRightString(7.5*inch, 0.5*inch, text)
        self.restoreState()


def clean_markdown(text: str) -> str:
    """Remove any markdown formatting from text."""
    import re
    
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    
    # Remove italic (*text* or _text_)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'\1', text)
    
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Replace asterisk bullets with dashes
    text = re.sub(r'^\s*\*\s+', '- ', text, flags=re.MULTILINE)
    
    # Clean stray asterisks
    text = re.sub(r'^\s*\*+\s*', '', text, flags=re.MULTILINE)
    
    return text


def generate_contract_pdf(contract_text: str, contract_spec: Dict[str, Any]) -> bytes:
    """Generate a professional legal document PDF."""
    # Clean any markdown from contract text
    contract_text = clean_markdown(contract_text)
    
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1.25*inch,
        leftMargin=1.25*inch,
        topMargin=1*inch,
        bottomMargin=1*inch,
    )
    
    styles = getSampleStyleSheet()
    
    # Legal document styles - Times font for formal look
    title_style = ParagraphStyle(
        'ContractTitle',
        fontName='Times-Bold',
        fontSize=16,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.black,
        leading=20,
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontName='Times-Roman',
        fontSize=11,
        spaceAfter=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#333333'),
    )
    
    section_style = ParagraphStyle(
        'Section',
        fontName='Times-Bold',
        fontSize=11,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.black,
        leading=14,
    )
    
    body_style = ParagraphStyle(
        'Body',
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    
    clause_style = ParagraphStyle(
        'Clause',
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leftIndent=0.25*inch,
    )
    
    party_style = ParagraphStyle(
        'Party',
        fontName='Times-Roman',
        fontSize=10,
        leading=13,
        spaceAfter=4,
        leftIndent=0.4*inch,
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    
    story = []
    today = datetime.now().strftime("%B %d, %Y")
    
    # Title
    title = contract_spec.get("title", "FREELANCE SERVICE AGREEMENT")
    story.append(Paragraph(title.upper(), title_style))
    story.append(Paragraph(f"Effective Date: {today}", subtitle_style))
    
    # Top line
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=16))
    
    # Preamble
    story.append(Paragraph(
        "<b>WHEREAS</b>, the parties desire to enter into this Agreement for the provision of services as set forth herein;",
        body_style
    ))
    story.append(Paragraph(
        "<b>NOW, THEREFORE</b>, in consideration of the mutual covenants and agreements contained herein, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the parties agree as follows:",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    # Parse sections
    sections = parse_contract_sections(contract_text)
    
    for section_title, section_content in sections:
        if section_title:
            formatted_title = format_section_title(section_title)
            story.append(Paragraph(formatted_title, section_style))
        
        for para in section_content.split('\n\n'):
            para = para.strip()
            if not para:
                continue
            
            # Numbered clauses
            if para and len(para) > 2 and para[0].isdigit() and para[1] == '.':
                story.append(Paragraph(format_clause(para), clause_style))
            # Bullet points
            elif para.startswith('•') or para.startswith('-') or para.startswith('*'):
                para = para.replace('•', '&bull;').replace('- ', '&bull; ').replace('* ', '&bull; ')
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{para}", body_style))
            # Party info
            elif any(kw in para.lower() for kw in ['freelancer:', 'client:', 'email:', 'address:']):
                story.append(Paragraph(para, party_style))
            else:
                story.append(Paragraph(para, body_style))
        
        story.append(Spacer(1, 0.05*inch))
    
    # Signature page
    story.append(PageBreak())
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceAfter=16))
    
    story.append(Paragraph(
        "<b>IN WITNESS WHEREOF</b>, the parties have executed this Agreement as of the date first written above.",
        body_style
    ))
    story.append(Spacer(1, 0.4*inch))
    
    # Get names
    freelancer = contract_spec.get("freelancer", {}) or {}
    client = contract_spec.get("client", {}) or {}
    freelancer_name = freelancer.get("name", "")
    client_name = client.get("name", "")
    
    # Signature table
    sig_data = [
        [Paragraph("<b>FREELANCER:</b>", body_style), "", Paragraph("<b>CLIENT:</b>", body_style)],
        ["", "", ""],
        ["", "", ""],
        ["Signature: ________________________", "", "Signature: ________________________"],
        ["", "", ""],
        [f"Print Name: {freelancer_name}", "", f"Print Name: {client_name}"],
        ["", "", ""],
        ["Date: ____________________________", "", "Date: ____________________________"],
    ]
    
    sig_table = Table(sig_data, colWidths=[2.5*inch, 0.75*inch, 2.5*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(sig_table)
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceAfter=8))
    story.append(Paragraph(f"Contract generated by PebblePay • {today}", footer_style))
    
    # Build with page numbers
    doc.build(story, canvasmaker=NumberedCanvas)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def format_section_title(title: str) -> str:
    """Format section title for legal document."""
    title = title.strip()
    # Add ARTICLE prefix if numbered
    if title and title[0].isdigit():
        parts = title.split('.', 1)
        if len(parts) == 2:
            num = parts[0].strip()
            text = parts[1].strip().upper()
            return f"ARTICLE {num}. {text}"
    return title.upper()


def format_clause(clause: str) -> str:
    """Format a numbered clause."""
    return clause


def parse_contract_sections(contract_text: str) -> list:
    """Parse contract text into sections."""
    sections = []
    current_title = None
    current_content = []
    
    for line in contract_text.split('\n'):
        line_stripped = line.strip()
        is_header = False
        
        if line_stripped and len(line_stripped) > 2:
            if line_stripped[0].isdigit() and '.' in line_stripped[:3]:
                is_header = True
            elif line_stripped.isupper() and 3 < len(line_stripped) < 50:
                is_header = True
            elif line_stripped.startswith('===') or line_stripped.startswith('---'):
                continue
        
        if is_header:
            if current_title or current_content:
                sections.append((current_title, '\n'.join(current_content)))
            current_title = line_stripped
            current_content = []
        elif line_stripped:
            current_content.append(line_stripped)
    
    if current_title or current_content:
        sections.append((current_title, '\n'.join(current_content)))
    
    return sections


def generate_simple_contract_pdf(contract_spec: Dict[str, Any]) -> bytes:
    """Generate PDF from spec when contract_text isn't available."""
    contract_text = build_contract_from_spec(contract_spec)
    return generate_contract_pdf(contract_text, contract_spec)


def build_contract_from_spec(spec: Dict[str, Any]) -> str:
    """Build contract text from specification."""
    freelancer = spec.get("freelancer", {}) or {}
    client = spec.get("client", {}) or {}
    payment = spec.get("payment", {}) or {}
    timeline = spec.get("timeline", {}) or {}
    quality = spec.get("quality_standards", {}) or {}
    failure = spec.get("failure_scenarios", {}) or {}
    dispute = spec.get("dispute_resolution", {}) or {}
    
    deliverables = spec.get("deliverables", []) or []
    deliverables_text = "\n".join(
        f"• {d.get('item', d) if isinstance(d, dict) else d}" 
        for d in deliverables
    ) or "• As agreed"
    
    currency_symbol = "£" if payment.get("currency") == "GBP" else "$" if payment.get("currency") == "USD" else ""
    amount = payment.get("amount", "[Amount]")
    
    return f"""
1. PARTIES

This Agreement is entered into between:

Freelancer: {freelancer.get('name', '[Name]')}
Email: {freelancer.get('email', '[Email]')}

Client: {client.get('name', '[Name]')}
Email: {client.get('email', '[Email]')}

2. SCOPE OF WORK

The Freelancer agrees to provide the following deliverables to the Client:

{deliverables_text}

3. COMPENSATION

Total Fee: {currency_symbol}{amount} {payment.get('currency', '')}
Payment Schedule: {payment.get('schedule', 'Upon completion of services')}

Payment shall be made according to the schedule set forth above. Late payments shall accrue interest at the rate of 1.5% per month.

4. TIMELINE

Commencement Date: {timeline.get('start_date', 'Upon execution of this Agreement')}
Completion Deadline: {timeline.get('deadline', '[To be determined]')}

5. REVISIONS AND MODIFICATIONS

The Client shall be entitled to {quality.get('max_revisions', 'two (2)')} rounds of revisions at no additional charge. Additional revisions shall be billed at the Freelancer's standard hourly rate.

6. INTELLECTUAL PROPERTY

Upon receipt of full payment, all intellectual property rights in the deliverables shall transfer to the Client. The Freelancer retains the right to display the work in their portfolio for promotional purposes.

7. CONFIDENTIALITY

Both parties agree to maintain the confidentiality of any proprietary information disclosed during the course of this Agreement.

8. TERMINATION

Either party may terminate this Agreement with fourteen (14) days written notice. In the event of termination, the Client shall pay for all work completed to date.

9. LIMITATION OF LIABILITY

The Freelancer's liability under this Agreement shall not exceed the total fees paid by the Client.

10. DISPUTE RESOLUTION

Method: {dispute.get('method', 'Mediation, followed by binding arbitration if necessary')}

Any disputes arising under this Agreement shall be resolved through the method specified above.

11. GENERAL PROVISIONS

This Agreement constitutes the entire agreement between the parties and supersedes all prior negotiations and agreements. This Agreement may only be modified in writing signed by both parties.

12. GOVERNING LAW

This Agreement shall be governed by and construed in accordance with the laws of the jurisdiction in which the Freelancer is located.
"""
