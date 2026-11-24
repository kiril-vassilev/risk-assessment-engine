from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml.shared import OxmlElement
from docx.shared import Inches, Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.text.paragraph import Paragraph
from docx.text.run import Run


class ColorConfig(NamedTuple):
    """Color configuration for different indicator types."""
    fact: RGBColor = RGBColor(0, 112, 192)  # Blue
    analysis: RGBColor = RGBColor(112, 173, 71)  # Green
    favorable: RGBColor = RGBColor(146, 208, 80)  # Light Green
    neutral: RGBColor = RGBColor(127, 127, 127)  # Gray
    risk: RGBColor = RGBColor(192, 0, 0)  # Red


def add_formatted_text(paragraph: Paragraph, text: str, *, hyperlinks: bool = False) -> list[Run]:
    runs = []

    def add_segment(segment: str, bold: bool) -> None:
        start = 0
        if hyperlinks:
            for match in re.finditer(r'https?://[^\s]+', segment):
                if match.start() > start:
                    run = paragraph.add_run(segment[start:match.start()])
                    if bold:
                        run.bold = True
                    runs.append(run)
                add_hyperlink(paragraph, match.group(), match.group(), bold=bold)
                start = match.end()
        if start < len(segment):
            run = paragraph.add_run(segment[start:])
            if bold:
                run.bold = True
            runs.append(run)

    start = 0
    for match in re.finditer(r'\*\*(.+?)\*\*', text):
        add_segment(text[start:match.start()], False)
        add_segment(match.group(1), True)
        start = match.end()
    add_segment(text[start:], False)
    return runs


def add_page_break(doc: Document) -> None:
    """Add a page break to the document."""
    doc.add_page_break()


def set_margins(doc: Document, margins: float = 1) -> None:
    """Set document margins in inches."""
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(margins)
        section.bottom_margin = Inches(margins)
        section.left_margin = Inches(margins)
        section.right_margin = Inches(margins)


def add_header(doc: Document, title: str, subtitle: str) -> None:
    """Add a professional header to the document."""
    # Add title
    title_para = doc.add_paragraph()
    for title_run in add_formatted_text(title_para, title):
        title_run.font.size = Pt(24)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(0, 51, 102)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add subtitle
    subtitle_para = doc.add_paragraph()
    for subtitle_run in add_formatted_text(subtitle_para, subtitle):
        subtitle_run.font.size = Pt(12)
        subtitle_run.font.color.rgb = RGBColor(89, 89, 89)
    subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add date
    date_para = doc.add_paragraph()
    date_run = date_para.add_run(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    date_run.font.size = Pt(10)
    date_run.font.italic = True
    date_run.font.color.rgb = RGBColor(127, 127, 127)
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add separator line
    separator = doc.add_paragraph()
    separator.paragraph_format.space_after = Pt(12)
    pPr = separator._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '666666')
    pBdr.append(bottom)
    pPr.append(pBdr)
    
    doc.add_paragraph()  # Spacing


def add_toc_placeholder(doc: Document) -> None:
    """Add a table of contents placeholder."""
    toc_para = doc.add_paragraph()
    toc_run = toc_para.add_run("TABLE OF CONTENTS")
    toc_run.font.bold = True
    toc_run.font.size = Pt(14)
    toc_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Add note about TOC
    note_para = doc.add_paragraph()
    note_run = note_para.add_run("(To generate automatic table of contents, right-click here and select 'Update Field' in Microsoft Word)")
    note_run.font.italic = True
    note_run.font.size = Pt(9)
    note_run.font.color.rgb = RGBColor(127, 127, 127)
    
    # Add field for TOC
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-2" \\h \\z \\u'
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    
    doc.add_paragraph()


def add_toc_page(doc: Document) -> None:
    add_page_break(doc)
    add_toc_placeholder(doc)
    add_page_break(doc)


def parse_table_row(line: str) -> list[str] | None:
    line = line.strip()
    if not line.startswith('|') or not line.endswith('|'):
        return None
    return [cell.strip() for cell in line[1:-1].split('|')]


def add_report_table(doc: Document, rows: list[list[str]]) -> None:
    table = doc.add_table(rows=0, cols=len(rows[0]))
    table.style = 'Table Grid'
    for index, values in enumerate(rows):
        row = table.add_row()
        if index == 0:
            row_properties = row._tr.get_or_add_trPr()
            row_properties.append(OxmlElement('w:tblHeader'))
        for cell, value in zip(row.cells, values):
            runs = add_formatted_text(cell.paragraphs[0], value)
            if index == 0:
                for run in runs:
                    run.bold = True


def parse_finding_line(line: str) -> dict:
    """Parse a finding line to extract components.
    
    Format: - [KIND] [DIRECTION] statement (date_context) [Sources: source_ids]
    Example: - [FACT] [FAVORABLE] Text here (2025) [Sources: F001, F002]
    """
    finding = {
        'kind': None,
        'direction': None,
        'statement': '',
        'date_context': '',
        'source_ids': [],
        'raw_line': line
    }
    
    # Remove leading dash and spaces
    line = line.lstrip('- ').strip()
    
    # Extract kind (FACT, ANALYSIS, etc.)
    kind_match = re.match(r'\[([A-Z]+)\]', line)
    if kind_match:
        finding['kind'] = kind_match.group(1)
        line = line[kind_match.end():].strip()
    
    # Extract direction (FAVORABLE, NEUTRAL, RISK)
    direction_match = re.match(r'\[([A-Z]+)\]', line)
    if direction_match:
        finding['direction'] = direction_match.group(1)
        line = line[direction_match.end():].strip()
    
    # Extract sources from end (before date context if present)
    sources_match = re.search(r'\[Sources: ([^\]]+)\]$', line)
    if sources_match:
        source_str = sources_match.group(1)
        finding['source_ids'] = [s.strip() for s in source_str.split(',')]
        line = line[:sources_match.start()].strip()
    
    # Extract date context (last parenthesized content before sources)
    date_match = re.search(r'\(([^)]+)\)\s*$', line)
    if date_match:
        finding['date_context'] = date_match.group(1)
        line = line[:date_match.start()].strip()
    
    finding['statement'] = line
    return finding


def get_indicator_color(indicator_type: str, colors: ColorConfig) -> RGBColor:
    """Get color based on indicator type."""
    indicator_map = {
        'FACT': colors.fact,
        'ANALYSIS': colors.analysis,
        'FAVORABLE': colors.favorable,
        'NEUTRAL': colors.neutral,
        'RISK': colors.risk,
    }
    return indicator_map.get(indicator_type, colors.neutral)


def add_finding_to_doc(doc: Document, finding: dict, colors: ColorConfig) -> None:
    """Add a formatted finding paragraph to document."""
    para = doc.add_paragraph(style='List Bullet')
    
    # Add kind indicator
    if finding['kind']:
        kind_run = para.add_run(f"[{finding['kind']}]")
        kind_run.font.bold = True
        kind_run.font.color.rgb = get_indicator_color(finding['kind'], colors)
        para.add_run(" ")
    
    # Add direction indicator
    if finding['direction']:
        direction_run = para.add_run(f"[{finding['direction']}]")
        direction_run.font.bold = True
        direction_color = get_indicator_color(finding['direction'], colors)
        direction_run.font.color.rgb = direction_color
        para.add_run(" ")
    
    # Add statement
    for statement_run in add_formatted_text(para, finding['statement']):
        if finding['direction'] == 'RISK':
            statement_run.font.color.rgb = colors.risk
    
    # Add date context
    if finding['date_context']:
        for date_run in add_formatted_text(para, f" ({finding['date_context']})"):
            date_run.font.italic = True
            date_run.font.size = Pt(9)
    
    # Add sources
    if finding['source_ids']:
        for sources_run in add_formatted_text(para, f" [Sources: {', '.join(finding['source_ids'])}]"):
            sources_run.font.italic = True
            sources_run.font.size = Pt(9)
            sources_run.font.color.rgb = colors.neutral


def convert_text_report_to_word(input_file: Path, output_file: Path | None = None) -> Path:
    """Convert text report to Word document.
    
    Args:
        input_file: Path to input text file
        output_file: Path to output Word file (defaults to same name with .docx)
    
    Returns:
        Path to generated Word document
    """
    if output_file is None:
        output_file = input_file.with_suffix('.docx')
    
    # Read input file
    text_content = input_file.read_text(encoding='utf-8')
    lines = text_content.split('\n')
    
    # Create document
    doc = Document()
    set_margins(doc)
    
    # Add page numbers and footer
    section = doc.sections[0]
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_run = footer_para.add_run()
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add field for page number
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    footer_run._r.append(fldChar)
    footer_run._r.append(instrText)
    footer_run._r.append(fldChar2)
    
    colors = ColorConfig()
    in_sources_section = False
    pending_toc = False
    table_end = 0
    
    # Parse and add content
    for i, line in enumerate(lines):
        if i < table_end:
            continue
        line = line.rstrip()

        is_metadata = line.startswith('Aircraft MSN:') or line.startswith('Deal Jurisdiction:') or line == '---'
        toc_just_added = pending_toc and bool(line) and not is_metadata
        if toc_just_added:
            add_toc_page(doc)
            pending_toc = False

        if not line:
            doc.add_paragraph()
            continue
        
        # Title (# prefix)
        if line.startswith('# '):
            title = line[2:].strip()
            # Extract airline name and details from title if available
            add_header(doc, title, "")
            if i < 20:  # Only add TOC near the beginning
                pending_toc = True
            in_sources_section = False
            continue
        
        # Subtitle/metadata lines (after title, before first ##)
        if is_metadata:
            if line != '---':
                meta_para = doc.add_paragraph()
                add_formatted_text(meta_para, line)
                meta_para.style = 'Normal'
            continue
        
        # Main sections (## prefix)
        if line.startswith('## '):
            section_title = line[3:].strip()
            heading = doc.add_heading(level=1)
            add_formatted_text(heading, section_title)
            heading.style = 'Heading 1'
            heading.paragraph_format.page_break_before = not toc_just_added
            in_sources_section = section_title == "Sources" or "Sources" in section_title
            continue
        
        # Subsections (### prefix)
        if line.startswith('### '):
            section_title = line[4:].strip()
            heading = doc.add_heading(level=2)
            add_formatted_text(heading, section_title)
            heading.style = 'Heading 2'
            in_sources_section = section_title == "Sources" or "Sources" in section_title
            continue

        header = parse_table_row(line)
        separator = parse_table_row(lines[i + 1]) if header and i + 1 < len(lines) else None
        if (header and separator and len(header) == len(separator)
                and all(re.fullmatch(r':?-{3,}:?', cell) for cell in separator)):
            rows = [header]
            table_end = i + 2
            while table_end < len(lines):
                row = parse_table_row(lines[table_end])
                if row is None or len(row) != len(header):
                    break
                rows.append(row)
                table_end += 1
            add_report_table(doc, rows)
            continue
        
        # Findings (bullet points starting with -)
        if line.startswith('- ['):
            finding = parse_finding_line(line)
            add_finding_to_doc(doc, finding, colors)
            continue
        
        # Sources section entries
        if in_sources_section and line.startswith('- '):
            source_line = line[2:].strip()
            para = doc.add_paragraph(style='List Bullet')
            add_formatted_text(para, source_line, hyperlinks=True)
            continue
        
        # Regular text paragraphs
        if line:
            para = doc.add_paragraph()
            add_formatted_text(para, line)
    
    if pending_toc:
        add_toc_page(doc)

    # Save document
    doc.save(str(output_file))
    return output_file


def add_hyperlink(paragraph: Paragraph, url: str, text: str, *, bold: bool = False) -> None:
    """Add a hyperlink to a paragraph using the proper Word format."""
    # This is a workaround since python-docx doesn't have built-in hyperlink support
    part = paragraph.part
    rel_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), rel_id)
    
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    new_run.append(rPr)
    
    rStyle = OxmlElement('w:rStyle')
    rStyle.set(qn('w:val'), 'Hyperlink')
    rPr.append(rStyle)
    if bold:
        rPr.append(OxmlElement('w:b'))
    
    new_run.append(OxmlElement('w:t'))
    new_run[-1].text = text
    hyperlink.append(new_run)
    
    paragraph._element.append(hyperlink)
