from datetime import date

from risk_assessment_engine.analysis import build_country_prompt
from risk_assessment_engine.graph import build_country_graph, resolve_deal_jurisdiction
from risk_assessment_engine.models import (
    AssessmentInput,
    BenchmarkScore,
    CountryRiskAnalysis,
    Finding,
    SectionAnalysis,
    SourceRecord,
)
from risk_assessment_engine.render import render_country_report
from risk_assessment_engine.research import COUNTRY_QUERIES, collect_country_sources


class FakeCountrySearch:
    def __init__(self):
        self.queries = []

    def search(self, query, **kwargs):
        self.queries.append(query)
        return {
            "results": [
                {
                    "url": "https://example.com/jurisdiction/oman",
                    "title": f"Oman Aviation Law: {query[:25]}",
                    "publisher": "Civil Aviation Authority & Legal Gazette",
                    "content": f"Evidence for {query} with Cape Town Convention ratification and ICAO score.",
                }
            ]
        }


def make_sample_country_analysis(country="Oman"):
    return CountryRiskAnalysis(
        country_name=country,
        jurisdiction_rationale="Primary domicile and operating AOC of the airline.",
        benchmarking_summary="Oman scores in the mid-range of aviation finance jurisdictions, behind Tier-1 CTC signatories like the US and Ireland but ahead of high-risk jurisdictions.",
        benchmarking_scores=[
            BenchmarkScore(
                country="United States",
                ctc_score=1.0,
                repossession_score=1.0,
                icao_safety_score=1.0,
                bankruptcy_score=2.0,
                overall_score=1.15,
            ),
            BenchmarkScore(
                country="Ireland",
                ctc_score=1.0,
                repossession_score=1.0,
                icao_safety_score=1.0,
                bankruptcy_score=2.0,
                overall_score=1.15,
            ),
            BenchmarkScore(
                country=country,
                ctc_score=2.0,
                repossession_score=3.0,
                icao_safety_score=3.0,
                bankruptcy_score=4.0,
                overall_score=2.85,
            ),
        ],
        cape_town_convention=SectionAnalysis(
            summary="Oman is a contracting state to the Cape Town Convention and Aircraft Protocol with standard qualifying declarations.",
            findings=[
                Finding(
                    statement="Oman deposited instruments of accession to the Cape Town Convention with qualifying declarations under Alternative A.",
                    source_ids=["C001"],
                    kind="FACT",
                    category="cape_town",
                    scope="JURISDICTION",
                    date_context="2020",
                )
            ],
        ),
        repossession_risk=SectionAnalysis(
            summary="Repossession risk is moderate, supported by IDERA recording with CAA Oman.",
            findings=[
                Finding(
                    statement="Lessor deregistration and export remedies are enforceable via CAA administrative procedures.",
                    source_ids=["C001"],
                    kind="ANALYSIS",
                    category="repossession",
                    scope="JURISDICTION",
                )
            ],
        ),
        icao_safety=SectionAnalysis(
            summary="Oman maintains strong ICAO USOAP safety oversight audit performance above global averages.",
            findings=[
                Finding(
                    statement="CAA Oman achieved an Effective Implementation score of approximately 85% in recent USOAP audits.",
                    source_ids=["C001"],
                    kind="FACT",
                    category="icao_safety",
                    scope="JURISDICTION",
                    date_context="latest USOAP audit",
                )
            ],
        ),
        bankruptcy_law=SectionAnalysis(
            summary="Commercial insolvency law provides recognizable liquidation and restructuring processes with typical litigation timelines of 6 to 12 months.",
            findings=[
                Finding(
                    statement="Court-supervised restructuring processes average 6-12 months before asset release in contested matters.",
                    source_ids=["C001"],
                    kind="ANALYSIS",
                    category="bankruptcy_timelines",
                    scope="JURISDICTION",
                )
            ],
        ),
        geopolitical_assessment=SectionAnalysis(
            summary="Oman presents low-to-moderate geopolitical risk characterized by foreign policy neutrality and economic stability.",
            findings=[
                Finding(
                    statement="Sovereign stability and neutral regional foreign policy support predictable cross-border currency remittances.",
                    source_ids=["C001"],
                    kind="FACT",
                    category="geopolitics",
                    scope="JURISDICTION",
                )
            ],
        ),
    )


class FakeCountryAnalysisClient:
    def analyze_country(self, prompt):
        assert "Jurisdictional Risk Benchmarking" in prompt
        assert "Cape Town Convention" in prompt
        assert "ICAO" in prompt
        assert "Bankruptcy" in prompt
        assert "Geopolitical" in prompt
        return make_sample_country_analysis("Oman")


def test_country_queries_cover_required_appendix_topics():
    query_text = " ".join(COUNTRY_QUERIES.values()).lower()
    for topic in (
        "domicile",
        "registration",
        "cape town",
        "repossession",
        "icao",
        "usoap",
        "bankruptcy",
        "insolvency",
        "geopolitical",
    ):
        assert topic in query_text


def test_country_sources_are_deduplicated_and_tagged():
    search = FakeCountrySearch()
    sources = collect_country_sources(search, "SalamAir", "Oman", accessed_date=date(2026, 9, 13))
    assert len(search.queries) == len(COUNTRY_QUERIES)
    assert len(sources) == 1
    assert sources[0].source_id == "C001"
    assert sources[0].evidence_scope == "JURISDICTION"
    assert "Oman" in sources[0].evidence


def test_resolve_deal_jurisdiction_prefers_user_input_and_maps_known_airlines():
    # Explicit user input override
    assert resolve_deal_jurisdiction("SalamAir", user_jurisdiction="Ireland") == "Ireland"
    # Auto-resolution from known airline name
    assert resolve_deal_jurisdiction("SalamAir") == "Oman"
    assert resolve_deal_jurisdiction("American Airlines") == "United States"
    assert resolve_deal_jurisdiction("Jetstar Japan") == "Japan"
    # Fallback to default
    assert resolve_deal_jurisdiction("Unknown Regional Air") == "United States"


def test_country_prompt_requires_all_areas_and_scope():
    inp = AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214", jurisdiction="Oman")
    source = SourceRecord(
        source_id="C001",
        url="https://example.com/jurisdiction/oman",
        title="Oman Aviation Law",
        accessed_date=date(2026, 9, 13),
        category="cape_town",
        evidence="Ratification and IDERA evidence.",
        evidence_scope="JURISDICTION",
    )
    prompt = build_country_prompt(inp, "Oman", [source])
    assert "SalamAir" in prompt
    assert "Oman" in prompt
    assert "6061" in prompt
    assert "A320-214" in prompt
    assert "Jurisdictional Risk Benchmarking" in prompt
    assert "Cape Town Convention Compliance" in prompt
    assert "Repossession Risk" in prompt
    assert "ICAO Country Safety Score" in prompt
    assert "Bankruptcy Law" in prompt
    assert "Overall Geopolitical Assessment" in prompt
    assert "JURISDICTION" in prompt


def test_render_country_report_formats_benchmarking_table_and_sources():
    inp = AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214", jurisdiction="Oman")
    analysis = make_sample_country_analysis("Oman")
    sources = [
        SourceRecord(
            source_id="C001",
            url="https://example.com/jurisdiction/oman",
            title="Oman CAA Legal Framework",
            publisher="CAA Oman",
            accessed_date=date(2026, 9, 13),
            category="cape_town",
            evidence="Accession details.",
            evidence_scope="JURISDICTION",
        ),
        SourceRecord(
            source_id="C999",
            url="https://example.com/unused",
            title="Unused Article",
            publisher="News",
            accessed_date=date(2026, 9, 13),
            category="geopolitics",
            evidence="General news.",
            evidence_scope="JURISDICTION",
        ),
    ]

    report = render_country_report(inp, analysis, sources)

    assert "# Step 7 Country Risk Assessment: SalamAir" in report
    assert "## Appendix A: Country Risk — Oman" in report
    assert "### Jurisdictional Risk Benchmarking" in report
    assert "| Country | CTC (25%) | Repossession (25%) | ICAO Safety (20%) | Bankruptcy/Litigation (15%) | Overall Score |" in report
    assert "| Oman |" in report
    assert "### Cape Town Convention Compliance" in report
    assert "### Repossession Risk with the Airline" in report
    assert "### ICAO Country Safety Score" in report
    assert "### Bankruptcy Law — Repossession, Restructuring & Litigation Timelines" in report
    assert "### Overall Geopolitical Assessment" in report
    assert "### Sources" in report
    assert "C001" in report
    assert "C999" not in report
    assert "## Scope Deferred" in report


def test_compiled_country_graph_runs_end_to_end():
    search_client = FakeCountrySearch()
    analysis_client = FakeCountryAnalysisClient()
    graph = build_country_graph(search_client, analysis_client)

    result = graph.invoke(
        {
            "assessment_input": AssessmentInput(
                airline="SalamAir", msn="6061", aircraft_variant="A320-214", jurisdiction="Oman"
            )
        }
    )

    assert "country_analysis" in result
    assert result["country_analysis"].country_name == "Oman"
    assert "# Step 7 Country Risk Assessment: SalamAir" in result["report"]
    assert "## Appendix A: Country Risk — Oman" in result["report"]
    assert "C001" in result["report"]
