from datetime import date

from risk_assessment_engine.models import AirlineAnalysis, AssessmentInput, Finding, SectionAnalysis, SourceRecord
from risk_assessment_engine.graph import build_airline_graph
from risk_assessment_engine.render import render_airline_report
from risk_assessment_engine.research import collect_airline_sources


class FakeSearch:
    def search(self, query, **kwargs):
        return {"results": [{"url": "https://example.com/report/", "title": "Report", "content": query}]}

    def extract(self, urls, **kwargs):
        return {}


class FakeAnalysis:
    def analyze_airline(self, prompt):
        assert "Example" in prompt
        return make_analysis()


def make_analysis():
    finding = Finding(statement="Revenue improved.", source_ids=["S001"], kind="FACT", category="financial")
    section = SectionAnalysis(summary="Evidence was reviewed.", findings=[finding])
    return AirlineAnalysis(
        executive_summary=section,
    )


def test_input_rejects_blank_values():
    try:
        AssessmentInput(airline=" ", msn="123", aircraft_variant="A320-214")
    except ValueError as error:
        assert "blank" in str(error)
    else:
        raise AssertionError("blank airline should be rejected")

    try:
        AssessmentInput(airline="Example", msn="123", aircraft_variant=" ")
    except ValueError as error:
        assert "blank" in str(error)
    else:
        raise AssertionError("blank aircraft_variant should be rejected")


def test_sources_are_deduplicated():
    sources = collect_airline_sources(FakeSearch(), "Example Airline", date(2026, 9, 11))
    assert len(sources) == 1
    assert sources[0].url == "https://example.com/report"


def test_renderer_contains_required_sections_and_sources():
    source = SourceRecord(
        source_id="S001",
        url="https://example.com/report",
        title="Report",
        publisher="Example",
        accessed_date=date(2026, 9, 11),
        category="financial",
        evidence="Revenue improved.",
    )
    report = render_airline_report(AssessmentInput(airline="Example", msn="123", aircraft_variant="A320-214"), make_analysis(), [source])
    assert "## 1. Executive Summary" in report
    assert "Financial Risk" in report
    assert "### Sources" in report
    assert "S001" in report
    assert "aircraft analysis pending" in report


def test_compiled_graph_runs_with_injected_clients():
    graph = build_airline_graph(FakeSearch(), FakeAnalysis())
    result = graph.invoke({"assessment_input": AssessmentInput(airline="Example", msn="123", aircraft_variant="A320-214")})
    assert result["assessment_input"].msn == "123"
    assert result["sources"][0].source_id == "S001"
    assert "## 1. Executive Summary" in result["report"]