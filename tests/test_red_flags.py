from datetime import date

from risk_assessment_engine.analysis import build_red_flags_prompt
from risk_assessment_engine.graph import build_red_flags_graph
from risk_assessment_engine.models import (
    AircraftAnalysis,
    AircraftIdentity,
    AssessmentInput,
    FinancialAnalysis,
    Finding,
    MarketAnalysis,
    OperationalAnalysis,
    RedFlagItem,
    RedFlagsAnalysis,
    SectionAnalysis,
    SourceRecord,
)
from risk_assessment_engine.render import render_red_flags_report


class FakeMultiDomainSearch:
    def __init__(self):
        self.queries = []

    def search(self, query, **kwargs):
        self.queries.append(query)
        if "financial" in query or "revenue" in query or "debt" in query:
            url = "https://example.com/financial"
            prefix = "F"
        elif "operational" in query or "safety" in query or "maintenance" in query or "fleet" in query:
            url = "https://example.com/operational"
            prefix = "O"
        elif "competition" in query or "demand" in query or "fuel" in query:
            url = "https://example.com/market"
            prefix = "M"
        else:
            url = "https://example.com/aircraft"
            prefix = "A"

        return {
            "results": [
                {
                    "url": url,
                    "title": f"Report for {query[:20]}",
                    "publisher": "Aviation Records",
                    "content": f"Evidence snippet for {query} with MSN 6061 type: A320-214",
                }
            ]
        }


def make_sample_findings():
    fin_finding = Finding(
        statement="High leverage and tight liquidity with near-term debt maturities.",
        source_ids=["F001"],
        kind="FACT",
        category="liquidity",
        materiality="high",
        confidence="high",
    )
    op_finding = Finding(
        statement="Recent maintenance reliability issues and staffing shortages.",
        source_ids=["O001"],
        kind="FACT",
        category="maintenance",
        materiality="high",
        confidence="medium",
    )
    mkt_finding = Finding(
        statement="Intense LCC competition on core routes pressuring yields.",
        source_ids=["M001"],
        kind="ANALYSIS",
        category="competition",
        direction="RISK",
        materiality="high",
    )
    ac_finding = Finding(
        statement="Upcoming heavy maintenance check due within 6 months.",
        source_ids=["A001"],
        kind="FACT",
        category="history",
        scope="AIRCRAFT",
        materiality="high",
    )
    return fin_finding, op_finding, mkt_finding, ac_finding


def make_sample_red_flags():
    return RedFlagsAnalysis(
        summary="Synthesized 4 material red flags across financial, operational, market, and aircraft domains requiring lessor attention.",
        red_flags=[
            RedFlagItem(
                headline="Tight Liquidity & High Debt Burden",
                domain="financial",
                severity="critical",
                finding_statement="Near-term debt maturities create acute refinancing exposure.",
                source_ids=["F001"],
                rationale="High probability of lease payment default during market downturn.",
                scope="AIRLINE",
            ),
            RedFlagItem(
                headline="Workforce & Maintenance Constraints",
                domain="operational",
                severity="high",
                finding_statement="Staffing shortages impacting maintenance turnaround times.",
                source_ids=["O001"],
                rationale="Operational disruption threatens asset utilization and maintenance compliance.",
                scope="AIRLINE",
            ),
            RedFlagItem(
                headline="Yield Erosion from Aggressive Competitor Capacity",
                domain="market",
                severity="high",
                finding_statement="Competitors expanding overlapping routes by 25%.",
                source_ids=["M001"],
                rationale="Compresses operating margins required to service aircraft lease payments.",
                scope="AIRLINE",
            ),
            RedFlagItem(
                headline="Imminent Heavy Maintenance Event",
                domain="aircraft",
                severity="critical",
                finding_statement="Airframe C-check due within 6 months with unconfirmed reserve balances.",
                source_ids=["A001"],
                rationale="Unfunded major maintenance event presents immediate repossession/value risk.",
                scope="AIRCRAFT",
            ),
        ],
    )


class FakeMultiDomainAnalysis:
    def analyze_financial(self, prompt):
        f, _, _, _ = make_sample_findings()
        return FinancialAnalysis(
            financial_risks=SectionAnalysis(summary="Financial summary", findings=[f])
        )

    def analyze_operational(self, prompt):
        _, o, _, _ = make_sample_findings()
        return OperationalAnalysis(
            operational_risks=SectionAnalysis(summary="Operational summary", findings=[o])
        )

    def analyze_market(self, prompt):
        _, _, m, _ = make_sample_findings()
        return MarketAnalysis(
            market_risks=SectionAnalysis(summary="Market summary", findings=[m])
        )

    def analyze_aircraft(self, prompt):
        _, _, _, a = make_sample_findings()
        identity = AircraftIdentity(
            msn="6061",
            aircraft_type="A320-214",
            aircraft_variant="A320-214",
            confidence="high",
            supporting_source_ids=["A001"],
        )
        return AircraftAnalysis(
            identity=identity,
            airline_context=SectionAnalysis(summary="Context", findings=[]),
            aircraft_risks=SectionAnalysis(summary="Aircraft specific", findings=[a]),
            aircraft_type_risks=SectionAnalysis(summary="Type level", findings=[]),
        )

    def analyze_red_flags(self, prompt):
        assert "Domain Findings JSON" in prompt
        assert "3–6" in prompt or "3-6" in prompt
        assert "financial_findings" in prompt
        assert "operational_findings" in prompt
        assert "market_findings" in prompt
        assert "aircraft_findings" in prompt
        return make_sample_red_flags()


def test_build_red_flags_prompt_contains_all_domains_and_metadata():
    inp = AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214")
    f, o, m, a = make_sample_findings()
    identity = AircraftIdentity(msn="6061", aircraft_type="A320-214", confidence="high")

    prompt = build_red_flags_prompt(
        inp,
        financial_findings=[f],
        operational_findings=[o],
        market_findings=[m],
        aircraft_findings=[a],
        identity=identity,
    )

    assert "SalamAir" in prompt
    assert "6061" in prompt
    assert "A320-214" in prompt
    assert "Tight liquidity" in prompt or "liquidity" in prompt
    assert "F001" in prompt
    assert "O001" in prompt
    assert "M001" in prompt
    assert "A001" in prompt
    assert "3–6" in prompt or "3-6" in prompt


def test_red_flags_analysis_model_validates_items():
    analysis = make_sample_red_flags()
    assert len(analysis.red_flags) == 4
    for flag in analysis.red_flags:
        assert flag.severity in ("high", "critical")
        assert flag.domain in ("financial", "operational", "market", "aircraft")
        assert len(flag.source_ids) > 0


def test_render_red_flags_report_formats_headings_and_sources():
    inp = AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214")
    analysis = make_sample_red_flags()
    sources = [
        SourceRecord(
            source_id="F001",
            url="https://example.com/financial",
            title="Financial Statement",
            publisher="Securities Commission",
            accessed_date=date(2026, 9, 13),
            category="financial_filings",
            evidence="High debt levels.",
        ),
        SourceRecord(
            source_id="O001",
            url="https://example.com/operational",
            title="Operations Review",
            publisher="Aviation Authority",
            accessed_date=date(2026, 9, 13),
            category="maintenance_reliability",
            evidence="Staffing shortage.",
        ),
        SourceRecord(
            source_id="M001",
            url="https://example.com/market",
            title="Market Review",
            publisher="Industry Intelligence",
            accessed_date=date(2026, 9, 13),
            category="competition",
            evidence="LCC competition.",
        ),
        SourceRecord(
            source_id="A001",
            url="https://example.com/aircraft",
            title="Airframe History",
            publisher="Fleet Registry",
            accessed_date=date(2026, 9, 13),
            category="history",
            evidence="C-check due.",
        ),
        SourceRecord(
            source_id="UNUSED001",
            url="https://example.com/unused",
            title="Unused Article",
            publisher="News",
            accessed_date=date(2026, 9, 13),
            category="events",
            evidence="General news.",
        ),
    ]

    report = render_red_flags_report(inp, analysis, sources)

    assert "# Step 6 Red Flags Assessment: SalamAir" in report
    assert "## 5. Red Flags" in report
    assert "### Red Flag 1: [CRITICAL] Tight Liquidity & High Debt Burden" in report
    assert "### Red Flag 4: [CRITICAL] Imminent Heavy Maintenance Event" in report
    assert "### Sources" in report
    assert "F001" in report
    assert "O001" in report
    assert "M001" in report
    assert "A001" in report
    assert "UNUSED001" not in report
    assert "## Scope Deferred" in report


def test_compiled_red_flags_graph_runs_end_to_end():
    search_client = FakeMultiDomainSearch()
    analysis_client = FakeMultiDomainAnalysis()
    graph = build_red_flags_graph(search_client, analysis_client)

    result = graph.invoke(
        {
            "assessment_input": AssessmentInput(
                airline="SalamAir", msn="6061", aircraft_variant="A320-214"
            )
        }
    )

    assert "red_flags_analysis" in result
    assert len(result["red_flags_analysis"].red_flags) == 4
    assert "# Step 6 Red Flags Assessment: SalamAir" in result["report"]
    assert "## 5. Red Flags" in result["report"]
    assert "[CRITICAL] Tight Liquidity & High Debt Burden" in result["report"]
    assert "F001" in result["report"]
