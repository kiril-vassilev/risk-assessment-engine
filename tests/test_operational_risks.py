from datetime import date

from risk_assessment_engine.analysis import build_operational_prompt
from risk_assessment_engine.graph import build_operational_graph
from risk_assessment_engine.models import (
    AssessmentInput,
    Finding,
    OperationalAnalysis,
    SectionAnalysis,
    SourceRecord,
)
from risk_assessment_engine.research import OPERATIONAL_QUERIES, collect_operational_sources


class FakeOperationalSearch:
    def __init__(self):
        self.queries = []

    def search(self, query, **kwargs):
        self.queries.append(query)
        return {
            "results": [
                {
                    "url": "https://example.com/operations/",
                    "title": "Operations Review",
                    "publisher": "Example Aviation Authority",
                    "content": "Fleet and safety evidence.",
                }
            ]
        }


def make_operational_analysis():
    return OperationalAnalysis(
        operational_risks=SectionAnalysis(
            summary="Fleet, safety, maintenance, compliance, and workforce evidence was assessed.",
            findings=[
                Finding(
                    statement="The operator reported fleet utilization data.",
                    source_ids=["O001"],
                    kind="FACT",
                    category="fleet_utilization",
                    date_context="latest reported period",
                ),
                Finding(
                    statement="Operational resilience requires continued monitoring.",
                    source_ids=["O001"],
                    kind="ANALYSIS",
                    category="reliability",
                ),
            ],
        )
    )


class FakeOperationalAnalysis:
    def analyze_operational(self, prompt):
        assert "maintenance" in prompt
        assert "regulatory compliance" in prompt
        assert "workforce" in prompt
        assert "aircraft identified by the MSN" in prompt
        return make_operational_analysis()


def test_operational_queries_cover_required_topics():
    query_text = " ".join(OPERATIONAL_QUERIES.values()).lower()
    for topic in (
        "fleet",
        "utilization",
        "maintenance",
        "safety",
        "regulator",
        "deliveries",
        "workforce",
    ):
        assert topic in query_text


def test_operational_sources_are_deduplicated_and_tagged():
    search = FakeOperationalSearch()
    sources = collect_operational_sources(search, "Example Airline", date(2026, 9, 11))
    assert len(search.queries) == len(OPERATIONAL_QUERIES)
    assert len(sources) == 1
    assert sources[0].source_id == "O001"
    assert sources[0].category == "fleet_utilization"
    assert sources[0].accessed_date == date(2026, 9, 11)


def test_operational_prompt_requires_grounded_dated_evidence():
    assessment_input = AssessmentInput(airline="Example Airline", msn="123", aircraft_variant="A320-214")
    source = SourceRecord(
        source_id="O001",
        url="https://example.com/operations",
        title="Operations Review",
        accessed_date=date(2026, 9, 11),
        category="fleet_utilization",
        evidence="Fleet and safety evidence.",
    )
    prompt = build_operational_prompt(assessment_input, [source])
    assert "source_ids" in prompt
    assert "unavailable" in prompt
    assert "aircraft identified by the MSN" in prompt


def test_compiled_operational_graph_renders_operational_risks():
    result = build_operational_graph(FakeOperationalSearch(), FakeOperationalAnalysis()).invoke(
        {"assessment_input": AssessmentInput(airline="Example Airline", msn="123", aircraft_variant="A320-214")}
    )
    assert result["operational_sources"][0].source_id == "O001"
    assert "# Step 3 Operational Risk Assessment" in result["report"]
    assert "## 3. Operational Risks" in result["report"]
    assert "O001" in result["report"]
    assert "fleet utilization data" in result["report"]