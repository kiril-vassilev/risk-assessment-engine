from datetime import date

from risk_assessment_engine.analysis import build_financial_prompt
from risk_assessment_engine.graph import build_financial_graph
from risk_assessment_engine.models import (
    AssessmentInput,
    FinancialAnalysis,
    Finding,
    SectionAnalysis,
    SourceRecord,
)
from risk_assessment_engine.research import FINANCIAL_QUERIES, collect_financial_sources


class FakeFinancialSearch:
    def __init__(self):
        self.queries = []

    def search(self, query, **kwargs):
        self.queries.append(query)
        return {
            "results": [
                {
                    "url": "https://example.com/annual-report/",
                    "title": "Annual Report",
                    "publisher": "Example Investor Relations",
                    "content": "Revenue and liquidity evidence.",
                }
            ]
        }


def make_financial_analysis():
    return FinancialAnalysis(
        financial_risks=SectionAnalysis(
            summary="Liquidity and profitability were assessed from retained financial evidence.",
            findings=[
                Finding(
                    statement="Revenue increased during the reported period.",
                    source_ids=["F001"],
                    kind="FACT",
                    category="revenue",
                    date_context="latest reported period",
                ),
                Finding(
                    statement="Lease-support capacity requires continued monitoring.",
                    source_ids=["F001"],
                    kind="ANALYSIS",
                    category="liquidity",
                ),
            ],
        )
    )


class FakeFinancialAnalysis:
    def analyze_financial(self, prompt):
        assert "cash flow" in prompt
        assert "refinancing" in prompt
        return make_financial_analysis()


def test_financial_queries_cover_required_topics():
    query_text = " ".join(FINANCIAL_QUERIES.values()).lower()
    for topic in ("revenue", "profit", "cash flow", "liquidity", "debt", "refinancing"):
        assert topic in query_text


def test_financial_sources_are_deduplicated_and_tagged():
    search = FakeFinancialSearch()
    sources = collect_financial_sources(search, "Example Airline", date(2026, 9, 11))
    assert len(search.queries) == len(FINANCIAL_QUERIES)
    assert len(sources) == 1
    assert sources[0].source_id == "F001"
    assert sources[0].category == "financial_filings"
    assert sources[0].accessed_date == date(2026, 9, 11)


def test_financial_prompt_requires_evidence_grounding():
    assessment_input = AssessmentInput(airline="Example Airline", msn="123", aircraft_variant="A320-214")
    source = SourceRecord(
        source_id="F001",
        url="https://example.com/annual-report",
        title="Annual Report",
        accessed_date=date(2026, 9, 11),
        category="financial_filings",
        evidence="Revenue and liquidity evidence.",
    )
    prompt = build_financial_prompt(assessment_input, [source])
    assert "source_ids" in prompt
    assert "unavailable" in prompt
    assert "123" not in prompt


def test_compiled_financial_graph_renders_financial_risks():
    result = build_financial_graph(FakeFinancialSearch(), FakeFinancialAnalysis()).invoke(
        {"assessment_input": AssessmentInput(airline="Example Airline", msn="123", aircraft_variant="A320-214")}
    )
    assert result["financial_sources"][0].source_id == "F001"
    assert "# Step 2 Financial Risk Assessment" in result["report"]
    assert "## 2. Financial Risks" in result["report"]
    assert "F001" in result["report"]
    assert "Revenue increased" in result["report"]