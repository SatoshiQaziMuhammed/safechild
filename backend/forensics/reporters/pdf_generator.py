"""
PDF Report Generator
Professional court-admissible PDF reports using ReportLab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

# Define the path to the logo (assuming it's in the backend directory)
LOGO_PATH = Path(__file__).parent.parent.parent / "safechild_logo.png"

class PDFReportGenerator:
    """Generate professional PDF forensic reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=15, # Changed from 30 to 15
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#93c5fd'),
            borderPadding=5,
            backColor=colors.HexColor('#eff6ff')
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6
        ))
        
        # Small text style
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=4
        ))
        
        # COC Event style
        self.styles.add(ParagraphStyle(
            name='CoCEvent',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=3,
            leftIndent=0.5*cm
        ))
    
    async def generate(self, data: Dict, output_path: Path):
        """
        Generate PDF report
        
        Args:
            data: Report data dictionary
            output_path: Path to save PDF
        """
        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build story (content)
        story = []
        
        # Header
        story.extend(self._build_header(data))
        story.append(PageBreak())
        
        # Case Information
        story.extend(self._build_case_info(data))
        story.append(Spacer(1, 0.5*cm))
        
        # Summary Statistics
        story.extend(self._build_summary(data))
        story.append(Spacer(1, 0.5*cm))
        
        # WhatsApp Analysis
        if data.get('whatsapp', {}).get('messages'):
            story.extend(self._build_whatsapp_section(data))
            story.append(Spacer(1, 0.5*cm))
        
        # Telegram Analysis
        if data.get('telegram', {}).get('messages'):
            story.extend(self._build_telegram_section(data))
            story.append(Spacer(1, 0.5*cm))
        
        # SMS & Calls
        if data.get('sms', {}).get('messages') or data.get('sms', {}).get('calls'):
            story.extend(self._build_sms_section(data))
            story.append(Spacer(1, 0.5*cm))

        # Signal Analysis
        if data.get('signal', {}).get('messages'):
            story.extend(self._build_signal_section(data))
            story.append(Spacer(1, 0.5*cm))

        # Media Analysis Summary
        if data.get('media_analysis', {}).get('total_files', 0) > 0:
            story.extend(self._build_media_summary_section(data))
            story.append(Spacer(1, 0.5*cm))

        # Timeline
        story.append(PageBreak())
        story.extend(self._build_timeline_section(data))
        
        # Contact Network
        story.append(PageBreak())
        story.extend(self._build_contacts_section(data))

        # Chain of Custody
        story.append(PageBreak())
        story.extend(self._build_chain_of_custody_section(data))
        
        # Footer (Certification)
        story.append(PageBreak())
        story.extend(self._build_footer(data))
        
        # Build PDF
        doc.build(story, onFirstPage=self._page_template, onLaterPages=self._page_template)
        
        return output_path
    
    def _build_header(self, data: Dict):
        """Build report header with logo"""
        elements = []

        # Logo
        if LOGO_PATH.exists():
            logo = Image(str(LOGO_PATH), width=4*cm, height=4*cm)
            elements.append(logo)
            elements.append(Spacer(1, 0.5*cm))
        
        # Title
        elements.append(Paragraph(
            "SafeChild Hukuk Bürosu",
            self.styles['CustomTitle']
        ))
        
        elements.append(Paragraph(
            "Forensic Analysis Report",
            self.styles['CustomSubtitle']
        ))
        
        elements.append(Spacer(1, 1*cm))
        
        # Case ID Box
        case_id_style = ParagraphStyle(
            'CaseIDBox',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        case_table = Table(
            [[Paragraph(f"Case ID: {data['case_id']}", case_id_style)]],
            colWidths=[15*cm]
        )
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(case_table)
        
        elements.append(Spacer(1, 1.5*cm))
        
        # Warning box
        warning_text = Paragraph(
            "<b>CONFIDENTIAL - LEGAL DOCUMENT</b><br/>"
            "This forensic analysis report contains sensitive information "
            "and is intended solely for legal proceedings. "
            "Unauthorized disclosure is prohibited.",
            self.styles['SmallText']
        )
        
        warning_table = Table([[warning_text]], colWidths=[15*cm])
        warning_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#f59e0b')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(warning_table)
        
        return elements
    
    def _build_case_info(self, data: Dict):
        """Build case information section"""
        elements = []
        
        elements.append(Paragraph("Case Information", self.styles['SectionHeader']))
        
        info_data = [
            ['Case ID:', data['case_id']],
            ['Client:', data['client'].get('email', 'N/A')],
            ['Analysis Date:', datetime.fromisoformat(data['analysis_date']).strftime('%Y-%m-%d %H:%M:%S UTC')],
            ['File Name:', data['file_name']],
            ['File Size:', self._format_size(data['file_size'])],
            ['SHA-256 Hash:', data['file_hash'][:64]],
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 11*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff6ff')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        
        return elements
    
    def _build_summary(self, data: Dict):
        """Build summary statistics"""
        elements = []
        
        elements.append(Paragraph("Summary Statistics", self.styles['SectionHeader']))
        
        stats = data.get('statistics', {})
        
        summary_data = [
            ['Platform', 'Messages', 'Contacts', 'Additional'],
            [
                'WhatsApp',
                str(len(data.get('whatsapp', {}).get('messages', []))),
                str(len(data.get('whatsapp', {}).get('contacts', []))),
                f"{len(data.get('whatsapp', {}).get('deleted', []))} deleted"
            ],
            [
                'Telegram',
                str(len(data.get('telegram', {}).get('messages', []))),
                str(len(data.get('telegram', {}).get('contacts', []))),
                f"{len(data.get('telegram', {}).get('chats', []))} chats"
            ],
            [
                'SMS',
                str(len(data.get('sms', {}).get('messages', []))),
                '-',
                f"{len(data.get('sms', {}).get('calls', []))} calls"
            ],
            [
                'Signal',
                str(len(data.get('signal', {}).get('messages', []))),
                str(len(data.get('signal', {}).get('contacts', []))),
                '-'
            ],
            [
                'TOTAL',
                str(sum([
                    len(data.get('whatsapp', {}).get('messages', [])),
                    len(data.get('telegram', {}).get('messages', [])),
                    len(data.get('sms', {}).get('messages', [])),
                    len(data.get('signal', {}).get('messages', []))
                ])),
                str(data.get('contact_network', {}).get('total_contacts', 0)),
                f"{len(data.get('timeline', []))} timeline events"
            ]
        ]
        
        summary_table = Table(summary_data, colWidths=[4*cm, 3*cm, 3*cm, 5*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        
        return elements
    
    def _build_whatsapp_section(self, data: Dict):
        """Build WhatsApp analysis section"""
        elements = []
        
        elements.append(Paragraph("WhatsApp Analysis", self.styles['SectionHeader']))
        
        messages = data.get('whatsapp', {}).get('messages', [])[:10]  # First 10
        
        for msg in messages:
            timestamp = datetime.fromtimestamp(msg.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S') if msg.get('timestamp') else 'N/A'
            
            msg_text = f"""
            <b>Time:</b> {timestamp}<br/>
            <b>Contact:</b> {msg.get('contact', 'Unknown')}<br/>
            <b>Direction:</b> {'Outgoing' if msg.get('from_me') else 'Incoming'}<br/>
            <b>Content:</b> {msg.get('content', '[No text]')[:200]}
            """
            
            elements.append(Paragraph(msg_text, self.styles['SmallText']))
            elements.append(Spacer(1, 0.3*cm))
        
        return elements
    
    def _build_telegram_section(self, data: Dict):
        """Build Telegram analysis section"""
        elements = []
        
        elements.append(Paragraph("Telegram Analysis", self.styles['SectionHeader']))
        elements.append(Paragraph(
            f"Total Messages: {len(data.get('telegram', {}).get('messages', []))}",
            self.styles['InfoText']
        ))
        
        return elements
    
    def _build_sms_section(self, data: Dict):
        """Build SMS & Calls section"""
        elements = []
        
        elements.append(Paragraph("SMS & Call Logs", self.styles['SectionHeader']))
        elements.append(Paragraph(
            f"SMS Messages: {len(data.get('sms', {}).get('messages', []))}",
            self.styles['InfoText']
        ))
        elements.append(Paragraph(
            f"Call Logs: {len(data.get('sms', {}).get('calls', []))}",
            self.styles['InfoText']
        ))
        
        return elements
    
    def _build_timeline_section(self, data: Dict):
        """Build timeline section"""
        elements = []
        
        elements.append(Paragraph("Communication Timeline", self.styles['SectionHeader']))
        
        timeline = data.get('timeline', [])[:50]  # Increased to 50 events for more detail
        
        for event in timeline:
            timestamp = datetime.fromtimestamp(event.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S UTC') if event.get('timestamp') else 'N/A'
            
            event_text = f"[{timestamp}] <b>{event.get('source', 'Unknown')}</b> - {event.get('type', 'message')}"
            if event.get('deleted'):
                event_text += " <font color=\'red\'>⚠️ DELETED</font>"
            content_preview = event.get('content_preview', '')
            if content_preview:
                event_text += f"<br/><i>Content:</i> {content_preview}"
            
            elements.append(Paragraph(event_text, self.styles['SmallText']))
            elements.append(Spacer(1, 0.2*cm))
        
        return elements
    
    def _build_contacts_section(self, data: Dict):
        """Build contacts section"""
        elements = []
        
        elements.append(Paragraph("Contact Network", self.styles['SectionHeader']))
        
        network = data.get('contact_network', {})
        elements.append(Paragraph(
            f"Total Contacts: {network.get('total_contacts', 0)}",
            self.styles['InfoText']
        ))

        if network.get('top_contacts'):
            elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph("Top Interacted Contacts:", self.styles['InfoText']))
            contact_table_data = [["Contact ID", "Name", "Platforms", "Messages", "Calls", "Total Interactions"]]
            for contact_id in network['top_contacts'][:10]: # Top 10
                contact = network['contacts'].get(contact_id, {})
                contact_table_data.append([
                    contact_id,
                    contact.get('name', 'Unknown'),
                    ', '.join(contact.get('platforms', [])),
                    str(contact.get('message_count', 0)),
                    str(contact.get('call_count', 0)),
                    str(contact.get('total_interactions', 0))
                ])
            
            contact_table = Table(contact_table_data, colWidths=[3*cm, 4*cm, 3*cm, 2*cm, 2*cm, 2*cm])
            contact_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(contact_table)
        
        return elements

    def _build_footer(self, data: Dict):
        """Build report footer"""
        elements = []
        
        elements.append(Paragraph("Report Certification", self.styles['SectionHeader']))
        
        cert_text = f"""
        This report was generated using the SafeChild Forensic Data Parser
        on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}.
        <br/><br/>
        The analysis was conducted by parsing data from the provided backup file. The integrity
        of the original evidence file is guaranteed by cryptographic hashing.
        (SHA-256: {data['file_hash']}).
        <br/><br/>
        This report reflects the data found within the provided backup file.
        """
        
        elements.append(Paragraph(cert_text, self.styles['InfoText']))
        
        return elements
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def _page_template(self, canvas_obj, doc):
        """Adds page number and current date/time to each page"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 9)

        # Page Number
        page_num_text = f"Page {canvas_obj.getPageNumber()}"
        canvas_obj.drawRightString(doc.rightMargin + doc.width, 1.5 * cm, page_num_text)

        # Current Date/Time
        current_datetime_text = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        canvas_obj.drawString(doc.leftMargin, 1.5 * cm, current_datetime_text)

        canvas_obj.restoreState()

    def _build_signal_section(self, data: Dict):
        """Build Signal analysis section"""
        elements = []
        
        elements.append(Paragraph("Signal Analysis", self.styles['SectionHeader']))
        elements.append(Paragraph(
            f"Total Messages: {len(data.get('signal', {}).get('messages', []))}",
            self.styles['InfoText']
        ))
        
        return elements
    
    def _build_media_summary_section(self, data: Dict):
        """Build media analysis summary section"""
        elements = []
        elements.append(Paragraph("Media File Analysis Summary", self.styles['SectionHeader']))
        
        media_analysis = data.get('media_analysis', {})
        elements.append(Paragraph(
            f"Total Files: {media_analysis.get('total_files', 0)}",
            self.styles['InfoText']
        ))
        elements.append(Paragraph(
            f"Total Size: {media_analysis.get('total_size_formatted', 'N/A')}",
            self.styles['InfoText']
        ))

        by_type_data = [["Type", "Count"]]
        for m_type, count in media_analysis.get('by_type', {}).items():
            by_type_data.append([m_type, str(count)])

        if len(by_type_data) > 1:
            type_table = Table(by_type_data, colWidths=[7.5*cm, 7.5*cm])
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(Spacer(1, 0.5*cm))
            elements.append(type_table)

        return elements

    def _build_chain_of_custody_section(self, data: Dict):
        """Build Chain of Custody section"""
        elements = []
        elements.append(Paragraph("Chain of Custody Log", self.styles['SectionHeader']))
        elements.append(Paragraph(
            "A chronological record of actions taken on the evidence file to maintain its integrity.",
            self.styles['InfoText']
        ))
        elements.append(Spacer(1, 0.3*cm))

        coc_events = data.get('chain_of_custody', [])
        if not coc_events:
            elements.append(Paragraph("No Chain of Custody events recorded.", self.styles['InfoText']))
            return elements

        # Sort by timestamp ascending
        sorted_coc = sorted(coc_events, key=lambda x: x.get('timestamp', datetime.min))

        for event in sorted_coc:
            timestamp = event.get('timestamp', datetime.min).strftime('%Y-%m-%d %H:%M:%S UTC')
            actor = event.get('actor', 'N/A')
            action = event.get('action', 'N/A')
            details = event.get('details', 'N/A')
            event_hash = event.get('hashAtEvent', 'N/A')
            ip_address = event.get('ipAddress', 'N/A')

            event_text = f"""
            <b>Time:</b> {timestamp}<br/>
            <b>Actor:</b> {actor}<br/>
            <b>Action:</b> {action}<br/>
            <b>Details:</b> {details}<br/>
            <b>IP Address:</b> {ip_address}<br/>
            <b>Hash (at event):</b> {event_hash[:64]}
            """
            elements.append(Paragraph(event_text, self.styles['CoCEvent']))
            elements.append(Spacer(1, 0.2*cm))
        
        return elements
