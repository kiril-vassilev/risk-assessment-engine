from datetime import date

from risk_assessment_engine.analysis import build_assessment_view_prompt
from risk_assessment_engine.graph import build_assessment_view_graph
from risk_assessment_engine.models import (
    AircraftAnalysis,
    AircraftIdentity,
    AssessmentInput,
    AssessmentViewAnalysis,
    BenchmarkScore,
    CountryRiskAnalysis,
    FinancialAnalysis,
    Finding,
    MarketAnalysis,
    OperationalAnalysis,
    RedFlagItem,
    RedFlagsAnalysis,
    SectionAnalysis,
    SourceRecord,
)
from risk_assessment_engine.render import render_assessment_view_report


class FakeFullEngineSearch:
    def __init__(self):
        self.queries = []

    def search(self, query, **kwargs):
        self.queries.append(query)
        if any(k in query for k in ("financial", "revenue", "debt", "profit", "liquidity")):
            url = "https://example.com/financial"
        elif any(k in query for k in ("operational", "fleet", "maintenance", "safety")):
            url = "https://example.com/operational"
        elif any(k in query for k in ("competition", "demand", "fuel")):
            url = "https://example.com/market"
        elif any(k in query for k in ("MSN", "engine", "remarketing")):
            url = "https://example.com/aircraft"
        else:
            url = "https://example.com/country"

        return {
            "results": [
                {
                    "url": url,
                    "title": f"Report for {query[:25]}",
                    "publisher": "Aviation Registry & Intelligence",
                    "content": f"Evidence for {query} with MSN 6061 type: A320-214 in Oman.",
                }
            ]
        }


def make_sample_assessment_view():
    return AssessmentViewAnalysis(
        recommendation="SUITABLE_SUBJECT_TO_CONDITIONS",
        headline="SalamAir represents an expanding regional LCC with manageable credit risk, strong A320-214 secondary market liquidity, and solid Cape Town repossession protections in Oman.",
        airline_credit_factors="Moderate financial leverage and positive operating cash flow offset by thin net margins and fuel cost volatility.",
        asset_quality_factors="A320-214 airframe sits in the deepest global narrowbody liquidity pool with broad operator demand and predictable part-out economics.",
        market_factors="Expanding regional GCC leisure and expatriate routes with increasing competitive pressure from Gulf ULCC peers.",
        jurisdiction_factors="Oman's Cape Town Convention accession (Alternative A declarations) and reliable CAA IDERA record provide effective creditor repossession remedies.",
        conditions_and_mitigants=[
            "3 months cash security deposit or equivalent Letter of Credit",
            "Monthly maintenance reserve collections for airframe and engine overhauls",
            "Irrevocable De-Registration and Export Request Authorization (IDERA) registered with CAA Oman prior to delivery",
        ],
        rationale="The transaction is supported by high asset liquidity and solid repossession rights in Oman, but requires customary credit and maintenance security mitigants given airline-level margin volatility.",
        cited_source_ids=["F001", "O001", "M001", "A001", "C001"],
    )


class FakeFullEngineAnalysisClient:
    def analyze_financial(self, prompt):
        f = Finding(statement="Financial findings", source_ids=["F001"], kind="FACT", category="financial")
        return FinancialAnalysis(financial_risks=SectionAnalysis(summary="Fin", findings=[f]))

    def analyze_operational(self, prompt):
        o = Finding(statement="Operational findings", source_ids=["O001"], kind="FACT", category="operational")
        return OperationalAnalysis(operational_risks=SectionAnalysis(summary="Op", findings=[o]))

    def analyze_market(self, prompt):
        m = Finding(statement="Market findings", source_ids=["M001"], kind="FACT", category="market")
        return MarketAnalysis(market_risks=SectionAnalysis(summary="Mkt", findings=[m]))

    def analyze_aircraft(self, prompt):
        a = Finding(statement="Aircraft findings", source_ids=["A001"], kind="FACT", category="history", scope="AIRCRAFT")
        identity = AircraftIdentity(msn="6061", aircraft_type="A320-214", aircraft_variant="A320-214", confidence="high", supporting_source_ids=["A001"])
        return AircraftAnalysis(
            identity=identity,
            airline_context=SectionAnalysis(summary="Ctx", findings=[]),
            aircraft_risks=SectionAnalysis(summary="Ac", findings=[a]),
            aircraft_type_risks=SectionAnalysis(summary="Type", findings=[]),
        )

    def analyze_red_flags(self, prompt):
        rf = RedFlagItem(
            headline="Thin Margin Vulnerability",
            domain="financial",
            severity="high",
            finding_statement="Thin operating margins exposed to fuel spikes.",
            source_ids=["F001"],
            rationale="Increases payment default risk.",
            scope="AIRLINE",
        )
        return RedFlagsAnalysis(summary="RF summary", red_flags=[rf])

    def analyze_country(self, prompt):
        c = Finding(statement="Country findings", source_ids=["C001"], kind="FACT", category="cape_town", scope="JURISDICTION")
        sec = SectionAnalysis(summary="Sec", findings=[c])
        return CountryRiskAnalysis(
            country_name="Oman",
            jurisdiction_rationale="Primary domicile.",
            benchmarking_summary="Benchmarking summary.",
            benchmarking_scores=[
                BenchmarkScore(country="Oman", ctc_score=2.0, repossession_score=3.0, icao_safety_score=3.0, bankruptcy_score=4.0, overall_score=2.85)
            ],
            cape_town_convention=sec,
            repossession_risk=sec,
            icao_safety=sec,
            bankruptcy_law=sec,
            geopolitical_assessment=sec,
        )

    def analyze_assessment_view(self, prompt):
        assert "Comprehensive Assessment Evidence JSON" in prompt
        assert "SUITABLE_FOR_PURCHASE_LEASE" in prompt
        assert "SUITABLE_SUBJECT_TO_CONDITIONS" in prompt
        assert "NOT_SUITABLE" in prompt
        assert "financial_findings" in prompt
        assert "red_flags" in prompt
        assert "country_risk" in prompt
        return make_sample_assessment_view()


def test_build_assessment_view_prompt_contains_all_domains_and_metadata():
    inp = AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214", jurisdiction="Oman")
    prompt = build_assessment_view_prompt(
        inp,
        financial_findings=[Finding(statement="Fin data", source_ids=["F001"], kind="FACT", category="fin")],
        operational_findings=[Finding(statement="Op data", source_ids=["O001"], kind="FACT", category="op")],
        market_findings=[Finding(statement="Mkt data", source_ids=["M001"], kind="FACT", category="mkt")],
        aircraft_findings=[Finding(statement="Ac data", source_ids=["A001"], kind="FACT", category="ac", scope="AIRCRAFT")],
        red_flags=[RedFlagItem(headline="RF headline", domain="financial", severity="high", finding_statement="issue", rationale="impact", source_ids=["F001"])],
        country_analysis=None,
        identity=AircraftIdentity(msn="6061", aircraft_type="A320-214", confidence="high"),
    )

    assert "SalamAir" in prompt
    assert "6061" in prompt
    assert "A320-214" in prompt
    assert "SUITABLE_SUBJECT_TO_CONDITIONS" in prompt
    assert "financial_findings" in prompt
    assert "red_flags" in prompt


def test_render_assessment_view_report_formats_all_subsections():
    inp = AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214")
    analysis = make_sample_assessment_view()
    sources = [
        SourceRecord(
            source_id="F001",
            url="https://example.com/financial",
            title="Financial Statement",
            publisher="Securities Commission",
            accessed_date=date(2026, 9, 13),
            category="financial_filings",
            evidence="Financial evidence.",
        ),
        SourceRecord(
            source_id="C001",
            url="https://example.com/country",
            title="Oman Law",
            publisher="CAA",
            accessed_date=date(2026, 9, 13),
            category="cape_town",
            evidence="Cape town evidence.",
        ),
    ]

    report = render_assessment_view_report(inp, analysis, sources)

    assert "# Step 8 Assessment View: SalamAir" in report
    assert "## 7. Assessment View (Recommendation)" in report
    assert "Suitable for Purchase / Lease Investment Subject to Conditions & Approvals" in report
    assert "### Key Investment Factors" in report
    assert "- **Airline Credit & Operational Capacity**:" in report
    assert "- **Aircraft Asset Liquidity & Remarketability**:" in report
    assert "- **Market & Commercial Dynamics**:" in report
    assert "- **Jurisdictional & Repossession Enforceability**:" in report
    assert "### Recommended Conditions & Approval Mitigants" in report
    assert "3 months cash security deposit" in report
    assert "### Synthesis & Investment Rationale" in report
    assert "### Sources" in report
    assert "F001" in report
    assert "C001" in report


def test_compiled_assessment_view_graph_runs_end_to_end():
    search_client = FakeFullEngineSearch()
    analysis_client = FakeFullEngineAnalysisClient()
    graph = build_assessment_view_graph(search_client, analysis_client)

    result = graph.invoke(
        {
            "assessment_input": AssessmentInput(
                airline="SalamAir", msn="6061", aircraft_variant="A320-214", jurisdiction="Oman"
            )
        }
    )

    assert "assessment_view_analysis" in result
    assert result["assessment_view_analysis"].recommendation == "SUITABLE_SUBJECT_TO_CONDITIONS"
    assert "# Step 8 Assessment View: SalamAir" in result["report"]
    assert "## 7. Assessment View (Recommendation)" in result["report"]
    assert "Suitable for Purchase / Lease Investment Subject to Conditions & Approvals" in result["report"]
    assert "### Recommended Conditions & Approval Mitigants" in result["report"]
