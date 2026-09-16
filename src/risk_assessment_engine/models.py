from __future__ import annotations

from datetime import date
from typing import Literal, TypedDict

from pydantic import BaseModel, Field, field_validator


class AssessmentInput(BaseModel):
    airline: str = Field(min_length=1)
    msn: str = Field(min_length=1)
    aircraft_variant: str = Field(min_length=1)
    jurisdiction: str | None = None

    @field_validator("airline", "msn", "aircraft_variant")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value

    @field_validator("jurisdiction")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value if value else None


class SourceRecord(BaseModel):
    source_id: str
    url: str
    title: str
    publisher: str = "Unknown publisher"
    publication_date: date | None = None
    accessed_date: date
    category: str
    evidence: str
    authority: Literal["primary", "authoritative", "established", "other"] = "other"
    evidence_scope: Literal["AIRLINE", "AIRCRAFT", "AIRCRAFT_TYPE", "JURISDICTION", "UNKNOWN"] = "UNKNOWN"


class Finding(BaseModel):
    statement: str
    source_ids: list[str] = Field(default_factory=list)
    kind: Literal["FACT", "ANALYSIS"]
    category: str
    scope: Literal["AIRLINE", "AIRCRAFT", "AIRCRAFT_TYPE", "JURISDICTION"] = "AIRLINE"
    direction: Literal["RISK", "FAVORABLE", "NEUTRAL"] = "RISK"
    materiality: Literal["low", "medium", "high"] = "medium"
    confidence: Literal["low", "medium", "high"] = "medium"
    date_context: str | None = None


class SectionAnalysis(BaseModel):
    summary: str
    findings: list[Finding] = Field(default_factory=list)


class AirlineAnalysis(BaseModel):
    executive_summary: SectionAnalysis


class FinancialAnalysis(BaseModel):
    financial_risks: SectionAnalysis


class OperationalAnalysis(BaseModel):
    operational_risks: SectionAnalysis


class MarketAnalysis(BaseModel):
    market_risks: SectionAnalysis


class AircraftIdentity(BaseModel):
    msn: str
    manufacturer: str | None = None
    aircraft_type: str | None = None
    aircraft_variant: str | None = None
    variant: str | None = None
    build_year: int | None = None
    engine_configuration: str | None = None
    registration: str | None = None
    current_operator: str | None = None
    current_owner: str | None = None
    confidence: Literal["unavailable", "low", "medium", "high"] = "unavailable"
    supporting_source_ids: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)


class AircraftAnalysis(BaseModel):
    identity: AircraftIdentity
    airline_context: SectionAnalysis
    aircraft_risks: SectionAnalysis
    aircraft_type_risks: SectionAnalysis


class RedFlagItem(BaseModel):
    headline: str
    domain: Literal["financial", "operational", "market", "aircraft"]
    severity: Literal["high", "critical"] = "high"
    finding_statement: str
    source_ids: list[str] = Field(default_factory=list)
    rationale: str
    scope: Literal["AIRLINE", "AIRCRAFT", "AIRCRAFT_TYPE"] = "AIRLINE"


class RedFlagsAnalysis(BaseModel):
    summary: str
    red_flags: list[RedFlagItem] = Field(default_factory=list)


class BenchmarkScore(BaseModel):
    country: str
    ctc_score: float
    repossession_score: float
    icao_safety_score: float
    bankruptcy_score: float
    overall_score: float


class CountryRiskAnalysis(BaseModel):
    country_name: str
    jurisdiction_rationale: str
    benchmarking_summary: str
    benchmarking_scores: list[BenchmarkScore] = Field(default_factory=list)
    cape_town_convention: SectionAnalysis
    repossession_risk: SectionAnalysis
    icao_safety: SectionAnalysis
    bankruptcy_law: SectionAnalysis
    geopolitical_assessment: SectionAnalysis


class AssessmentViewAnalysis(BaseModel):
    recommendation: Literal[
        "SUITABLE_FOR_PURCHASE_LEASE",
        "SUITABLE_SUBJECT_TO_CONDITIONS",
        "NOT_SUITABLE",
    ]
    headline: str
    airline_credit_factors: str
    asset_quality_factors: str
    market_factors: str
    jurisdiction_factors: str
    conditions_and_mitigants: list[str] = Field(default_factory=list)
    rationale: str
    cited_source_ids: list[str] = Field(default_factory=list)


class FinalReportAnalysis(BaseModel):
    executive_summary: SectionAnalysis
    financial_analysis: FinancialAnalysis
    operational_analysis: OperationalAnalysis
    market_analysis: MarketAnalysis
    aircraft_analysis: AircraftAnalysis
    red_flags_analysis: RedFlagsAnalysis
    assessment_view_analysis: AssessmentViewAnalysis
    country_analysis: CountryRiskAnalysis


class GraphState(TypedDict, total=False):
    assessment_input: AssessmentInput
    sources: list[SourceRecord]
    analysis: AirlineAnalysis
    financial_sources: list[SourceRecord]
    financial_analysis: FinancialAnalysis
    operational_sources: list[SourceRecord]
    operational_analysis: OperationalAnalysis
    market_sources: list[SourceRecord]
    market_analysis: MarketAnalysis
    aircraft_sources: list[SourceRecord]
    aircraft_identity: AircraftIdentity
    aircraft_analysis: AircraftAnalysis
    red_flags_analysis: RedFlagsAnalysis
    country_sources: list[SourceRecord]
    country_analysis: CountryRiskAnalysis
    assessment_view_analysis: AssessmentViewAnalysis
    executive_summary: SectionAnalysis
    final_report_analysis: FinalReportAnalysis
    report: str
    error: str
