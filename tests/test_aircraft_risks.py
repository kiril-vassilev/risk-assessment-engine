from datetime import date

from typing import Literal

from risk_assessment_engine.analysis import build_aircraft_prompt
from risk_assessment_engine.graph import build_aircraft_graph, resolve_aircraft_identity
from risk_assessment_engine.models import (
    AircraftAnalysis,
    AircraftIdentity,
    AssessmentInput,
    Finding,
    SectionAnalysis,
    SourceRecord,
)
from risk_assessment_engine.research import AIRCRAFT_QUERIES, collect_aircraft_sources


class FakeAircraftSearch:
    def __init__(self, evidence="MSN 12345 type: A320"):
        self.queries = []
        self.evidence = evidence

    def search(self, query, **kwargs):
        self.queries.append(query)
        return {
            "results": [
                {
                    "url": "https://example.com/aircraft/12345/",
                    "title": "Aircraft Record",
                    "publisher": "Example Registry",
                    "content": self.evidence,
                }
            ]
        }


def aircraft_source(
    source_id="A001",
    scope: Literal["AIRLINE", "AIRCRAFT", "AIRCRAFT_TYPE", "JURISDICTION", "UNKNOWN"] = "AIRCRAFT",
    evidence="MSN 12345 type: A320",
):
    return SourceRecord(
        source_id=source_id,
        url="https://example.com/aircraft/12345",
        title="Aircraft Record",
        accessed_date=date(2026, 9, 11),
        category="identity",
        evidence=evidence,
        evidence_scope=scope,
    )


def make_aircraft_analysis(identity):
    finding = Finding(
        statement="The aircraft type has observable market evidence.",
        source_ids=["A001"],
        kind="FACT",
        category="type_market",
        scope="AIRCRAFT_TYPE",
    )
    section = SectionAnalysis(summary="Evidence is separated by scope.", findings=[finding])
    return AircraftAnalysis(
        identity=identity,
        airline_context=section,
        aircraft_risks=section,
        aircraft_type_risks=section,
    )


class FakeAircraftAnalysis:
    def analyze_aircraft(self, prompt):
        assert "AIRCRAFT_TYPE" in prompt
        assert "unavailable" in prompt
        identity = AircraftIdentity(
            msn="12345",
            aircraft_type="A320",
            confidence="medium",
            supporting_source_ids=["A001"],
        )
        return make_aircraft_analysis(identity)


def test_aircraft_queries_cover_identity_and_asset_topics():
    query_text = " ".join(AIRCRAFT_QUERIES.values()).lower()
    for topic in ("msn", "registration", "owner", "engine", "maintenance", "orderbook", "lease rates", "part-out"):
        assert topic in query_text


def test_aircraft_sources_are_deduplicated_and_scoped():
    search = FakeAircraftSearch()
    sources = collect_aircraft_sources(search, "Example Airline", "12345", "A320-214", accessed_date=date(2026, 9, 11))
    assert len(search.queries) == len(AIRCRAFT_QUERIES)
    assert len(sources) == 1
    assert sources[0].source_id == "A001"
    assert sources[0].evidence_scope == "AIRCRAFT"
    assert "12345" in sources[0].evidence


def test_identity_requires_explicit_msn_linked_evidence():
    resolved = resolve_aircraft_identity("12345", [aircraft_source()])
    unresolved = resolve_aircraft_identity(
        "12345", [aircraft_source(evidence="A320 type market orderbook data", scope="AIRCRAFT_TYPE")]
    )
    assert resolved.aircraft_type == "A320"
    assert resolved.confidence == "medium"
    assert unresolved.aircraft_type is None
    assert unresolved.confidence == "unavailable"


def test_aircraft_prompt_preserves_three_risk_scopes():
    prompt = build_aircraft_prompt(
        AssessmentInput(airline="Example Airline", msn="12345", aircraft_variant="A320-214"),
        AircraftIdentity(msn="12345"),
        [aircraft_source()],
    )
    assert "AIRLINE" in prompt
    assert "AIRCRAFT" in prompt
    assert "AIRCRAFT_TYPE" in prompt
    assert "Do not use AIRCRAFT_TYPE evidence to support AIRCRAFT claims" in prompt


def test_compiled_aircraft_graph_renders_scoped_report():
    result = build_aircraft_graph(FakeAircraftSearch(), FakeAircraftAnalysis()).invoke(
        {"assessment_input": AssessmentInput(airline="Example Airline", msn="12345", aircraft_variant="A320-214")}
    )
    assert result["aircraft_sources"][0].source_id == "A001"
    assert result["aircraft_identity"].aircraft_type == "A320"
    assert "# Step 5 Aircraft Risk Assessment" in result["report"]
    assert "## Aircraft Identity" in result["report"]
    assert "## Aircraft-Specific Risk" in result["report"]
    assert "## Aircraft-Type Risk" in result["report"]


def test_aircraft_queries_include_aircraft_variant():
    search = FakeAircraftSearch()
    collect_aircraft_sources(search, "SalamAir", "6061", aircraft_variant="A320-214", accessed_date=date(2026, 9, 13))
    for query in search.queries:
        assert "A320-214" in query
        if "msn" in query.lower():
            assert "6061" in query


def test_identity_resolution_with_user_provided_variant():
    # User provides variant, evidence doesn't specify variant -> seeded with user variant
    identity_seeded = resolve_aircraft_identity(
        "6061", [aircraft_source(evidence="MSN 6061 delivered to SalamAir")], user_aircraft_variant="A320-214"
    )
    assert identity_seeded.aircraft_variant == "A320-214"
    assert identity_seeded.confidence == "medium"

    # User provides variant and evidence matches
    identity_matching = resolve_aircraft_identity(
        "12345", [aircraft_source(evidence="MSN 12345 type: A320")], user_aircraft_variant="A320-214"
    )
    assert identity_matching.aircraft_type == "A320"
    assert identity_matching.aircraft_variant == "A320-214"
    assert identity_matching.confidence == "medium"

    # User provides variant but evidence conflicts
    identity_conflict = resolve_aircraft_identity(
        "12345", [aircraft_source(evidence="MSN 12345 type: B737-800")], user_aircraft_variant="A320-214"
    )
    assert identity_conflict.aircraft_type == "B737-800"
    assert len(identity_conflict.conflicts) > 0
    assert identity_conflict.confidence == "low"


def test_compiled_aircraft_graph_with_aircraft_variant_parameter():
    result = build_aircraft_graph(FakeAircraftSearch(), FakeAircraftAnalysis()).invoke(
        {"assessment_input": AssessmentInput(airline="SalamAir", msn="6061", aircraft_variant="A320-214")}
    )
    assert result["assessment_input"].aircraft_variant == "A320-214"
    assert result["aircraft_sources"][0].source_id == "A001"
    assert "# Step 5 Aircraft Risk Assessment: SalamAir" in result["report"]