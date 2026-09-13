from __future__ import annotations

from .models import (
    AirlineAnalysis,
    AircraftAnalysis,
    AssessmentInput,
    AssessmentViewAnalysis,
    CountryRiskAnalysis,
    FinalReportAnalysis,
    FinancialAnalysis,
    MarketAnalysis,
    OperationalAnalysis,
    RedFlagsAnalysis,
    SectionAnalysis,
    SourceRecord,
)


def _section(title: str, analysis: SectionAnalysis, sources: list[SourceRecord]) -> str:
    lines = [f"## {title}", analysis.summary]
    for finding in analysis.findings:
        citations = ", ".join(finding.source_ids) if finding.source_ids else "Unavailable"
        date_context = f" ({finding.date_context})" if finding.date_context else ""
        direction = f" [{finding.direction}]" if finding.direction else ""
        lines.append(f"- [{finding.kind}]{direction} {finding.statement}{date_context} [Sources: {citations}]")
    lines.append("### Sources")
    section_source_ids = {source_id for finding in analysis.findings for source_id in finding.source_ids}
    matching = [source for source in sources if source.source_id in section_source_ids]
    if not matching:
        lines.append("- Unavailable: no reliable sources were retained for this section.")
    for source in matching:
        published = source.publication_date.isoformat() if source.publication_date else "publication date unavailable"
        lines.append(f"- {source.source_id}: {source.title} — {source.publisher}; published {published}; {source.url}")
    return "\n".join(lines)


def render_airline_report(assessment_input: AssessmentInput, analysis: AirlineAnalysis, sources: list[SourceRecord]) -> str:
    sections = [
        f"# Step 1 Airline Risk Research: {assessment_input.airline}",
        f"Aircraft MSN: {assessment_input.msn} (aircraft analysis pending)",
        "",
        _section("1. Executive Summary", analysis.executive_summary, sources),
        _section("2. Financial Risks", analysis.financial_risks, sources),
        _section("3. Operational Risks", analysis.operational_risks, sources),
        _section("4. Market and Competitive Risks", analysis.market_risks, sources),
        "## Scope Deferred",
        "Aircraft Risk, Red Flags, Assessment View, and Appendix A Country Risk require later research increments and are unavailable in Step 1.",
    ]
    return "\n\n".join(sections) + "\n"


# Backward-compatible alias
render_report = render_airline_report


def render_financial_report(
    assessment_input: AssessmentInput,
    analysis: FinancialAnalysis,
    sources: list[SourceRecord],
) -> str:
    sections = [
        f"# Step 2 Financial Risk Assessment: {assessment_input.airline}",
        f"Aircraft MSN: {assessment_input.msn} (aircraft analysis pending)",
        "",
        _section("2. Financial Risks", analysis.financial_risks, sources),
        "## Scope Deferred",
        "Operational Risks, Market and Competitive Risks, Red Flags, Aircraft Risk, Assessment View, and Appendix A Country Risk require later increments.",
    ]
    return "\n\n".join(sections) + "\n"


def render_operational_report(
    assessment_input: AssessmentInput,
    analysis: OperationalAnalysis,
    sources: list[SourceRecord],
) -> str:
    sections = [
        f"# Step 3 Operational Risk Assessment: {assessment_input.airline}",
        f"Aircraft MSN: {assessment_input.msn} (aircraft-specific analysis pending)",
        "",
        _section("3. Operational Risks", analysis.operational_risks, sources),
        "## Scope Deferred",
        "Financial Risks, Market and Competitive Risks, Red Flags, Aircraft Risk, Assessment View, and Appendix A Country Risk are separate or later capabilities.",
    ]
    return "\n\n".join(sections) + "\n"


def render_market_report(
    assessment_input: AssessmentInput,
    analysis: MarketAnalysis,
    sources: list[SourceRecord],
) -> str:
    sections = [
        f"# Step 4 Market and Competitive Risk Assessment: {assessment_input.airline}",
        f"Aircraft MSN: {assessment_input.msn} (aircraft-specific analysis pending)",
        "",
        _section("4. Market and Competitive Risks", analysis.market_risks, sources),
        "## Scope Deferred",
        "Financial Risks, Operational Risks, Red Flags, Aircraft Risk, Assessment View, and Appendix A Country Risk are separate or later capabilities.",
    ]
    return "\n\n".join(sections) + "\n"


def render_aircraft_report(
    assessment_input: AssessmentInput,
    analysis: AircraftAnalysis,
    sources: list[SourceRecord],
) -> str:
    identity = analysis.identity
    identity_lines = [
        f"MSN: {identity.msn}",
        f"Aircraft variant: {identity.aircraft_variant or assessment_input.aircraft_variant}",
        f"Aircraft type: {identity.aircraft_type or 'Unavailable'}",
        f"Engine/configuration: {identity.engine_configuration or 'Unavailable'}",
        f"Current operator: {identity.current_operator or 'Unavailable'}",
        f"Current owner: {identity.current_owner or 'Unavailable'}",
        f"Identity confidence: {identity.confidence}",
    ]
    if identity.conflicts:
        identity_lines.append("Identity conflicts: " + "; ".join(identity.conflicts))
    sections = [
        f"# Step 5 Aircraft Risk Assessment: {assessment_input.airline}",
        "## Aircraft Identity",
        "\n".join(identity_lines),
        _section("Airline-Level Context", analysis.airline_context, sources),
        _section("Aircraft-Specific Risk", analysis.aircraft_risks, sources),
        _section("Aircraft-Type Risk", analysis.aircraft_type_risks, sources),
        "## Scope Deferred",
        "Red Flags, Assessment View, and Appendix A Country Risk require later capabilities.",
    ]
    return "\n\n".join(sections) + "\n"


def render_red_flags_report(
    assessment_input: AssessmentInput,
    analysis: RedFlagsAnalysis,
    sources: list[SourceRecord],
) -> str:
    lines = [
        f"# Step 6 Red Flags Assessment: {assessment_input.airline}",
        f"Aircraft MSN: {assessment_input.msn} | Aircraft Variant: {assessment_input.aircraft_variant}",
        "",
        "## 5. Red Flags",
        analysis.summary,
    ]
    if not analysis.red_flags:
        lines.append("- No material red flags identified based on the available evidence.")
    for i, flag in enumerate(analysis.red_flags, start=1):
        citations = ", ".join(flag.source_ids) if flag.source_ids else "Unavailable"
        lines.append(
            f"### Red Flag {i}: [{flag.severity.upper()}] {flag.headline} ({flag.domain.capitalize()} | {flag.scope})\n"
            f"- **Issue**: {flag.finding_statement}\n"
            f"- **Investor/Lessor Impact**: {flag.rationale}\n"
            f"- **Sources**: {citations}"
        )
    lines.append("### Sources")
    flag_source_ids = {source_id for flag in analysis.red_flags for source_id in flag.source_ids}
    matching = [source for source in sources if source.source_id in flag_source_ids]
    if not matching:
        lines.append("- Unavailable: no reliable sources were retained for this section.")
    for source in matching:
        published = source.publication_date.isoformat() if source.publication_date else "publication date unavailable"
        lines.append(f"- {source.source_id}: {source.title} — {source.publisher}; published {published}; {source.url}")
    lines.append("\n## Scope Deferred\nAssessment View (Recommendation) and Appendix A Country Risk require later capabilities.")
    return "\n\n".join(lines) + "\n"


def _render_benchmarking_table(analysis: CountryRiskAnalysis) -> str:
    lines = [
        "### Jurisdictional Risk Benchmarking",
        analysis.benchmarking_summary,
        "",
        "| Country | CTC (25%) | Repossession (25%) | ICAO Safety (20%) | Bankruptcy/Litigation (15%) | Overall Score |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if not analysis.benchmarking_scores:
        lines.append(f"| {analysis.country_name} | Unavailable | Unavailable | Unavailable | Unavailable | Unavailable |")
    else:
        for score in analysis.benchmarking_scores:
            lines.append(
                f"| {score.country} | {score.ctc_score:.2f} | {score.repossession_score:.2f} | "
                f"{score.icao_safety_score:.2f} | {score.bankruptcy_score:.2f} | {score.overall_score:.2f} |"
            )
    return "\n".join(lines)


def _country_subsection(title: str, analysis: SectionAnalysis) -> str:
    lines = [f"### {title}", analysis.summary]
    for finding in analysis.findings:
        citations = ", ".join(finding.source_ids) if finding.source_ids else "Unavailable"
        date_context = f" ({finding.date_context})" if finding.date_context else ""
        lines.append(f"- [{finding.kind}] {finding.statement}{date_context} [Sources: {citations}]")
    return "\n".join(lines)


def render_country_report(
    assessment_input: AssessmentInput,
    analysis: CountryRiskAnalysis,
    sources: list[SourceRecord],
) -> str:
    sections = [
        f"# Step 7 Country Risk Assessment: {assessment_input.airline}",
        f"Aircraft MSN: {assessment_input.msn} | Aircraft Variant: {assessment_input.aircraft_variant}",
        f"Deal Jurisdiction: {analysis.country_name} ({analysis.jurisdiction_rationale})",
        "",
        f"## Appendix A: Country Risk — {analysis.country_name}",
        _render_benchmarking_table(analysis),
        _country_subsection("Cape Town Convention Compliance", analysis.cape_town_convention),
        _country_subsection("Repossession Risk with the Airline", analysis.repossession_risk),
        _country_subsection("ICAO Country Safety Score", analysis.icao_safety),
        _country_subsection(
            "Bankruptcy Law — Repossession, Restructuring & Litigation Timelines",
            analysis.bankruptcy_law,
        ),
        _country_subsection("Overall Geopolitical Assessment", analysis.geopolitical_assessment),
    ]

    # Collect all sources referenced across the subsections
    all_findings = (
        analysis.cape_town_convention.findings
        + analysis.repossession_risk.findings
        + analysis.icao_safety.findings
        + analysis.bankruptcy_law.findings
        + analysis.geopolitical_assessment.findings
    )
    section_source_ids = {source_id for finding in all_findings for source_id in finding.source_ids}
    matching = [source for source in sources if source.source_id in section_source_ids]

    source_lines = ["### Sources"]
    if not matching:
        source_lines.append("- Unavailable: no reliable sources were retained for this section.")
    for source in matching:
        published = source.publication_date.isoformat() if source.publication_date else "publication date unavailable"
        source_lines.append(
            f"- {source.source_id}: {source.title} — {source.publisher}; published {published}; {source.url}"
        )

    sections.append("\n".join(source_lines))
    sections.append("## Scope Deferred\nAssessment View (Recommendation) requires later capability integration.")
    return "\n\n".join(sections) + "\n"


def render_assessment_view_report(
    assessment_input: AssessmentInput,
    analysis: AssessmentViewAnalysis,
    sources: list[SourceRecord],
) -> str:
    rec_labels = {
        "SUITABLE_FOR_PURCHASE_LEASE": "Suitable for Purchase / Lease Investment",
        "SUITABLE_SUBJECT_TO_CONDITIONS": "Suitable for Purchase / Lease Investment Subject to Conditions & Approvals",
        "NOT_SUITABLE": "Not Suitable for Purchase / Lease Investment",
    }
    rec_display = rec_labels.get(analysis.recommendation, analysis.recommendation)

    lines = [
        f"# Step 8 Assessment View: {assessment_input.airline}",
        f"Aircraft MSN: {assessment_input.msn} | Aircraft Variant: {assessment_input.aircraft_variant}",
        "",
        "## 7. Assessment View (Recommendation)",
        f"### Recommendation: {rec_display}",
        f"**Executive Thesis**: {analysis.headline}",
        "",
        "### Key Investment Factors",
        f"- **Airline Credit & Operational Capacity**: {analysis.airline_credit_factors}",
        f"- **Aircraft Asset Liquidity & Remarketability**: {analysis.asset_quality_factors}",
        f"- **Market & Commercial Dynamics**: {analysis.market_factors}",
        f"- **Jurisdictional & Repossession Enforceability**: {analysis.jurisdiction_factors}",
    ]

    if analysis.conditions_and_mitigants:
        lines.append("\n### Recommended Conditions & Approval Mitigants")
        for cond in analysis.conditions_and_mitigants:
            lines.append(f"- {cond}")

    lines.append(f"\n### Synthesis & Investment Rationale\n{analysis.rationale}")

    # Sources section
    source_lines = ["### Sources"]
    matching = [source for source in sources if source.source_id in set(analysis.cited_source_ids)]
    if not matching:
        # Fall back to showing sample of sources if cited_source_ids is empty
        matching = sources[:10] if sources else []
    if not matching:
        source_lines.append("- Unavailable: no reliable sources were retained for this section.")
    else:
        for source in matching:
            published = source.publication_date.isoformat() if source.publication_date else "publication date unavailable"
            source_lines.append(
                f"- {source.source_id}: {source.title} — {source.publisher}; published {published}; {source.url}"
            )

    lines.append("\n".join(source_lines))
    return "\n\n".join(lines) + "\n"


def _render_aircraft_risk_section(
    assessment_input: AssessmentInput,
    analysis: AircraftAnalysis,
    sources: list[SourceRecord],
) -> str:
    identity = analysis.identity
    identity_lines = [
        f"MSN: {identity.msn}",
        f"Aircraft variant: {identity.aircraft_variant or assessment_input.aircraft_variant}",
        f"Aircraft type: {identity.aircraft_type or 'Unavailable'}",
        f"Engine/configuration: {identity.engine_configuration or 'Unavailable'}",
        f"Current operator: {identity.current_operator or 'Unavailable'}",
        f"Current owner: {identity.current_owner or 'Unavailable'}",
        f"Identity confidence: {identity.confidence}",
    ]
    if identity.conflicts:
        identity_lines.append("Identity conflicts: " + "; ".join(identity.conflicts))
    sections = [
        "## 6. Aircraft Risk",
        "### Aircraft Identity",
        "\n".join(identity_lines),
        _section("Airline-Level Context", analysis.airline_context, sources),
        _section("Aircraft-Specific Risk", analysis.aircraft_risks, sources),
        _section("Aircraft-Type Risk", analysis.aircraft_type_risks, sources),
    ]
    return "\n\n".join(sections)


def _render_assessment_view_section(
    analysis: AssessmentViewAnalysis,
    sources: list[SourceRecord],
) -> str:
    rec_labels = {
        "SUITABLE_FOR_PURCHASE_LEASE": "Suitable for Purchase / Lease Investment",
        "SUITABLE_SUBJECT_TO_CONDITIONS": "Suitable for Purchase / Lease Investment Subject to Conditions & Approvals",
        "NOT_SUITABLE": "Not Suitable for Purchase / Lease Investment",
    }
    rec_display = rec_labels.get(analysis.recommendation, analysis.recommendation)

    lines = [
        "## 7. Assessment View (Recommendation)",
        f"### Recommendation: {rec_display}",
        f"**Executive Thesis**: {analysis.headline}",
        "",
        "### Key Investment Factors",
        f"- **Airline Credit & Operational Capacity**: {analysis.airline_credit_factors}",
        f"- **Aircraft Asset Liquidity & Remarketability**: {analysis.asset_quality_factors}",
        f"- **Market & Commercial Dynamics**: {analysis.market_factors}",
        f"- **Jurisdictional & Repossession Enforceability**: {analysis.jurisdiction_factors}",
    ]

    if analysis.conditions_and_mitigants:
        lines.append("\n### Recommended Conditions & Approval Mitigants")
        for cond in analysis.conditions_and_mitigants:
            lines.append(f"- {cond}")

    lines.append(f"\n### Synthesis & Investment Rationale\n{analysis.rationale}")

    # Sources section
    source_lines = ["### Sources"]
    matching = [source for source in sources if source.source_id in set(analysis.cited_source_ids)]
    if not matching:
        matching = sources[:10] if sources else []
    if not matching:
        source_lines.append("- Unavailable: no reliable sources were retained for this section.")
    else:
        for source in matching:
            published = source.publication_date.isoformat() if source.publication_date else "publication date unavailable"
            source_lines.append(
                f"- {source.source_id}: {source.title} — {source.publisher}; published {published}; {source.url}"
            )

    lines.append("\n".join(source_lines))
    return "\n\n".join(lines)


def render_final_report(
    assessment_input: AssessmentInput,
    analysis: FinalReportAnalysis,
    sources: list[SourceRecord],
) -> str:
    # 1. Executive Summary
    exec_summary_rendered = _section("1. Executive Summary", analysis.executive_summary, sources)

    # 2. Financial Risks
    fin_rendered = _section("2. Financial Risks", analysis.financial_analysis.financial_risks, sources)

    # 3. Operational Risks
    op_rendered = _section("3. Operational Risks", analysis.operational_analysis.operational_risks, sources)

    # 4. Market and Competitive Risks
    mkt_rendered = _section("4. Market and Competitive Risks", analysis.market_analysis.market_risks, sources)

    # 5. Red Flags
    rf_lines = [
        "## 5. Red Flags",
        analysis.red_flags_analysis.summary,
    ]
    if not analysis.red_flags_analysis.red_flags:
        rf_lines.append("- No material red flags identified based on the available evidence.")
    for i, flag in enumerate(analysis.red_flags_analysis.red_flags, start=1):
        citations = ", ".join(flag.source_ids) if flag.source_ids else "Unavailable"
        rf_lines.append(
            f"### Red Flag {i}: [{flag.severity.upper()}] {flag.headline} ({flag.domain.capitalize()} | {flag.scope})\n"
            f"- **Issue**: {flag.finding_statement}\n"
            f"- **Investor/Lessor Impact**: {flag.rationale}\n"
            f"- **Sources**: {citations}"
        )
    rf_lines.append("### Sources")
    flag_source_ids = {source_id for flag in analysis.red_flags_analysis.red_flags for source_id in flag.source_ids}
    matching_rf_sources = [source for source in sources if source.source_id in flag_source_ids]
    if not matching_rf_sources:
        rf_lines.append("- Unavailable: no reliable sources were retained for this section.")
    for source in matching_rf_sources:
        published = source.publication_date.isoformat() if source.publication_date else "publication date unavailable"
        rf_lines.append(f"- {source.source_id}: {source.title} — {source.publisher}; published {published}; {source.url}")
    rf_rendered = "\n\n".join(rf_lines)

    # 6. Aircraft Risk
    aircraft_rendered = _render_aircraft_risk_section(assessment_input, analysis.aircraft_analysis, sources)

    # 7. Assessment View (Recommendation)
    view_rendered = _render_assessment_view_section(analysis.assessment_view_analysis, sources)

    # Appendix A: Country Risk
    country_an = analysis.country_analysis
    country_sections = [
        "## Appendix",
        f"### Appendix A: Country Risk — {country_an.country_name}",
        f"Deal Jurisdiction Context: {country_an.country_name} ({country_an.jurisdiction_rationale})",
        _render_benchmarking_table(country_an),
        _country_subsection("Cape Town Convention Compliance", country_an.cape_town_convention),
        _country_subsection("Repossession Risk with the Airline", country_an.repossession_risk),
        _country_subsection("ICAO Country Safety Score", country_an.icao_safety),
        _country_subsection(
            "Bankruptcy Law — Repossession, Restructuring & Litigation Timelines",
            country_an.bankruptcy_law,
        ),
        _country_subsection("Overall Geopolitical Assessment", country_an.geopolitical_assessment),
    ]

    all_country_findings = (
        country_an.cape_town_convention.findings
        + country_an.repossession_risk.findings
        + country_an.icao_safety.findings
        + country_an.bankruptcy_law.findings
        + country_an.geopolitical_assessment.findings
    )
    country_source_ids = {source_id for finding in all_country_findings for source_id in finding.source_ids}
    matching_country_sources = [source for source in sources if source.source_id in country_source_ids]

    c_source_lines = ["### Sources"]
    if not matching_country_sources:
        c_source_lines.append("- Unavailable: no reliable sources were retained for this section.")
    for source in matching_country_sources:
        published = source.publication_date.isoformat() if source.publication_date else "publication date unavailable"
        c_source_lines.append(
            f"- {source.source_id}: {source.title} — {source.publisher}; published {published}; {source.url}"
        )
    country_sections.append("\n".join(c_source_lines))
    country_rendered = "\n\n".join(country_sections)

    header = [
        f"# Risk Assessment Report: {assessment_input.airline}",
        f"Aircraft MSN: {assessment_input.msn} | Aircraft Variant: {assessment_input.aircraft_variant}",
        f"Deal Jurisdiction: {country_an.country_name}",
        "---",
    ]

    full_document = [
        "\n".join(header),
        exec_summary_rendered,
        fin_rendered,
        op_rendered,
        mkt_rendered,
        rf_rendered,
        aircraft_rendered,
        view_rendered,
        country_rendered,
    ]
    return "\n\n".join(full_document) + "\n"