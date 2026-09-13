from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .models import SourceRecord


AIRLINE_QUERIES = {
    "financial": "{airline} annual report financial results revenue profitability liquidity debt",
    "operational": "{airline} fleet safety operations maintenance regulatory incidents",
    "market": "{airline} competition demand fuel foreign exchange geopolitical market outlook",
    "events": "{airline} latest news restructuring financing order cancellation litigation",
}

FINANCIAL_QUERIES = {
    "financial_filings": "{airline} annual report latest interim results filing revenue profit cash flow",
    "liquidity": "{airline} cash liquidity credit facilities debt maturities lease liabilities",
    "leverage": "{airline} total debt leverage covenant refinancing default going concern",
    "financial_outlook": "{airline} financial outlook restructuring losses financing support latest",
}

OPERATIONAL_QUERIES = {
    "fleet_utilization": "{airline} fleet composition aircraft age utilization fleet size",
    "maintenance_reliability": "{airline} aircraft maintenance MRO operational reliability delays cancellations",
    "safety": "{airline} aviation safety incidents accidents safety indicators",
    "regulatory_compliance": "{airline} air operator certificate regulator oversight audit findings sanctions",
    "fleet_strategy": "{airline} fleet strategy aircraft deliveries retirements orders capacity plan",
    "management_workforce": "{airline} pilots workforce training labor relations strike staffing management",
}

MARKET_QUERIES = {
    "competition": "{airline} competition market share competitor capacity routes network",
    "demand": "{airline} passenger demand traffic trends yields seasonality route performance",
    "fuel": "{airline} fuel price exposure fuel hedging aviation outlook",
    "foreign_exchange": "{airline} foreign exchange exposure currency risk financial outlook",
    "macroeconomics": "{airline} macroeconomic travel demand inflation interest rates aviation outlook",
    "geopolitics": "{airline} geopolitical risk sanctions airspace restrictions regional instability",
    "consolidation": "{airline} airline industry consolidation alliances competitor distress",
    "routes_network": "{airline} route network changes airport capacity expansion contraction",
}

AIRCRAFT_QUERIES = {
    "identity": "{airline} {aircraft_variant} MSN {msn} registration operator owner",
    "type_configuration": "{aircraft_variant} MSN {msn} manufacturer variant engine configuration",
    "history": "{aircraft_variant} MSN {msn} maintenance incident damage grounding utilization history",
    "type_market": "{airline} {aircraft_variant} fleet demand orderbook lease rates market value",
    "remarketing": "{aircraft_variant} re-lease saleability part-out teardown economics",
}

COUNTRY_QUERIES = {
    "jurisdiction_identity": "{airline} {country} country of domicile headquarters aircraft registration jurisdiction aviation financing",
    "cape_town": "{country} Cape Town Convention compliance aircraft leasing IDERA declarations creditor rights",
    "repossession": "{country} aircraft repossession risk airline insolvency creditor enforcement courts",
    "icao_safety": "{country} ICAO USOAP safety oversight audit score civil aviation authority",
    "bankruptcy_timelines": "{country} airline bankruptcy insolvency restructuring court litigation repossession timeline",
    "geopolitics": "{country} geopolitical risk sanctions political stability macroeconomic aviation risk",
}


def _canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip("/"), parts.query, ""))


def collect_airline_sources(client: Any, airline: str, accessed_date: date | None = None) -> list[SourceRecord]:
    accessed_date = accessed_date or date.today()
    records: list[SourceRecord] = []
    seen: set[str] = set()
    for category, template in AIRLINE_QUERIES.items():
        response = client.search(template.format(airline=airline), search_depth="advanced", max_results=5)
        for index, result in enumerate(response.get("results", []), start=1):
            url = _canonical_url(str(result.get("url", "")))
            if not url or url in seen:
                continue
            seen.add(url)
            records.append(
                SourceRecord(
                    source_id=f"S{len(records) + 1:03d}",
                    url=url,
                    title=str(result.get("title") or url),
                    publisher=str(result.get("publisher") or urlsplit(url).netloc),
                    accessed_date=accessed_date,
                    category=category,
                    evidence=str(result.get("content") or result.get("raw_content") or "Unavailable"),
                    authority="other",
                )
            )
    return records


# Backward-compatible alias
collect_sources = collect_airline_sources


def collect_financial_sources(
    client: Any, airline: str, accessed_date: date | None = None
) -> list[SourceRecord]:
    accessed_date = accessed_date or date.today()
    records: list[SourceRecord] = []
    seen: set[str] = set()
    for category, template in FINANCIAL_QUERIES.items():
        response = client.search(template.format(airline=airline), search_depth="advanced", max_results=5)
        for result in response.get("results", []):
            url = _canonical_url(str(result.get("url", "")))
            if not url or url in seen:
                continue
            seen.add(url)
            records.append(
                SourceRecord(
                    source_id=f"F{len(records) + 1:03d}",
                    url=url,
                    title=str(result.get("title") or url),
                    publisher=str(result.get("publisher") or urlsplit(url).netloc),
                    accessed_date=accessed_date,
                    category=category,
                    evidence=str(result.get("content") or result.get("raw_content") or "Unavailable"),
                    authority="other",
                )
            )
    return records


def collect_operational_sources(
    client: Any, airline: str, accessed_date: date | None = None
) -> list[SourceRecord]:
    accessed_date = accessed_date or date.today()
    records: list[SourceRecord] = []
    seen: set[str] = set()
    for category, template in OPERATIONAL_QUERIES.items():
        response = client.search(template.format(airline=airline), search_depth="advanced", max_results=5)
        for result in response.get("results", []):
            url = _canonical_url(str(result.get("url", "")))
            if not url or url in seen:
                continue
            seen.add(url)
            records.append(
                SourceRecord(
                    source_id=f"O{len(records) + 1:03d}",
                    url=url,
                    title=str(result.get("title") or url),
                    publisher=str(result.get("publisher") or urlsplit(url).netloc),
                    accessed_date=accessed_date,
                    category=category,
                    evidence=str(result.get("content") or result.get("raw_content") or "Unavailable"),
                    authority="other",
                )
            )
    return records


def collect_market_sources(
    client: Any, airline: str, accessed_date: date | None = None
) -> list[SourceRecord]:
    accessed_date = accessed_date or date.today()
    records: list[SourceRecord] = []
    seen: set[str] = set()
    for category, template in MARKET_QUERIES.items():
        response = client.search(template.format(airline=airline), search_depth="advanced", max_results=5)
        for result in response.get("results", []):
            url = _canonical_url(str(result.get("url", "")))
            if not url or url in seen:
                continue
            seen.add(url)
            records.append(
                SourceRecord(
                    source_id=f"M{len(records) + 1:03d}",
                    url=url,
                    title=str(result.get("title") or url),
                    publisher=str(result.get("publisher") or urlsplit(url).netloc),
                    accessed_date=accessed_date,
                    category=category,
                    evidence=str(result.get("content") or result.get("raw_content") or "Unavailable"),
                    authority="other",
                )
            )
    return records


def collect_aircraft_sources(
    client: Any,
    airline: str,
    msn: str,
    aircraft_variant: str,
    accessed_date: date | None = None,
) -> list[SourceRecord]:
    if isinstance(aircraft_variant, date):
        accessed_date = aircraft_variant
        aircraft_variant = "aircraft"
    accessed_date = accessed_date or date.today()
    variant_term = (
        aircraft_variant.strip()
        if aircraft_variant and isinstance(aircraft_variant, str) and aircraft_variant.strip()
        else "aircraft"
    )
    records: list[SourceRecord] = []
    seen: set[str] = set()
    for category, template in AIRCRAFT_QUERIES.items():
        query = template.format(airline=airline, msn=msn, aircraft_variant=variant_term)
        response = client.search(query, search_depth="advanced", max_results=5)
        for result in response.get("results", []):
            url = _canonical_url(str(result.get("url", "")))
            if not url or url in seen:
                continue
            seen.add(url)
            scope = "AIRCRAFT_TYPE" if category in {"type_market", "remarketing"} else "AIRCRAFT"
            records.append(
                SourceRecord(
                    source_id=f"A{len(records) + 1:03d}",
                    url=url,
                    title=str(result.get("title") or url),
                    publisher=str(result.get("publisher") or urlsplit(url).netloc),
                    accessed_date=accessed_date,
                    category=category,
                    evidence=str(result.get("content") or result.get("raw_content") or "Unavailable"),
                    authority="other",
                    evidence_scope=scope,
                )
            )
    return records


def collect_country_sources(
    client: Any,
    airline: str,
    country: str,
    accessed_date: date | None = None,
) -> list[SourceRecord]:
    accessed_date = accessed_date or date.today()
    country_term = country.strip() if country and country.strip() else "airline domicile"
    records: list[SourceRecord] = []
    seen: set[str] = set()
    for category, template in COUNTRY_QUERIES.items():
        query = template.format(airline=airline, country=country_term)
        response = client.search(query, search_depth="advanced", max_results=5)
        for result in response.get("results", []):
            url = _canonical_url(str(result.get("url", "")))
            if not url or url in seen:
                continue
            seen.add(url)
            records.append(
                SourceRecord(
                    source_id=f"C{len(records) + 1:03d}",
                    url=url,
                    title=str(result.get("title") or url),
                    publisher=str(result.get("publisher") or urlsplit(url).netloc),
                    accessed_date=accessed_date,
                    category=category,
                    evidence=str(result.get("content") or result.get("raw_content") or "Unavailable"),
                    authority="other",
                    evidence_scope="JURISDICTION",
                )
            )
    return records