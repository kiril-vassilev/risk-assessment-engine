from datetime import date

from risk_assessment_engine.analysis import build_executive_summary_prompt
from risk_assessment_engine.graph import build_final_report_graph
from risk_assessment_engine.models import (
    AircraftAnalysis,
    AircraftIdentity,
    AssessmentInput,
    AssessmentViewAnalysis,
    BenchmarkScore,
    CountryRiskAnalysis,
    FinalReportAnalysis,
    FinancialAnalysis,
    Finding,
    MarketAnalysis,
    OperationalAnalysis,
    RedFlagItem,
    RedFlagsAnalysis,
    SectionAnalysis,
    SourceRecord,
)
from risk_assessment_engine.render import render_final_report


class FakeFinalReportSearch:
    def __init__(self):
        self.queries = []

    def search(self, query, **kwargs):
        self.queries.append(query)
        if any(k in query for k in ("financial", "revenue", "debt", "profit", "liquidity")):
            url = "https://example.com/financial"
            prefix = "F"
        elif any(k in query for k in ("operational", "fleet", "maintenance", "safety")):
            url = "https://example.com/operational"
            prefix = "O"
        elif any(k in query for k in ("competition", "demand", "fuel")):
            url = "https://example.com/market"
            prefix = "M"
        elif any(k in query for k in ("MSN", "engine", "remarketing")):
            url = "https://example.com/aircraft"
            prefix = "A"
        else:
            url = "https://example.com/country"
            prefix = "C"

        return {
            "results": [
                {
                    "url": url,
                    "title": f"Aviation Data for {query[:25]}",
                    "publisher": "Aviation Registry & Intelligence",
                    "content": f"Evidence snippet for {query} referencing MSN 6061 and A320-214.",
                }
            ]
        }


def make_full_test_analysis():
    f_finding = Finding(
        statement="Revenue of $150M with operating margin of 4.2%.",
        source_ids=["F001"],
        kind="FACT",
        category="revenue",
        date_context="FY2025",
    )
    o_finding = Finding(
        statement="Fleet of 14 Airbus A320/A321 family aircraft with 99.2% dispatch reliability.",
        source_ids=["O001"],
        kind="FACT",
        category="fleet_utilization",
        date_context="2025-2026",
    )
    m_finding = Finding(
        statement="Regional route demand expanding at 8% CAGR across GCC destinations.",
        source_ids=["M001"],
        kind="ANALYSIS",
        category="demand",
        direction="FAVORABLE",
        date_context="2026",
    )
    a_finding = Finding(
        statement="CFM56-5B4 engine configuration with 4,200 flight cycles remaining until shop visit.",
        source_ids=["A001"],
        kind="FACT",
        category="history",
        scope="AIRCRAFT",
        date_context="Q1 2026",
    )
    type_finding = Finding(
        statement="Global in-service A320-200 fleet exceeds 4,000 units with liquid secondary trading.",
        source_ids=["A002"],
        kind="FACT",
        category="type_market",
        scope="AIRCRAFT_TYPE",
        date_context="2026",
    )
    c_finding = Finding(
        statement="Oman ratified Cape Town Convention with standard Alternative A qualifying declarations.",
        source_ids=["C001"],
        kind="FACT",
        category="cape_town",
        scope="JURISDICTION",
        date_context="2020",
    )
    exec_finding = Finding(
        statement="SalamAir presents a viable regional LCC credit with liquid A320-214 asset collateral.",
        source_ids=["F001", "A001"],
        kind="ANALYSIS",
        category="summary",
        direction="FAVORABLE",
    )

    identity = AircraftIdentity(
        msn="6061",
        aircraft_type="A320-214",
        aircraft_variant="A320-214",
        engine_configuration="CFM56-5B4",
        current_operator="SalamAir",
        current_owner="Avolon",
        confidence="high",
        supporting_source_ids=["A001"],
    )

    c_sec = SectionAnalysis(summary="Country Risk section summary", findings=[c_finding])
    country_an = CountryRiskAnalysis(
        country_name="Oman",
        jurisdiction_rationale="Primary domicile and registration jurisdiction.",
        benchmarking_summary="Oman scores in the mid-range of aviation finance jurisdictions.",
        benchmarking_scores=[
            BenchmarkScore(country="United States", ctc_score=1.0, repossession_score=1.0, icao_safety_score=1.0, bankruptcy_score=2.0, overall_score=1.15),
            BenchmarkScore(country="Oman", ctc_score=2.0, repossession_score=3.0, icao_safety_score=3.0, bankruptcy_score=4.0, overall_score=2.85),
        ],
        cape_town_convention=c_sec,
        repossession_risk=c_sec,
        icao_safety=c_sec,
        bankruptcy_law=c_sec,
        geopolitical_assessment=c_sec,
    )

    rf = RedFlagItem(
        headline="Fuel Volatility Exposure on Thin Net Margin",
        domain="financial",
        severity="high",
        finding_statement="Unhedged fuel cost sensitivity on modest operating margin.",
        source_ids=["F001"],
        rationale="Increases risk of lease payment delays during fuel price spikes.",
        scope="AIRLINE",
    )

    av = AssessmentViewAnalysis(
        recommendation="SUITABLE_SUBJECT_TO_CONDITIONS",
        headline="Asset is suitable for lease investment with standard security deposit and maintenance reserve covenants.",
        airline_credit_factors="Moderate financial leverage and positive operating cash flow.",
        asset_quality_factors="High secondary market liquidity for A320-214.",
        market_factors="Resilient regional GCC passenger demand.",
        jurisdiction_factors="Cape Town Alternative A protections in Oman.",
        conditions_and_mitigants=["3 months security deposit", "Monthly maintenance reserves", "IDERA filing"],
        rationale="Solid asset collateral and legal remedies mitigate airline-level credit exposure.",
        cited_source_ids=["F001", "A001", "C001"],
    )

    return FinalReportAnalysis(
        executive_summary=SectionAnalysis(
            summary="SalamAir is an Omani low-cost carrier operating narrowbody aircraft across GCC and Asian routes. The proposed A320-214 asset offers high secondary market liquidity and robust Cape Town legal protections, subject to customary security structuring.",
            findings=[exec_finding],
        ),
        financial_analysis=FinancialAnalysis(
            financial_risks=SectionAnalysis(summary="Financial risk analysis summary.", findings=[f_finding])
        ),
        operational_analysis=OperationalAnalysis(
            operational_risks=SectionAnalysis(summary="Operational risk analysis summary.", findings=[o_finding])
        ),
        market_analysis=MarketAnalysis(
            market_risks=SectionAnalysis(summary="Market risk analysis summary.", findings=[m_finding])
        ),
        aircraft_analysis=AircraftAnalysis(
            identity=identity,
            airline_context=SectionAnalysis(summary="Airline context", findings=[]),
            aircraft_risks=SectionAnalysis(summary="Aircraft specific risk", findings=[a_finding]),
            aircraft_type_risks=SectionAnalysis(summary="Aircraft type liquidity", findings=[type_finding]),
        ),
        red_flags_analysis=RedFlagsAnalysis(
            summary="Synthesized 1 material red flag requiring lessor monitoring.",
            red_flags=[rf],
        ),
        assessment_view_analysis=av,
        country_analysis=country_an,
    )


class FakeFinalReportAnalysisClient:
    def analyze_financial(self, prompt):
        return make_full_test_analysis().financial_analysis

    def analyze_operational(self, prompt):
        return make_full_test_analysis().operational_analysis

    def analyze_market(self, prompt):
        return make_full_test_analysis().market_analysis

    def analyze_aircraft(self, prompt):
        return make_full_test_analysis().aircraft_analysis

    def analyze_red_flags(self, prompt):
        return make_full_test_analysis().red_flags_analysis

    def analyze_country(self, prompt):
        return make_full_test_analysis().country_analysis

    def analyze_assessment_view(self, prompt):
        return make_full_test_analysis().assessment_view_analysis

    def analyze_executive_summary(self, prompt):
        assert "Full Assessment Findings JSON" in prompt
        assert "Section 1: Executive Summary" in prompt
        return make_full_test_analysis().executive_summary


def test_build_executive_summary_prompt_contains_all_synthesized_sections():
    inp = AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214", jurisdiction="Oman")
    analysis = make_full_test_analysis()

    prompt = build_executive_summary_prompt(
        inp,
        financial_findings=analysis.financial_analysis.financial_risks.findings,
        operational_findings=analysis.operational_analysis.operational_risks.findings,
        market_findings=analysis.market_analysis.market_risks.findings,
        aircraft_findings=analysis.aircraft_analysis.aircraft_risks.findings,
        red_flags=analysis.red_flags_analysis.red_flags,
        assessment_view=analysis.assessment_view_analysis,
        country_analysis=analysis.country_analysis,
        identity=analysis.aircraft_analysis.identity,
    )

    assert "SalamAir" in prompt
    assert "6061" in prompt
    assert "A320-214" in prompt
    assert "Section 1: Executive Summary" in prompt
    assert "Full Assessment Findings JSON" in prompt


def test_render_final_report_generates_all_sections_and_sources():
    inp = AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214", jurisdiction="Oman")
    analysis = make_full_test_analysis()
    sources = [
        SourceRecord(
            source_id="F001",
            url="https://example.com/financial",
            title="Financial Statement",
            publisher="Securities Commission",
            accessed_date=date(2026, 9, 13),
            category="financial_filings",
            evidence="Financial revenue details.",
        ),
        SourceRecord(
            source_id="O001",
            url="https://example.com/operational",
            title="Operations Review",
            publisher="Aviation Authority",
            accessed_date=date(2026, 9, 13),
            category="fleet_utilization",
            evidence="Fleet data.",
        ),
        SourceRecord(
            source_id="M001",
            url="https://example.com/market",
            title="Market Review",
            publisher="Industry Intelligence",
            accessed_date=date(2026, 9, 13),
            category="demand",
            evidence="Demand data.",
        ),
        SourceRecord(
            source_id="A001",
            url="https://example.com/aircraft",
            title="Airframe Registry",
            publisher="Registry",
            accessed_date=date(2026, 9, 13),
            category="history",
            evidence="Engine details.",
        ),
        SourceRecord(
            source_id="A002",
            url="https://example.com/type",
            title="A320 Type Liquidity",
            publisher="IBA / Cirium",
            accessed_date=date(2026, 9, 13),
            category="type_market",
            evidence="Type fleet size.",
        ),
        SourceRecord(
            source_id="C001",
            url="https://example.com/country",
            title="Oman CAA Law",
            publisher="CAA",
            accessed_date=date(2026, 9, 13),
            category="cape_town",
            evidence="Cape Town details.",
        ),
    ]

    report = render_final_report(inp, analysis, sources)

    # Validate all 7 numbered sections + Appendix A
    assert "# Risk Assessment Report: SalamAir" in report
    assert "## 1. Executive Summary" in report
    assert "## 2. Financial Risks" in report
    assert "## 3. Operational Risks" in report
    assert "## 4. Market and Competitive Risks" in report
    assert "## 5. Red Flags" in report
    assert "## 6. Aircraft Risk" in report
    assert "## 7. Assessment View (Recommendation)" in report
    assert "## Appendix" in report
    assert "### Appendix A: Country Risk — Oman" in report

    # Check that each section contains Sources
    assert report.count("### Sources") >= 7

    # Ensure no Scope Deferred placeholders remain
    assert "## Scope Deferred" not in report


def test_compiled_final_report_graph_runs_end_to_end():
    search_client = FakeFinalReportSearch()
    analysis_client = FakeFinalReportAnalysisClient()
    graph = build_final_report_graph(search_client, analysis_client)

    result = graph.invoke(
        {
            "assessment_input": AssessmentInput(
                airline="SalamAir", msn="6061", aircraft_variant="A320-214", jurisdiction="Oman"
            )
        }
    )

    assert "final_report_analysis" in result
    assert "executive_summary" in result
    assert "# Risk Assessment Report: SalamAir" in result["report"]
    assert "## 1. Executive Summary" in result["report"]
    assert "## 2. Financial Risks" in result["report"]
    assert "## 3. Operational Risks" in result["report"]
    assert "## 4. Market and Competitive Risks" in result["report"]
    assert "## 5. Red Flags" in result["report"]
    assert "## 6. Aircraft Risk" in result["report"]
    assert "## 7. Assessment View (Recommendation)" in result["report"]
    assert "### Appendix A: Country Risk — Oman" in result["report"]
