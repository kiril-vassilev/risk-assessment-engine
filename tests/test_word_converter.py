"""Tests for the Word document converter module."""

from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

from risk_assessment_engine.word_converter import (
    convert_text_report_to_word,
    parse_finding_line,
    ColorConfig,
)


def test_parse_finding_line_with_all_components():
    """Test parsing a complete finding line with all components."""
    line = "- [FACT] [FAVORABLE] Revenue of $150M indicates strong financial performance. (2025) [Sources: F001, F002]"
    finding = parse_finding_line(line)
    
    assert finding['kind'] == 'FACT'
    assert finding['direction'] == 'FAVORABLE'
    assert finding['statement'] == 'Revenue of $150M indicates strong financial performance.'
    assert finding['date_context'] == '2025'
    assert finding['source_ids'] == ['F001', 'F002']


def test_parse_finding_line_with_kind_only():
    """Test parsing a finding line with only kind indicator."""
    line = "- [FACT] Revenue of $150M indicates strong financial performance. [Sources: F001]"
    finding = parse_finding_line(line)
    
    assert finding['kind'] == 'FACT'
    assert finding['direction'] is None
    assert finding['statement'] == 'Revenue of $150M indicates strong financial performance.'
    assert finding['source_ids'] == ['F001']


def test_parse_finding_line_with_analysis_risk():
    """Test parsing an ANALYSIS with RISK direction."""
    line = "- [ANALYSIS] [RISK] Rapid expansion increases operational risk. (2025-2026) [Sources: O001, O002, O003]"
    finding = parse_finding_line(line)
    
    assert finding['kind'] == 'ANALYSIS'
    assert finding['direction'] == 'RISK'
    assert finding['statement'] == 'Rapid expansion increases operational risk.'
    assert finding['date_context'] == '2025-2026'
    assert len(finding['source_ids']) == 3


def test_parse_finding_line_no_sources():
    """Test parsing a finding line without sources."""
    line = "- [FACT] [NEUTRAL] Fleet size is 15 aircraft. (2025)"
    finding = parse_finding_line(line)
    
    assert finding['kind'] == 'FACT'
    assert finding['direction'] == 'NEUTRAL'
    assert finding['statement'] == 'Fleet size is 15 aircraft.'
    assert finding['source_ids'] == []


def test_color_config_defaults():
    """Test that ColorConfig has proper default colors."""
    colors = ColorConfig()
    
    # RGBColor doesn't have .rgb attribute, but we can verify the hex representation
    assert str(colors.fact) == "0070C0"  # Blue in hex format
    assert str(colors.analysis) == "70AD47"  # Green
    assert str(colors.favorable) == "92D050"  # Light Green
    assert str(colors.neutral) == "7F7F7F"  # Gray
    assert str(colors.risk) == "C00000"  # Red


def test_convert_text_report_to_word_creates_file():
    """Test that conversion creates a valid Word document."""
    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a simple test report
        input_file = tmpdir_path / "test_report.txt"
        output_file = tmpdir_path / "test_report.docx"
        
        test_content = """# Risk Assessment Report: TestAirline
Aircraft MSN: 1001 | Aircraft Variant: A320-214
Deal Jurisdiction: Oman
---

## 1. Executive Summary
Test airline is a regional carrier operating narrowbody aircraft.

- [FACT] [FAVORABLE] Operating revenues of $100M. (2025) [Sources: F001]
- [ANALYSIS] [RISK] Limited financial disclosures available. (2025) [Sources: F001]

### Sources
- F001: Test Source — example.com; published 2026-01-01; https://example.com/test

## 2. Financial Risks
Financial analysis shows moderate performance.

- [FACT] [NEUTRAL] EBITDA margin of 5%. (2025) [Sources: F001]

### Sources
- F001: Test Source — example.com; published 2026-01-01; https://example.com/test
"""
        
        input_file.write_text(test_content, encoding='utf-8')
        
        # Convert to Word
        result = convert_text_report_to_word(input_file, output_file)
        
        # Verify output file exists
        assert result.exists()
        assert output_file.exists()
        
        # Verify it's a valid Word document
        doc = Document(str(output_file))
        assert len(doc.paragraphs) > 0
        
        # Check for expected content in document
        full_text = '\n'.join(p.text for p in doc.paragraphs)
        assert 'Risk Assessment Report' in full_text
        assert 'TestAirline' in full_text
        assert 'Executive Summary' in full_text
        assert 'Financial Risks' in full_text


def test_convert_text_report_default_output_filename():
    """Test that default output filename uses .docx extension."""
    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        input_file = tmpdir_path / "test_report.txt"
        input_file.write_text("# Test Report\n\nSome content")
        
        # Convert without specifying output file
        result = convert_text_report_to_word(input_file)
        
        # Should use same name but with .docx extension
        expected_output = tmpdir_path / "test_report.docx"
        assert result == expected_output
        assert result.exists()


def test_title_metadata_precedes_toc_on_new_page(tmp_path):
    input_file = tmp_path / "report.txt"
    input_file.write_text(
        "# Risk Assessment Report: TestAirline\n"
        "Aircraft MSN: 1001 | Aircraft Variant: A320-214\n"
        "Deal Jurisdiction: Oman\n"
        "---\n\n"
        "## 1. Executive Summary\nSummary text.\n",
        encoding="utf-8",
    )

    doc = Document(str(convert_text_report_to_word(input_file)))
    paragraphs = doc.paragraphs
    texts = [paragraph.text for paragraph in paragraphs]
    title = texts.index("Risk Assessment Report: TestAirline")
    aircraft = texts.index("Aircraft MSN: 1001 | Aircraft Variant: A320-214")
    jurisdiction = texts.index("Deal Jurisdiction: Oman")
    toc = texts.index("TABLE OF CONTENTS")
    summary = texts.index("1. Executive Summary")

    assert title < aircraft < jurisdiction < toc < summary
    assert any(p._p.xpath('.//w:br[@w:type="page"]') for p in paragraphs[jurisdiction + 1:toc])
    assert any(p._p.xpath('.//w:br[@w:type="page"]') for p in paragraphs[toc + 1:summary])
    assert any("TOC" in "".join(p._p.xpath(".//w:instrText/text()")) for p in paragraphs[toc:summary])


def test_toc_is_added_when_report_ends_after_metadata(tmp_path):
    input_file = tmp_path / "report.txt"
    input_file.write_text("# Report\nAircraft MSN: 1001\n", encoding="utf-8")

    doc = Document(str(convert_text_report_to_word(input_file)))
    texts = [paragraph.text for paragraph in doc.paragraphs]
    metadata = texts.index("Aircraft MSN: 1001")
    toc = texts.index("TABLE OF CONTENTS")

    assert metadata < toc
    assert any(p._p.xpath('.//w:br[@w:type="page"]') for p in doc.paragraphs[metadata + 1:toc])


def test_main_sections_start_on_new_pages_without_extra_break_after_toc(tmp_path):
    input_file = tmp_path / "report.txt"
    input_file.write_text(
        "# Report\nAircraft MSN: 1001\n"
        "## First section\nContent.\n"
        "### Subsection\nMore content.\n"
        "## Second section\n## Third section\n",
        encoding="utf-8",
    )
    doc = Document(str(convert_text_report_to_word(input_file)))
    paragraphs = doc.paragraphs
    texts = [p.text for p in paragraphs]
    toc = texts.index("TABLE OF CONTENTS")
    first = texts.index("First section")
    subsection = paragraphs[texts.index("Subsection")]
    second = paragraphs[texts.index("Second section")]
    third = paragraphs[texts.index("Third section")]

    assert len([p for p in paragraphs[toc + 1:first] if p._p.xpath('.//w:br[@w:type="page"]')]) == 1
    assert not paragraphs[first].paragraph_format.page_break_before
    assert not subsection.paragraph_format.page_break_before
    assert second.paragraph_format.page_break_before is True
    assert third.paragraph_format.page_break_before is True


def test_main_heading_without_title_starts_a_new_page(tmp_path):
    input_file = tmp_path / "report.txt"
    input_file.write_text("Introductory text.\n## Section\nContent.\n", encoding="utf-8")
    doc = Document(str(convert_text_report_to_word(input_file)))
    heading = next(p for p in doc.paragraphs if p.text == "Section")
    assert heading.paragraph_format.page_break_before is True


def test_bold_markup_is_rendered_in_report_text_and_findings(tmp_path):
    input_file = tmp_path / "report.txt"
    input_file.write_text(
        "# Report **Title**\n"
        "Aircraft MSN: **1001**\n"
        "## Section **One**\n"
        "Before **first** and **second** after; unmatched **marker.\n"
        "- **Issue**: example.\n"
        "- [ANALYSIS] [RISK] A **material** risk. (2025) [Sources: F001]\n"
        "### Subsection **Details**\n",
        encoding="utf-8",
    )
    doc = Document(str(convert_text_report_to_word(input_file)))
    paragraphs = {p.text: p for p in doc.paragraphs if p.text}

    assert "Report Title" in paragraphs
    assert paragraphs["Aircraft MSN: 1001"].runs[1].bold is True
    assert any(r.text == "One" and r.bold for r in paragraphs["Section One"].runs)
    body = paragraphs["Before first and second after; unmatched **marker."]
    assert [(r.text, r.bold) for r in body.runs] == [
        ("Before ", None), ("first", True), (" and ", None), ("second", True),
        (" after; unmatched **marker.", None),
    ]
    assert any(r.text == "Issue" and r.bold for r in paragraphs["- Issue: example."].runs)
    finding = paragraphs["[ANALYSIS] [RISK] A material risk. (2025) [Sources: F001]"]
    material = next(r for r in finding.runs if r.text == "material")
    assert material.bold is True
    assert str(material.font.color.rgb) == "C00000"
    assert any(r.text == "Details" and r.bold for r in paragraphs["Subsection Details"].runs)


def test_bold_markup_in_sources_preserves_clickable_urls(tmp_path):
    input_file = tmp_path / "report.txt"
    input_file.write_text(
        "# Report\n## Section\n### Sources\n"
        "- F001: **A source**; https://example.com/source\n"
        "- F002: **https://example.com/bold**\n"
        "- **Unavailable**: no source.\n",
        encoding="utf-8",
    )
    doc = Document(str(convert_text_report_to_word(input_file)))
    source = next(p for p in doc.paragraphs if p.text.startswith("F001:"))
    assert any(r.text == "A source" and r.bold for r in source.runs)
    assert "https://example.com/source" in [rel.target_ref for rel in doc.part.rels.values() if rel.reltype.endswith("/hyperlink")]
    bold_link = next(p for p in doc.paragraphs if p.text.startswith("F002:"))
    assert bold_link._p.xpath('.//w:hyperlink/w:r/w:rPr/w:b')
    assert "https://example.com/bold" in [rel.target_ref for rel in doc.part.rels.values() if rel.reltype.endswith("/hyperlink")]
    unavailable = next(p for p in doc.paragraphs if p.text.startswith("Unavailable:"))
    assert any(r.text == "Unavailable" and r.bold for r in unavailable.runs)


def test_pipe_table_becomes_word_table_in_report_order(tmp_path):
    input_file = tmp_path / "report.txt"
    input_file.write_text(
        "# Report\n## Appendix\n### Jurisdictional Risk Benchmarking\n"
        "Introductory paragraph.\n"
        "| Country | CTC (25%) | Repossession (25%) | ICAO Safety (20%) | Bankruptcy/Litigation (15%) | Overall Score |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| **Oman** | 2.00 | 3.00 | 3.50 | 3.00 | 2.80 |\n"
        "| United States | 3.00 | 2.50 | 1.00 | 2.50 | 2.30 |\n"
        "| Ireland | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 |\n"
        "| United Arab Emirates | 2.00 | 3.00 | 3.00 | 3.00 | 2.80 |\n"
        "### Next section\nFurther content.\n",
        encoding="utf-8",
    )
    doc = Document(str(convert_text_report_to_word(input_file)))

    assert len(doc.tables) == 1
    table = doc.tables[0]
    assert [[cell.text for cell in row.cells] for row in table.rows] == [
        ["Country", "CTC (25%)", "Repossession (25%)", "ICAO Safety (20%)", "Bankruptcy/Litigation (15%)", "Overall Score"],
        ["Oman", "2.00", "3.00", "3.50", "3.00", "2.80"],
        ["United States", "3.00", "2.50", "1.00", "2.50", "2.30"],
        ["Ireland", "3.00", "3.00", "3.00", "3.00", "3.00"],
        ["United Arab Emirates", "2.00", "3.00", "3.00", "3.00", "2.80"],
    ]
    assert table.style.name == "Table Grid"
    assert all(cell.paragraphs[0].runs[0].bold for cell in table.rows[0].cells)
    assert table.cell(1, 0).paragraphs[0].runs[0].bold
    before = next(p for p in doc.paragraphs if p.text == "Introductory paragraph.")
    after = next(p for p in doc.paragraphs if p.text == "Next section")
    assert before._p.getnext() is table._tbl
    assert table._tbl.getnext() is after._p


def test_non_table_and_malformed_rows_remain_visible(tmp_path):
    input_file = tmp_path / "report.txt"
    input_file.write_text(
        "# Report\n## Section\n"
        "| Not a table | ordinary text |\n"
        "Following paragraph.\n"
        "| A | B |\n| --- | --- |\n| 1 | 2 |\n"
        "| Too | many | cells |\n"
        "After table.\n",
        encoding="utf-8",
    )
    doc = Document(str(convert_text_report_to_word(input_file)))
    assert len(doc.tables) == 1
    assert [[cell.text for cell in row.cells] for row in doc.tables[0].rows] == [["A", "B"], ["1", "2"]]
    texts = [p.text for p in doc.paragraphs]
    assert "| Not a table | ordinary text |" in texts
    assert "| Too | many | cells |" in texts
    assert "After table." in texts


def test_convert_handles_markdown_formatting():
    """Test that the converter properly handles markdown-style formatting."""
    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        input_file = tmpdir_path / "formatted_report.txt"
        output_file = tmpdir_path / "formatted_report.docx"
        
        test_content = """# Risk Assessment Report: FormattedAirline
Aircraft MSN: 2001 | Aircraft Variant: B737-800
Deal Jurisdiction: United States
---

## 1. Executive Summary
Formatted test report with multiple sections and findings.

- [FACT] [FAVORABLE] First finding with positive direction. (2025) [Sources: F001]
- [ANALYSIS] [NEUTRAL] Second finding with neutral direction. (2026) [Sources: F002]
- [FACT] [RISK] Third finding with risk direction. (2025-2026) [Sources: F001, F002]

### Sources
- F001: Source One — publisher1.com; published date unavailable; https://publisher1.com/article1
- F002: Source Two — publisher2.com; published date unavailable; https://publisher2.com/article2

## 2. Operational Risks

Analysis of operational factors.

- [ANALYSIS] [FAVORABLE] Strong maintenance partnerships. (2025) [Sources: O001]

### Sources
- O001: Operational Data — publisher3.com; published date unavailable; https://publisher3.com/ops
"""
        
        input_file.write_text(test_content, encoding='utf-8')
        result = convert_text_report_to_word(input_file, output_file)
        
        # Verify document structure
        doc = Document(str(result))
        
        # Check paragraph count (should have multiple paragraphs for structured content)
        assert len(doc.paragraphs) > 15
        
        # Verify heading hierarchy
        headings = [p for p in doc.paragraphs if p.style.name.startswith('Heading')]
        assert len(headings) >= 2


def test_convert_real_report_file():
    """Test conversion of an actual report file if available."""
    report_path = Path("C:/PROJECTS/risk-assessment-engine/report-salamair-6061.txt")
    
    if not report_path.exists():
        # Skip test if report file doesn't exist
        return
    
    with TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        output_file = tmpdir_path / "salamair-converted.docx"
        
        # Convert the actual report
        result = convert_text_report_to_word(report_path, output_file)
        
        # Verify output exists and is valid
        assert result.exists()
        doc = Document(str(result))
        
        # Check for expected content from the actual report
        full_text = '\n'.join(p.text for p in doc.paragraphs)
        assert 'SalamAir' in full_text
        assert 'A320' in full_text or 'A320-214' in full_text
        
        # Verify document has reasonable size (not empty)
        assert len(doc.paragraphs) > 50
