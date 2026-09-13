from __future__ import annotations

import argparse
from pathlib import Path

from tavily import TavilyClient

from .analysis import AzureAnalysisClient
from .config import Settings
from .graph import (
    build_aircraft_graph,
    build_assessment_view_graph,
    build_country_graph,
    build_final_report_graph,
    build_financial_graph,
    build_airline_graph,
    build_market_graph,
    build_operational_graph,
    build_red_flags_graph,
)
from .models import AssessmentInput


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate airline risk research.")
    parser.add_argument("--airline", required=True)
    parser.add_argument("--msn", required=True)
    parser.add_argument("--aircraft-variant", "-v", dest="aircraft_variant", required=True, help="Aircraft variant (e.g., A320-214, B737-800)")
    parser.add_argument("--jurisdiction", "-j", dest="jurisdiction", default=None, help="Deal/registration jurisdiction (e.g., Oman, United States, Ireland)")
    parser.add_argument(
        "--workflow",
        choices=(
            "final",
            "final_report",
            "final-report",
            "airline",
            "financial",
            "operational",
            "market",
            "aircraft",
            "red_flags",
            "red-flags",
            "country",
            "country_risk",
            "country-risk",
            "assessment_view",
            "assessment-view",
            "recommendation",
        ),
        default="final",
        help="Assessment workflow to execute (default: final - complete Risk Assessment Report)",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    settings = Settings.from_env()
    search_client = TavilyClient(api_key=settings.tavily_api_key)
    analysis_client = AzureAnalysisClient(settings)
    if args.workflow == "financial":
        graph = build_financial_graph(search_client, analysis_client)
    elif args.workflow == "operational":
        graph = build_operational_graph(search_client, analysis_client)
    elif args.workflow == "market":
        graph = build_market_graph(search_client, analysis_client)
    elif args.workflow == "aircraft":
        graph = build_aircraft_graph(search_client, analysis_client)
    elif args.workflow in ("red_flags", "red-flags"):
        graph = build_red_flags_graph(search_client, analysis_client)
    elif args.workflow in ("country", "country_risk", "country-risk"):
        graph = build_country_graph(search_client, analysis_client)
    elif args.workflow in ("assessment_view", "assessment-view", "recommendation"):
        graph = build_assessment_view_graph(search_client, analysis_client)
    elif args.workflow in ("airline", "airline_summary"):
        graph = build_airline_graph(search_client, analysis_client)
    else:
        graph = build_final_report_graph(search_client, analysis_client)
    result = graph.invoke({
        "assessment_input": AssessmentInput(
            airline=args.airline,
            msn=args.msn,
            aircraft_variant=args.aircraft_variant,
            jurisdiction=args.jurisdiction,
        )
    })
    report = result["report"]
    print(report, end="")
    if args.output:
        args.output.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()