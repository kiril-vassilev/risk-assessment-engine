from datetime import date

from risk_assessment_engine.analysis import build_market_prompt
from risk_assessment_engine.graph import build_market_graph
from risk_assessment_engine.models import (
    AssessmentInput,
    Finding,
    MarketAnalysis,
    SectionAnalysis,
    SourceRecord,
)
from risk_assessment_engine.research import MARKET_QUERIES, collect_market_sources


class FakeMarketSearch:
    def __init__(self):
        self.queries = []

    def search(self, query, **kwargs):
        self.queries.append(query)
        return {
            "results": [
                {
                    "url": "https://example.com/market/",
                    "title": "Market Outlook",
                    "publisher": "Example Aviation Authority",
                    "content": "Demand and competition evidence.",
                }
            ]
        }


def make_market_analysis():
    return MarketAnalysis(
        market_risks=SectionAnalysis(
            summary="Market downside and favorable developments were assessed.",
            findings=[
                Finding(
                    statement="Competitive capacity may pressure yields.",
                    source_ids=["M001"],
                    kind="ANALYSIS",
                    category="competition",
                    direction="RISK",
                ),
                Finding(
                    statement="Demand growth may support network resilience.",
                    source_ids=["M001"],
                    kind="ANALYSIS",
                    category="demand",
                    direction="FAVORABLE",
                ),
            ],
        )
    )


class FakeMarketAnalysis:
    def analyze_market(self, prompt):
        assert "competition" in prompt
        assert "favorable developments" in prompt
        assert "foreign exchange" in prompt
        assert "geopolitics" in prompt
        return make_market_analysis()


def test_market_queries_cover_required_topics():
    query_text = " ".join(MARKET_QUERIES.values()).lower()
    for topic in (
        "competition",
        "demand",
        "fuel",
        "foreign exchange",
        "macroeconomic",
        "geopolitical",
        "consolidation",
        "route",
    ):
        assert topic in query_text


def test_market_sources_are_deduplicated_and_tagged():
    search = FakeMarketSearch()
    sources = collect_market_sources(search, "Example Airline", date(2026, 9, 11))
    assert len(search.queries) == len(MARKET_QUERIES)
    assert len(sources) == 1
    assert sources[0].source_id == "M001"
    assert sources[0].category == "competition"
    assert sources[0].accessed_date == date(2026, 9, 11)


def test_market_prompt_requires_risk_and_favorable_evidence():
    assessment_input = AssessmentInput(airline="Example Airline", msn="123", aircraft_variant="A320-214")
    source = SourceRecord(
        source_id="M001",
        url="https://example.com/market",
        title="Market Outlook",
        accessed_date=date(2026, 9, 11),
        category="competition",
        evidence="Demand and competition evidence.",
    )
    prompt = build_market_prompt(assessment_input, [source])
    assert "RISK" in prompt
    assert "FAVORABLE" in prompt
    assert "source_ids" in prompt
    assert "unavailable" in prompt
    assert "123" not in prompt


def test_compiled_market_graph_preserves_directions():
    result = build_market_graph(FakeMarketSearch(), FakeMarketAnalysis()).invoke(
        {"assessment_input": AssessmentInput(airline="Example Airline", msn="123", aircraft_variant="A320-214")}
    )
    assert result["market_sources"][0].source_id == "M001"
    assert "# Step 4 Market and Competitive Risk Assessment" in result["report"]
    assert "## 4. Market and Competitive Risks" in result["report"]
    assert "[RISK]" in result["report"]
    assert "[FAVORABLE]" in result["report"]
    assert "M001" in result["report"]