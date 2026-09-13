from __future__ import annotations

import json
from typing import Any, Protocol

from .models import (
    AirlineAnalysis,
    AircraftAnalysis,
    AssessmentInput,
    AssessmentViewAnalysis,
    CountryRiskAnalysis,
    FinancialAnalysis,
    MarketAnalysis,
    OperationalAnalysis,
    RedFlagsAnalysis,
    SectionAnalysis,
    SourceRecord,
)


class AnalysisClient(Protocol):
    def analyze(self, prompt: str) -> AirlineAnalysis: ...


def build_airline_prompt(assessment_input: AssessmentInput, sources: list[SourceRecord]) -> str:
    evidence = [source.model_dump(mode="json") for source in sources]
    return (
        "You are an aviation investment risk analyst. Analyze only the airline, not the aircraft MSN. "
        "Use only the supplied evidence. Every material finding must cite one or more source_ids. "
        "Classify each finding as FACT or ANALYSIS. Say unavailable when evidence is insufficient.\n\n"
        f"Airline: {assessment_input.airline}\nAircraft MSN (pending aircraft research): {assessment_input.msn}\n"
        f"Evidence JSON:\n{json.dumps(evidence, indent=2)}"
    )


# Backward-compatible alias
build_prompt = build_airline_prompt


def build_financial_prompt(assessment_input: AssessmentInput, sources: list[SourceRecord]) -> str:
    evidence = [source.model_dump(mode="json") for source in sources]
    return (
        "You are an aviation lessor financial-risk analyst. Analyze only the airline's financial ability "
        "to support an aircraft lease. Use only the supplied evidence. Cover revenue, profitability, cash "
        "flow, liquidity, leverage, debt, lease liabilities, financing/refinancing, and financial trends. "
        "Every material finding must cite one or more source_ids. Classify each finding as FACT or ANALYSIS. "
        "Do not calculate or estimate values when inputs are missing or periods are not comparable; state "
        "unavailable instead. Include reporting periods or dates where relevant.\n\n"
        f"Airline: {assessment_input.airline}\n"
        f"Evidence JSON:\n{json.dumps(evidence, indent=2)}"
    )


def build_operational_prompt(assessment_input: AssessmentInput, sources: list[SourceRecord]) -> str:
    evidence = [source.model_dump(mode="json") for source in sources]
    return (
        "You are an aviation lessor operational-risk analyst. Analyze only the airline's operating capability, "
        "not the specific aircraft identified by the MSN. Use only the supplied evidence. Cover fleet composition, "
        "fleet age and utilization, maintenance and reliability, safety and incidents, regulatory compliance and "
        "oversight, fleet strategy and deliveries, and management and workforce risks. Every material finding must "
        "cite one or more source_ids. Classify each finding as FACT or ANALYSIS. Do not infer aircraft condition, "
        "engine configuration, or maintenance status from an MSN. State unavailable when evidence is insufficient, "
        "and include event or reporting dates where relevant.\n\n"
        f"Airline: {assessment_input.airline}\n"
        f"Evidence JSON:\n{json.dumps(evidence, indent=2)}"
    )


def build_market_prompt(assessment_input: AssessmentInput, sources: list[SourceRecord]) -> str:
    evidence = [source.model_dump(mode="json") for source in sources]
    return (
        "You are an aviation investment market-risk analyst. Analyze the airline's external market and "
        "competitive environment, not the specific aircraft identified by the MSN. Use only the supplied "
        "evidence. Cover competition, demand, fuel prices and hedging, foreign exchange, macroeconomic "
        "conditions, geopolitics, industry consolidation, and route/network changes. Identify both relevant "
        "downside risks and potentially favorable developments. For every finding, set direction to RISK, "
        "FAVORABLE, or NEUTRAL. Every material finding must cite one or more source_ids and be classified as "
        "FACT or ANALYSIS. Do not infer market share, fuel hedging, FX exposure, demand, or geopolitical impact "
        "when evidence is absent; state unavailable instead. Include dates, periods, routes, or regions where "
        "relevant. Do not treat the MSN as aircraft or market evidence.\n\n"
        f"Airline: {assessment_input.airline}\n"
        f"Evidence JSON:\n{json.dumps(evidence, indent=2)}"
    )


def build_aircraft_prompt(
    assessment_input: AssessmentInput,
    identity: Any,
    sources: list[SourceRecord],
) -> str:
    evidence = [source.model_dump(mode="json") for source in sources]
    return (
        "You are an aviation asset-risk analyst. Distinguish AIRLINE, AIRCRAFT, and AIRCRAFT_TYPE findings. "
        "Use only the supplied evidence and do not treat airline plus MSN text as verified identity. Analyze "
        "specific aircraft identity, age, engine/configuration, operator/owner, maintenance or incident history, "
        "and aircraft-type/variant liquidity, demand, orderbook, values, lease rates, re-lease, saleability, and part-out "
        "economics. Every material finding must be FACT or ANALYSIS, cite known source_ids, carry the correct scope, "
        "and include dates. Do not use AIRCRAFT_TYPE evidence to support AIRCRAFT claims. State unavailable for "
        "missing or conflicting evidence.\n\n"
        f"Airline context: {assessment_input.airline}\nMSN: {assessment_input.msn}\n"
        f"Specified aircraft variant: {assessment_input.aircraft_variant}\n"
        f"Resolved identity JSON: {identity.model_dump_json()}\n"
        f"Evidence JSON:\n{json.dumps(evidence, indent=2)}"
    )


def build_red_flags_prompt(
    assessment_input: AssessmentInput,
    financial_findings: list[Any],
    operational_findings: list[Any],
    market_findings: list[Any],
    aircraft_findings: list[Any],
    identity: Any | None = None,
) -> str:
    domain_data = {
        "financial_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in financial_findings],
        "operational_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in operational_findings],
        "market_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in market_findings],
        "aircraft_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in aircraft_findings],
        "resolved_identity": identity.model_dump(mode="json") if identity and hasattr(identity, "model_dump") else (identity or {}),
    }
    return (
        "You are an expert aviation lessor and investor risk analyst synthesizing red flags across all assessment domains. "
        "Identify the most significant immediate or potentially material vulnerabilities discovered during the assessment. "
        "Red flags must be specific, evidence-based issues requiring attention by an investor or lessor. "
        "Avoid simply repeating all risks or summarizing every section; select the issues with the greatest potential impact "
        "on the investment decision. Prioritise approximately 3–6 material red flags rather than producing an exhaustive list. "
        "Filter out minor risks and favorable developments. For each red flag, state the headline, domain (financial, operational, "
        "market, aircraft), severity (high or critical), finding_statement, originating source_ids, rationale for investor impact, "
        "and scope (AIRLINE, AIRCRAFT, or AIRCRAFT_TYPE). Do not invent claims or cite source_ids not present in the findings. "
        "If there are fewer than 3 material red flags based on the evidence, return only the verified ones.\n\n"
        f"Airline: {assessment_input.airline}\nMSN: {assessment_input.msn}\n"
        f"Specified aircraft variant: {assessment_input.aircraft_variant}\n"
        f"Domain Findings JSON:\n{json.dumps(domain_data, indent=2)}"
    )


def build_country_prompt(
    assessment_input: AssessmentInput,
    country: str,
    sources: list[SourceRecord],
) -> str:
    evidence = [source.model_dump(mode="json") for source in sources]
    return (
        f"You are an expert aviation financing and cross-border aircraft leasing legal risk analyst. "
        f"Analyze the Country Risk for the relevant jurisdiction: '{country}' in the context of leasing an aircraft "
        f"to {assessment_input.airline} (MSN {assessment_input.msn}, variant {assessment_input.aircraft_variant}).\n\n"
        f"Evaluate the following required areas strictly based on the supplied evidence:\n"
        f"1. Jurisdictional Risk Benchmarking: Provide a summary and comparative scoring across comparator jurisdictions "
        f"(e.g., target country, United States, Ireland, UAE, etc.) covering CTC (25%), Repossession (25%), ICAO Safety (20%), "
        f"Bankruptcy/Litigation (15%), and weighted Overall Score (1 = lowest risk, 5 = highest risk).\n"
        f"2. Cape Town Convention Compliance: Treaty ratification, declarations (e.g. Alternative A, IDERA), implementation, "
        f"and court enforcement record.\n"
        f"3. Repossession Risk with the Airline & Jurisdiction: Predictability, speed, and practical enforcement of lessor repossession rights.\n"
        f"4. ICAO Country Safety Score: State USOAP safety oversight audit performance, effective implementation scores, and regulator oversight.\n"
        f"5. Bankruptcy Law — Repossession, Restructuring & Litigation Timelines: Insolvency regime, stay provisions, lessor protections, and expected timeline in months.\n"
        f"6. Overall Geopolitical Assessment: Rule of law, political stability, foreign exchange / currency transferability, sanctions, and sovereign risk.\n\n"
        f"Every material finding must cite one or more source_ids and be classified as FACT or ANALYSIS with scope='JURISDICTION'. "
        f"If reliable data is not found in the evidence for any area, explicitly state that it is unavailable.\n\n"
        f"Airline: {assessment_input.airline}\nDeal Jurisdiction: {country}\n"
        f"Evidence JSON:\n{json.dumps(evidence, indent=2)}"
    )


def build_assessment_view_prompt(
    assessment_input: AssessmentInput,
    financial_findings: list[Any],
    operational_findings: list[Any],
    market_findings: list[Any],
    aircraft_findings: list[Any],
    red_flags: list[Any],
    country_analysis: Any | None = None,
    identity: Any | None = None,
) -> str:
    domain_data = {
        "financial_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in financial_findings],
        "operational_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in operational_findings],
        "market_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in market_findings],
        "aircraft_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in aircraft_findings],
        "red_flags": [rf.model_dump(mode="json") if hasattr(rf, "model_dump") else rf for rf in red_flags],
        "country_risk": country_analysis.model_dump(mode="json") if country_analysis and hasattr(country_analysis, "model_dump") else (country_analysis or {}),
        "resolved_identity": identity.model_dump(mode="json") if identity and hasattr(identity, "model_dump") else (identity or {}),
    }
    return (
        "You are an expert aviation investment committee chairman and chief credit officer. "
        "Provide the final investment assessment and recommendation (Assessment View) for purchasing/leasing "
        f"aircraft MSN {assessment_input.msn} ({assessment_input.aircraft_variant}) with a lease attached to {assessment_input.airline}.\n\n"
        "Your recommendation must be strictly grounded in the synthesized findings across all assessment domains:\n"
        "- Airline credit risk (Financial & Operational)\n"
        "- Asset liquidity, secondary market depth, orderbook, and part-out/remarketing economics (Aircraft Risk)\n"
        "- Commercial dynamics, competition, fuel/macro resilience (Market Risks)\n"
        "- Immediate vulnerabilities requiring investor attention (Red Flags)\n"
        "- Enforceability of repossession remedies, Cape Town Convention, and insolvency law (Country Risk)\n\n"
        "Choose one recommendation: 'SUITABLE_FOR_PURCHASE_LEASE', 'SUITABLE_SUBJECT_TO_CONDITIONS', or 'NOT_SUITABLE'.\n"
        "Provide a concise executive headline, detailed breakdown for airline credit factors, asset quality factors, "
        "market factors, jurisdiction factors, recommended conditions/mitigants (e.g. security deposit, maintenance reserves, L/C, Cape Town filings), "
        "a comprehensive synthesized rationale explaining the investment conclusion, and any cited source IDs.\n\n"
        f"Airline: {assessment_input.airline}\nMSN: {assessment_input.msn}\n"
        f"Aircraft Variant: {assessment_input.aircraft_variant}\n"
        f"Comprehensive Assessment Evidence JSON:\n{json.dumps(domain_data, indent=2)}"
    )


def build_executive_summary_prompt(
    assessment_input: AssessmentInput,
    financial_findings: list[Any],
    operational_findings: list[Any],
    market_findings: list[Any],
    aircraft_findings: list[Any],
    red_flags: list[Any],
    assessment_view: Any | None = None,
    country_analysis: Any | None = None,
    identity: Any | None = None,
) -> str:
    domain_data = {
        "financial_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in financial_findings],
        "operational_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in operational_findings],
        "market_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in market_findings],
        "aircraft_findings": [f.model_dump(mode="json") if hasattr(f, "model_dump") else f for f in aircraft_findings],
        "red_flags": [rf.model_dump(mode="json") if hasattr(rf, "model_dump") else rf for rf in red_flags],
        "assessment_view": assessment_view.model_dump(mode="json") if assessment_view and hasattr(assessment_view, "model_dump") else (assessment_view or {}),
        "country_risk": country_analysis.model_dump(mode="json") if country_analysis and hasattr(country_analysis, "model_dump") else (country_analysis or {}),
        "resolved_identity": identity.model_dump(mode="json") if identity and hasattr(identity, "model_dump") else (identity or {}),
    }
    return (
        "You are an expert aviation investment analyst writing Section 1: Executive Summary for a comprehensive "
        "Aircraft Risk Assessment Report. Provide a concise, high-impact overview of the airline, aircraft, "
        "principal risks, and overall investment view. Highlight the most important positive and negative factors "
        "identified across the assessment. The section should allow an executive or investment committee reader "
        "to understand the complete investment case without reading the full report.\n\n"
        "Return a structured SectionAnalysis containing:\n"
        "- summary: A clear narrative paragraph summarizing the transaction, operator, asset profile, key vulnerabilities, and overall investment thesis.\n"
        "- findings: 4 to 8 key bullet findings distinguishing FACT from ANALYSIS, citing originating source_ids, stating date context, and classifying direction as RISK, FAVORABLE, or NEUTRAL.\n\n"
        f"Airline: {assessment_input.airline}\nMSN: {assessment_input.msn}\n"
        f"Aircraft Variant: {assessment_input.aircraft_variant}\n"
        f"Deal Jurisdiction: {assessment_input.jurisdiction or 'Determined from context'}\n"
        f"Full Assessment Findings JSON:\n{json.dumps(domain_data, indent=2)}"
    )


class AzureAnalysisClient:
    def __init__(self, settings: Any) -> None:
        from openai import AzureOpenAI

        self._client = AzureOpenAI(
            api_key=settings.azure_api_key,
            azure_endpoint=settings.azure_endpoint,
            api_version=settings.azure_api_version,
        )
        self._deployment = settings.azure_deployment

    def analyze(self, prompt: str) -> AirlineAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=AirlineAnalysis,
            messages=[
                {"role": "system", "content": "Return concise, evidence-grounded airline risk analysis."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured analysis")
        return parsed

    def analyze_financial(self, prompt: str) -> FinancialAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=FinancialAnalysis,
            messages=[
                {"role": "system", "content": "Return concise, evidence-grounded financial risk analysis."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured financial analysis")
        return parsed

    def analyze_operational(self, prompt: str) -> OperationalAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=OperationalAnalysis,
            messages=[
                {"role": "system", "content": "Return concise, evidence-grounded operational risk analysis."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured operational analysis")
        return parsed

    def analyze_market(self, prompt: str) -> MarketAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=MarketAnalysis,
            messages=[
                {"role": "system", "content": "Return concise, evidence-grounded market risk analysis."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured market analysis")
        return parsed

    def analyze_aircraft(self, prompt: str) -> AircraftAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=AircraftAnalysis,
            messages=[
                {"role": "system", "content": "Return concise, evidence-grounded aircraft risk analysis."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured aircraft analysis")
        return parsed

    def analyze_red_flags(self, prompt: str) -> RedFlagsAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=RedFlagsAnalysis,
            messages=[
                {"role": "system", "content": "Return concise, prioritized red flag synthesis grounded in the provided findings."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured red flags analysis")
        return parsed

    def analyze_country(self, prompt: str) -> CountryRiskAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=CountryRiskAnalysis,
            messages=[
                {"role": "system", "content": "Return concise, evidence-grounded aviation country and jurisdictional risk analysis."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured country risk analysis")
        return parsed

    def analyze_assessment_view(self, prompt: str) -> AssessmentViewAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=AssessmentViewAnalysis,
            messages=[
                {"role": "system", "content": "Return a rigorous, concise, evidence-grounded aviation investment recommendation and assessment view."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured assessment view analysis")
        return parsed

    def analyze_executive_summary(self, prompt: str) -> SectionAnalysis:
        response = self._client.beta.chat.completions.parse(
            model=self._deployment,
            temperature=0,
            response_format=SectionAnalysis,
            messages=[
                {"role": "system", "content": "Return a concise, high-impact executive summary for an aircraft risk assessment report."},
                {"role": "user", "content": prompt},
            ],
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Azure OpenAI returned no structured executive summary analysis")
        return parsed