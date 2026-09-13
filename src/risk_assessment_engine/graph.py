from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from .analysis import (
    AnalysisClient,
    build_aircraft_prompt,
    build_assessment_view_prompt,
    build_country_prompt,
    build_executive_summary_prompt,
    build_financial_prompt,
    build_market_prompt,
    build_operational_prompt,
    build_airline_prompt,
    build_red_flags_prompt,
)
from .models import (
    AircraftIdentity,
    AssessmentInput,
    CountryRiskAnalysis,
    FinalReportAnalysis,
    GraphState,
)
from .render import (
    render_aircraft_report,
    render_assessment_view_report,
    render_country_report,
    render_final_report,
    render_financial_report,
    render_market_report,
    render_operational_report,
    render_red_flags_report,
    render_airline_report,
)
from .research import (
    collect_aircraft_sources,
    collect_country_sources,
    collect_financial_sources,
    collect_market_sources,
    collect_operational_sources,
    collect_airline_sources,
)


def build_airline_graph(search_client: Any, analysis_client: AnalysisClient):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_airline(state: GraphState) -> dict:
        return {"sources": collect_airline_sources(search_client, validated_input(state).airline)}

    def analyze_airline(state: GraphState) -> dict:
        prompt = build_airline_prompt(validated_input(state), state.get("sources", []))
        return {"analysis": analysis_client.analyze(prompt)}

    def render(state: GraphState) -> dict:
        assessment_input = validated_input(state)
        analysis = state.get("analysis")
        if analysis is None:
            raise ValueError("airline analysis is missing")
        return {"report": render_airline_report(assessment_input, analysis, state.get("sources", []))}

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("research_airline", research_airline)
    builder.add_node("analyze_airline", analyze_airline)
    builder.add_node("render", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "research_airline")
    builder.add_edge("research_airline", "analyze_airline")
    builder.add_edge("analyze_airline", "render")
    builder.add_edge("render", END)
    return builder.compile()


def build_financial_graph(search_client: Any, analysis_client: Any):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_financials(state: GraphState) -> dict:
        return {
            "financial_sources": collect_financial_sources(
                search_client, validated_input(state).airline
            )
        }

    def analyze_financials(state: GraphState) -> dict:
        prompt = build_financial_prompt(
            validated_input(state), state.get("financial_sources", [])
        )
        return {"financial_analysis": analysis_client.analyze_financial(prompt)}

    def render(state: GraphState) -> dict:
        assessment_input = validated_input(state)
        financial_analysis = state.get("financial_analysis")
        if financial_analysis is None:
            raise ValueError("financial analysis is missing")
        return {
            "report": render_financial_report(
                assessment_input,
                financial_analysis,
                state.get("financial_sources", []),
            )
        }

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("financial_research", research_financials)
    builder.add_node("financial_analysis", analyze_financials)
    builder.add_node("render_financial_report", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "financial_research")
    builder.add_edge("financial_research", "financial_analysis")
    builder.add_edge("financial_analysis", "render_financial_report")
    builder.add_edge("render_financial_report", END)
    return builder.compile()


def build_operational_graph(search_client: Any, analysis_client: Any):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_operationals(state: GraphState) -> dict:
        return {
            "operational_sources": collect_operational_sources(
                search_client, validated_input(state).airline
            )
        }

    def analyze_operationals(state: GraphState) -> dict:
        prompt = build_operational_prompt(
            validated_input(state), state.get("operational_sources", [])
        )
        return {"operational_analysis": analysis_client.analyze_operational(prompt)}

    def render(state: GraphState) -> dict:
        assessment_input = validated_input(state)
        operational_analysis = state.get("operational_analysis")
        if operational_analysis is None:
            raise ValueError("operational analysis is missing")
        return {
            "report": render_operational_report(
                assessment_input,
                operational_analysis,
                state.get("operational_sources", []),
            )
        }

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("operational_research", research_operationals)
    builder.add_node("operational_analysis", analyze_operationals)
    builder.add_node("render_operational_report", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "operational_research")
    builder.add_edge("operational_research", "operational_analysis")
    builder.add_edge("operational_analysis", "render_operational_report")
    builder.add_edge("render_operational_report", END)
    return builder.compile()


def build_market_graph(search_client: Any, analysis_client: Any):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_market(state: GraphState) -> dict:
        return {"market_sources": collect_market_sources(search_client, validated_input(state).airline)}

    def analyze_market(state: GraphState) -> dict:
        prompt = build_market_prompt(validated_input(state), state.get("market_sources", []))
        return {"market_analysis": analysis_client.analyze_market(prompt)}

    def render(state: GraphState) -> dict:
        assessment_input = validated_input(state)
        market_analysis = state.get("market_analysis")
        if market_analysis is None:
            raise ValueError("market analysis is missing")
        return {
            "report": render_market_report(
                assessment_input,
                market_analysis,
                state.get("market_sources", []),
            )
        }

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("market_research", research_market)
    builder.add_node("market_analysis", analyze_market)
    builder.add_node("render_market_report", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "market_research")
    builder.add_edge("market_research", "market_analysis")
    builder.add_edge("market_analysis", "render_market_report")
    builder.add_edge("render_market_report", END)
    return builder.compile()


def resolve_aircraft_identity(
    msn: str, sources: list[Any], user_aircraft_variant: str | None = None
) -> AircraftIdentity:
    """Accept explicit MSN-linked facts; corroborate or seed with user-provided aircraft_variant."""
    identity = AircraftIdentity(msn=msn)
    if user_aircraft_variant:
        variant_clean = user_aircraft_variant.strip().upper()
        identity.aircraft_variant = variant_clean
        identity.variant = variant_clean
        identity.aircraft_type = variant_clean
        identity.confidence = "medium"
    type_values: set[str] = set()
    for source in sources:
        if source.evidence_scope != "AIRCRAFT":
            continue
        evidence = source.evidence
        if msn.lower() not in evidence.lower():
            continue
        if source.source_id not in identity.supporting_source_ids:
            identity.supporting_source_ids.append(source.source_id)
        import re

        type_match = re.search(r"(?:type|model|variant|aircraft)\s*[:=]\s*([A-Z][A-Z0-9-]+)", evidence, re.IGNORECASE)
        if type_match:
            type_values.add(type_match.group(1).upper())
    if len(type_values) == 1:
        discovered_type = next(iter(type_values))
        user_norm = user_aircraft_variant.strip().upper() if user_aircraft_variant else None
        if user_norm:
            is_compatible = (
                user_norm == discovered_type
                or user_norm.startswith(discovered_type)
                or discovered_type.startswith(user_norm)
                or discovered_type.replace("-", "").startswith(user_norm.replace("-", ""))
                or user_norm.replace("-", "").startswith(discovered_type.replace("-", ""))
            )
            if not is_compatible:
                identity.conflicts.append(
                    f"User-specified variant '{user_aircraft_variant}' conflicts with discovered type/variant '{discovered_type}'."
                )
                identity.aircraft_variant = discovered_type
                identity.aircraft_type = discovered_type
                identity.variant = discovered_type
                identity.confidence = "low"
            else:
                identity.aircraft_variant = user_norm
                identity.variant = user_norm
                identity.aircraft_type = discovered_type
                identity.confidence = "medium" if len(identity.supporting_source_ids) == 1 else "high"
        else:
            identity.aircraft_variant = discovered_type
            identity.variant = discovered_type
            identity.aircraft_type = discovered_type
            identity.confidence = "medium" if len(identity.supporting_source_ids) == 1 else "high"
    elif len(type_values) > 1:
        identity.conflicts.append("Conflicting aircraft types/variants were reported for the MSN.")
        if not user_aircraft_variant:
            identity.confidence = "unavailable"
    return identity


def build_aircraft_graph(search_client: Any, analysis_client: Any):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_aircraft(state: GraphState) -> dict:
        value = validated_input(state)
        return {
            "aircraft_sources": collect_aircraft_sources(
                search_client, value.airline, value.msn, value.aircraft_variant
            )
        }

    def validate_identity(state: GraphState) -> dict:
        value = validated_input(state)
        return {
            "aircraft_identity": resolve_aircraft_identity(
                value.msn, state.get("aircraft_sources", []), value.aircraft_variant
            )
        }

    def analyze_aircraft(state: GraphState) -> dict:
        identity = state.get("aircraft_identity")
        if identity is None:
            raise ValueError("aircraft identity is missing")
        prompt = build_aircraft_prompt(
            validated_input(state), identity, state.get("aircraft_sources", [])
        )
        return {"aircraft_analysis": analysis_client.analyze_aircraft(prompt)}

    def render(state: GraphState) -> dict:
        analysis = state.get("aircraft_analysis")
        if analysis is None:
            raise ValueError("aircraft analysis is missing")
        return {"report": render_aircraft_report(
            validated_input(state), analysis, state.get("aircraft_sources", [])
        )}

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("aircraft_research", research_aircraft)
    builder.add_node("validate_aircraft_identity", validate_identity)
    builder.add_node("aircraft_analysis", analyze_aircraft)
    builder.add_node("render_aircraft_report", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "aircraft_research")
    builder.add_edge("aircraft_research", "validate_aircraft_identity")
    builder.add_edge("validate_aircraft_identity", "aircraft_analysis")
    builder.add_edge("aircraft_analysis", "render_aircraft_report")
    builder.add_edge("render_aircraft_report", END)
    return builder.compile()


def build_red_flags_graph(search_client: Any, analysis_client: Any):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_all_domains(state: GraphState) -> dict:
        inp = validated_input(state)
        f_sources = collect_financial_sources(search_client, inp.airline)
        o_sources = collect_operational_sources(search_client, inp.airline)
        m_sources = collect_market_sources(search_client, inp.airline)
        a_sources = collect_aircraft_sources(
            search_client, inp.airline, inp.msn, inp.aircraft_variant
        )
        identity = resolve_aircraft_identity(inp.msn, a_sources, inp.aircraft_variant)
        return {
            "financial_sources": f_sources,
            "operational_sources": o_sources,
            "market_sources": m_sources,
            "aircraft_sources": a_sources,
            "aircraft_identity": identity,
        }

    def analyze_all_domains(state: GraphState) -> dict:
        inp = validated_input(state)
        f_prompt = build_financial_prompt(inp, state.get("financial_sources", []))
        f_analysis = analysis_client.analyze_financial(f_prompt)

        o_prompt = build_operational_prompt(inp, state.get("operational_sources", []))
        o_analysis = analysis_client.analyze_operational(o_prompt)

        m_prompt = build_market_prompt(inp, state.get("market_sources", []))
        m_analysis = analysis_client.analyze_market(m_prompt)

        identity = state.get("aircraft_identity")
        if identity is None:
            raise ValueError("aircraft identity is missing")
        a_prompt = build_aircraft_prompt(inp, identity, state.get("aircraft_sources", []))
        a_analysis = analysis_client.analyze_aircraft(a_prompt)

        return {
            "financial_analysis": f_analysis,
            "operational_analysis": o_analysis,
            "market_analysis": m_analysis,
            "aircraft_analysis": a_analysis,
        }

    def synthesize_red_flags(state: GraphState) -> dict:
        inp = validated_input(state)
        f_analysis = state.get("financial_analysis")
        o_analysis = state.get("operational_analysis")
        m_analysis = state.get("market_analysis")
        a_analysis = state.get("aircraft_analysis")
        if not (f_analysis and o_analysis and m_analysis and a_analysis):
            raise ValueError("domain analyses must be completed before red flags synthesis")

        financial_findings = f_analysis.financial_risks.findings
        operational_findings = o_analysis.operational_risks.findings
        market_findings = m_analysis.market_risks.findings
        aircraft_findings = (
            a_analysis.aircraft_risks.findings + a_analysis.aircraft_type_risks.findings
        )

        prompt = build_red_flags_prompt(
            inp,
            financial_findings=financial_findings,
            operational_findings=operational_findings,
            market_findings=market_findings,
            aircraft_findings=aircraft_findings,
            identity=state.get("aircraft_identity"),
        )
        return {"red_flags_analysis": analysis_client.analyze_red_flags(prompt)}

    def render(state: GraphState) -> dict:
        inp = validated_input(state)
        analysis = state.get("red_flags_analysis")
        if analysis is None:
            raise ValueError("red flags analysis is missing")
        all_sources = (
            state.get("financial_sources", [])
            + state.get("operational_sources", [])
            + state.get("market_sources", [])
            + state.get("aircraft_sources", [])
        )
        return {"report": render_red_flags_report(inp, analysis, all_sources)}

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("research_all_domains", research_all_domains)
    builder.add_node("analyze_all_domains", analyze_all_domains)
    builder.add_node("synthesize_red_flags", synthesize_red_flags)
    builder.add_node("render_red_flags_report", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "research_all_domains")
    builder.add_edge("research_all_domains", "analyze_all_domains")
    builder.add_edge("analyze_all_domains", "synthesize_red_flags")
    builder.add_edge("synthesize_red_flags", "render_red_flags_report")
    builder.add_edge("render_red_flags_report", END)
    return builder.compile()


def resolve_deal_jurisdiction(
    airline: str, user_jurisdiction: str | None = None, sources: list[Any] | None = None
) -> str:
    """Determine the deal/financing jurisdiction from user input or airline context."""
    if user_jurisdiction and user_jurisdiction.strip():
        return user_jurisdiction.strip()

    # Common airline domicile mappings
    known_mappings = {
        "salamair": "Oman",
        "american": "United States",
        "american airlines": "United States",
        "frontier": "United States",
        "frontier airlines": "United States",
        "jetstar japan": "Japan",
        "ryanair": "Ireland",
        "emirates": "United Arab Emirates",
        "etihad": "United Arab Emirates",
        "wizz": "Hungary",
        "wizz air": "Hungary",
        "indigo": "India",
        "air india": "India",
        "airasia": "Malaysia",
        "qantas": "Australia",
        "lufthansa": "Germany",
        "air france": "France",
        "british airways": "United Kingdom",
    }
    airline_lower = airline.lower().strip()
    for name, country in known_mappings.items():
        if name in airline_lower:
            return country

    # Inspect sources for jurisdiction keywords if available
    if sources:
        for source in sources:
            evidence = getattr(source, "evidence", "").lower()
            for name, country in known_mappings.items():
                if name in evidence:
                    return country

    return "United States"


def build_country_graph(search_client: Any, analysis_client: Any):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_country(state: GraphState) -> dict:
        inp = validated_input(state)
        resolved_country = resolve_deal_jurisdiction(inp.airline, inp.jurisdiction)
        country_sources = collect_country_sources(search_client, inp.airline, resolved_country)
        return {
            "country_sources": country_sources,
        }

    def analyze_country(state: GraphState) -> dict:
        inp = validated_input(state)
        resolved_country = resolve_deal_jurisdiction(inp.airline, inp.jurisdiction)
        sources = state.get("country_sources", [])
        prompt = build_country_prompt(inp, resolved_country, sources)
        analysis = analysis_client.analyze_country(prompt)
        return {"country_analysis": analysis}

    def render(state: GraphState) -> dict:
        inp = validated_input(state)
        analysis = state.get("country_analysis")
        if analysis is None:
            raise ValueError("country analysis is missing")
        return {"report": render_country_report(inp, analysis, state.get("country_sources", []))}

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("country_research", research_country)
    builder.add_node("country_analysis", analyze_country)
    builder.add_node("render_country_report", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "country_research")
    builder.add_edge("country_research", "country_analysis")
    builder.add_edge("country_analysis", "render_country_report")
    builder.add_edge("render_country_report", END)
    return builder.compile()


def build_assessment_view_graph(search_client: Any, analysis_client: Any):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_all(state: GraphState) -> dict:
        inp = validated_input(state)
        resolved_country = resolve_deal_jurisdiction(inp.airline, inp.jurisdiction)
        f_sources = collect_financial_sources(search_client, inp.airline)
        o_sources = collect_operational_sources(search_client, inp.airline)
        m_sources = collect_market_sources(search_client, inp.airline)
        a_sources = collect_aircraft_sources(
            search_client, inp.airline, inp.msn, inp.aircraft_variant
        )
        c_sources = collect_country_sources(search_client, inp.airline, resolved_country)
        identity = resolve_aircraft_identity(inp.msn, a_sources, inp.aircraft_variant)
        return {
            "financial_sources": f_sources,
            "operational_sources": o_sources,
            "market_sources": m_sources,
            "aircraft_sources": a_sources,
            "country_sources": c_sources,
            "aircraft_identity": identity,
        }

    def analyze_domains(state: GraphState) -> dict:
        inp = validated_input(state)
        resolved_country = resolve_deal_jurisdiction(inp.airline, inp.jurisdiction)
        f_prompt = build_financial_prompt(inp, state.get("financial_sources", []))
        f_analysis = analysis_client.analyze_financial(f_prompt)

        o_prompt = build_operational_prompt(inp, state.get("operational_sources", []))
        o_analysis = analysis_client.analyze_operational(o_prompt)

        m_prompt = build_market_prompt(inp, state.get("market_sources", []))
        m_analysis = analysis_client.analyze_market(m_prompt)

        identity = state.get("aircraft_identity")
        if identity is None:
            raise ValueError("aircraft identity is missing")
        a_prompt = build_aircraft_prompt(inp, identity, state.get("aircraft_sources", []))
        a_analysis = analysis_client.analyze_aircraft(a_prompt)

        c_prompt = build_country_prompt(inp, resolved_country, state.get("country_sources", []))
        c_analysis = analysis_client.analyze_country(c_prompt)

        return {
            "financial_analysis": f_analysis,
            "operational_analysis": o_analysis,
            "market_analysis": m_analysis,
            "aircraft_analysis": a_analysis,
            "country_analysis": c_analysis,
        }

    def synthesize_red_flags(state: GraphState) -> dict:
        inp = validated_input(state)
        f_analysis = state.get("financial_analysis")
        o_analysis = state.get("operational_analysis")
        m_analysis = state.get("market_analysis")
        a_analysis = state.get("aircraft_analysis")
        if not (f_analysis and o_analysis and m_analysis and a_analysis):
            raise ValueError("domain analyses must be completed before red flags synthesis")

        financial_findings = f_analysis.financial_risks.findings
        operational_findings = o_analysis.operational_risks.findings
        market_findings = m_analysis.market_risks.findings
        aircraft_findings = (
            a_analysis.aircraft_risks.findings + a_analysis.aircraft_type_risks.findings
        )

        prompt = build_red_flags_prompt(
            inp,
            financial_findings=financial_findings,
            operational_findings=operational_findings,
            market_findings=market_findings,
            aircraft_findings=aircraft_findings,
            identity=state.get("aircraft_identity"),
        )
        return {"red_flags_analysis": analysis_client.analyze_red_flags(prompt)}

    def synthesize_assessment_view(state: GraphState) -> dict:
        inp = validated_input(state)
        f_analysis = state.get("financial_analysis")
        o_analysis = state.get("operational_analysis")
        m_analysis = state.get("market_analysis")
        a_analysis = state.get("aircraft_analysis")
        rf_analysis = state.get("red_flags_analysis")
        c_analysis = state.get("country_analysis")

        if not (f_analysis and o_analysis and m_analysis and a_analysis and rf_analysis):
            raise ValueError("prior analyses must be completed before assessment view synthesis")

        prompt = build_assessment_view_prompt(
            inp,
            financial_findings=f_analysis.financial_risks.findings,
            operational_findings=o_analysis.operational_risks.findings,
            market_findings=m_analysis.market_risks.findings,
            aircraft_findings=a_analysis.aircraft_risks.findings + a_analysis.aircraft_type_risks.findings,
            red_flags=rf_analysis.red_flags,
            country_analysis=c_analysis,
            identity=state.get("aircraft_identity"),
        )
        return {"assessment_view_analysis": analysis_client.analyze_assessment_view(prompt)}

    def render(state: GraphState) -> dict:
        inp = validated_input(state)
        analysis = state.get("assessment_view_analysis")
        if analysis is None:
            raise ValueError("assessment view analysis is missing")
        all_sources = (
            state.get("financial_sources", [])
            + state.get("operational_sources", [])
            + state.get("market_sources", [])
            + state.get("aircraft_sources", [])
            + state.get("country_sources", [])
        )
        return {"report": render_assessment_view_report(inp, analysis, all_sources)}

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("research_all", research_all)
    builder.add_node("analyze_domains", analyze_domains)
    builder.add_node("synthesize_red_flags", synthesize_red_flags)
    builder.add_node("synthesize_assessment_view", synthesize_assessment_view)
    builder.add_node("render_assessment_view_report", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "research_all")
    builder.add_edge("research_all", "analyze_domains")
    builder.add_edge("analyze_domains", "synthesize_red_flags")
    builder.add_edge("synthesize_red_flags", "synthesize_assessment_view")
    builder.add_edge("synthesize_assessment_view", "render_assessment_view_report")
    builder.add_edge("render_assessment_view_report", END)
    return builder.compile()


def build_final_report_graph(search_client: Any, analysis_client: Any):
    def validated_input(state: GraphState) -> AssessmentInput:
        value = state.get("assessment_input")
        if not isinstance(value, AssessmentInput):
            raise ValueError("assessment_input must be an AssessmentInput")
        return value

    def validate_input(state: GraphState) -> dict:
        validated_input(state)
        return {}

    def research_all(state: GraphState) -> dict:
        inp = validated_input(state)
        resolved_country = resolve_deal_jurisdiction(inp.airline, inp.jurisdiction)
        f_sources = collect_financial_sources(search_client, inp.airline)
        o_sources = collect_operational_sources(search_client, inp.airline)
        m_sources = collect_market_sources(search_client, inp.airline)
        a_sources = collect_aircraft_sources(
            search_client, inp.airline, inp.msn, inp.aircraft_variant
        )
        c_sources = collect_country_sources(search_client, inp.airline, resolved_country)
        identity = resolve_aircraft_identity(inp.msn, a_sources, inp.aircraft_variant)
        return {
            "financial_sources": f_sources,
            "operational_sources": o_sources,
            "market_sources": m_sources,
            "aircraft_sources": a_sources,
            "country_sources": c_sources,
            "aircraft_identity": identity,
        }

    def analyze_domains(state: GraphState) -> dict:
        inp = validated_input(state)
        resolved_country = resolve_deal_jurisdiction(inp.airline, inp.jurisdiction)
        f_prompt = build_financial_prompt(inp, state.get("financial_sources", []))
        f_analysis = analysis_client.analyze_financial(f_prompt)

        o_prompt = build_operational_prompt(inp, state.get("operational_sources", []))
        o_analysis = analysis_client.analyze_operational(o_prompt)

        m_prompt = build_market_prompt(inp, state.get("market_sources", []))
        m_analysis = analysis_client.analyze_market(m_prompt)

        identity = state.get("aircraft_identity")
        if identity is None:
            raise ValueError("aircraft identity is missing")
        a_prompt = build_aircraft_prompt(inp, identity, state.get("aircraft_sources", []))
        a_analysis = analysis_client.analyze_aircraft(a_prompt)

        c_prompt = build_country_prompt(inp, resolved_country, state.get("country_sources", []))
        c_analysis = analysis_client.analyze_country(c_prompt)

        return {
            "financial_analysis": f_analysis,
            "operational_analysis": o_analysis,
            "market_analysis": m_analysis,
            "aircraft_analysis": a_analysis,
            "country_analysis": c_analysis,
        }

    def synthesize_red_flags(state: GraphState) -> dict:
        inp = validated_input(state)
        f_analysis = state.get("financial_analysis")
        o_analysis = state.get("operational_analysis")
        m_analysis = state.get("market_analysis")
        a_analysis = state.get("aircraft_analysis")
        if not (f_analysis and o_analysis and m_analysis and a_analysis):
            raise ValueError("domain analyses must be completed before red flags synthesis")

        financial_findings = f_analysis.financial_risks.findings
        operational_findings = o_analysis.operational_risks.findings
        market_findings = m_analysis.market_risks.findings
        aircraft_findings = (
            a_analysis.aircraft_risks.findings + a_analysis.aircraft_type_risks.findings
        )

        prompt = build_red_flags_prompt(
            inp,
            financial_findings=financial_findings,
            operational_findings=operational_findings,
            market_findings=market_findings,
            aircraft_findings=aircraft_findings,
            identity=state.get("aircraft_identity"),
        )
        return {"red_flags_analysis": analysis_client.analyze_red_flags(prompt)}

    def synthesize_assessment_view(state: GraphState) -> dict:
        inp = validated_input(state)
        f_analysis = state.get("financial_analysis")
        o_analysis = state.get("operational_analysis")
        m_analysis = state.get("market_analysis")
        a_analysis = state.get("aircraft_analysis")
        rf_analysis = state.get("red_flags_analysis")
        c_analysis = state.get("country_analysis")

        if not (f_analysis and o_analysis and m_analysis and a_analysis and rf_analysis):
            raise ValueError("prior analyses must be completed before assessment view synthesis")

        prompt = build_assessment_view_prompt(
            inp,
            financial_findings=f_analysis.financial_risks.findings,
            operational_findings=o_analysis.operational_risks.findings,
            market_findings=m_analysis.market_risks.findings,
            aircraft_findings=a_analysis.aircraft_risks.findings + a_analysis.aircraft_type_risks.findings,
            red_flags=rf_analysis.red_flags,
            country_analysis=c_analysis,
            identity=state.get("aircraft_identity"),
        )
        return {"assessment_view_analysis": analysis_client.analyze_assessment_view(prompt)}

    def synthesize_executive_summary(state: GraphState) -> dict:
        inp = validated_input(state)
        f_analysis = state.get("financial_analysis")
        o_analysis = state.get("operational_analysis")
        m_analysis = state.get("market_analysis")
        a_analysis = state.get("aircraft_analysis")
        rf_analysis = state.get("red_flags_analysis")
        av_analysis = state.get("assessment_view_analysis")
        c_analysis = state.get("country_analysis")

        if not (f_analysis and o_analysis and m_analysis and a_analysis and rf_analysis and av_analysis):
            raise ValueError("prior analyses must be completed before executive summary synthesis")

        prompt = build_executive_summary_prompt(
            inp,
            financial_findings=f_analysis.financial_risks.findings,
            operational_findings=o_analysis.operational_risks.findings,
            market_findings=m_analysis.market_risks.findings,
            aircraft_findings=a_analysis.aircraft_risks.findings + a_analysis.aircraft_type_risks.findings,
            red_flags=rf_analysis.red_flags,
            assessment_view=av_analysis,
            country_analysis=c_analysis,
            identity=state.get("aircraft_identity"),
        )
        exec_summary = analysis_client.analyze_executive_summary(prompt)

        final_analysis = FinalReportAnalysis(
            executive_summary=exec_summary,
            financial_analysis=f_analysis,
            operational_analysis=o_analysis,
            market_analysis=m_analysis,
            aircraft_analysis=a_analysis,
            red_flags_analysis=rf_analysis,
            assessment_view_analysis=av_analysis,
            country_analysis=c_analysis if c_analysis else CountryRiskAnalysis(
                country_name=resolve_deal_jurisdiction(inp.airline, inp.jurisdiction),
                jurisdiction_rationale="Resolved domicile",
                benchmarking_summary="Benchmarking",
                cape_town_convention=f_analysis.financial_risks,
                repossession_risk=f_analysis.financial_risks,
                icao_safety=f_analysis.financial_risks,
                bankruptcy_law=f_analysis.financial_risks,
                geopolitical_assessment=f_analysis.financial_risks,
            ),
        )
        return {
            "executive_summary": exec_summary,
            "final_report_analysis": final_analysis,
        }

    def render(state: GraphState) -> dict:
        inp = validated_input(state)
        final_analysis = state.get("final_report_analysis")
        if final_analysis is None:
            raise ValueError("final report analysis is missing")
        all_sources = (
            state.get("financial_sources", [])
            + state.get("operational_sources", [])
            + state.get("market_sources", [])
            + state.get("aircraft_sources", [])
            + state.get("country_sources", [])
        )
        return {"report": render_final_report(inp, final_analysis, all_sources)}

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("research_all", research_all)
    builder.add_node("analyze_domains", analyze_domains)
    builder.add_node("synthesize_red_flags", synthesize_red_flags)
    builder.add_node("synthesize_assessment_view", synthesize_assessment_view)
    builder.add_node("synthesize_executive_summary", synthesize_executive_summary)
    builder.add_node("render_final_report", render)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "research_all")
    builder.add_edge("research_all", "analyze_domains")
    builder.add_edge("analyze_domains", "synthesize_red_flags")
    builder.add_edge("synthesize_red_flags", "synthesize_assessment_view")
    builder.add_edge("synthesize_assessment_view", "synthesize_executive_summary")
    builder.add_edge("synthesize_executive_summary", "render_final_report")
    builder.add_edge("render_final_report", END)
    return builder.compile()