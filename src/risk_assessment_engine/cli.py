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
from .word_converter import convert_text_report_to_word


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate airline risk research.")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Risk assessment command (default behavior)
    assess_parser = subparsers.add_parser("assess", help="Generate airline risk assessment report")
    assess_parser.add_argument("--airline", required=True)
    assess_parser.add_argument("--msn", required=True)
    assess_parser.add_argument("--aircraft-variant", "-v", dest="aircraft_variant", required=True, help="Aircraft variant (e.g., A320-214, B737-800)")
    assess_parser.add_argument("--jurisdiction", "-j", dest="jurisdiction", default=None, help="Deal/registration jurisdiction (e.g., Oman, United States, Ireland)")
    assess_parser.add_argument(
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
    assess_parser.add_argument("--output", type=Path)
    
    # Export to Word command
    export_parser = subparsers.add_parser("export-word", help="Convert text report to Word document")
    export_parser.add_argument("input", type=Path, help="Input text report file")
    export_parser.add_argument("--output", "-o", type=Path, help="Output Word document file (defaults to input filename with .docx extension)")
    
    args = parser.parse_args()
    
    # Handle export-word command
    if args.command == "export-word":
        output_file = convert_text_report_to_word(args.input, args.output)
        print(f"Report successfully converted to: {output_file}")
        return
    
    # Handle assess command or no command (backward compatibility)
    if args.command == "assess":
        airline = args.airline
        msn = args.msn
        aircraft_variant = args.aircraft_variant
        jurisdiction = args.jurisdiction
        workflow = args.workflow
        output = args.output
    else:
        # For backward compatibility with scripts that don't use subcommands
        # Create a simple assessment parser for direct arguments
        simple_parser = argparse.ArgumentParser(description="Generate airline risk research.")
        simple_parser.add_argument("--airline", required=True)
        simple_parser.add_argument("--msn", required=True)
        simple_parser.add_argument("--aircraft-variant", "-v", dest="aircraft_variant", required=True, help="Aircraft variant (e.g., A320-214, B737-800)")
        simple_parser.add_argument("--jurisdiction", "-j", dest="jurisdiction", default=None, help="Deal/registration jurisdiction (e.g., Oman, United States, Ireland)")
        simple_parser.add_argument(
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
        simple_parser.add_argument("--output", type=Path)
        simple_args = simple_parser.parse_args()
        airline = simple_args.airline
        msn = simple_args.msn
        aircraft_variant = simple_args.aircraft_variant
        jurisdiction = simple_args.jurisdiction
        workflow = simple_args.workflow
        output = simple_args.output

    settings = Settings.from_env()
    search_client = TavilyClient(api_key=settings.tavily_api_key)
    analysis_client = AzureAnalysisClient(settings)
    if workflow == "financial":
        graph = build_financial_graph(search_client, analysis_client)
    elif workflow == "operational":
        graph = build_operational_graph(search_client, analysis_client)
    elif workflow == "market":
        graph = build_market_graph(search_client, analysis_client)
    elif workflow == "aircraft":
        graph = build_aircraft_graph(search_client, analysis_client)
    elif workflow in ("red_flags", "red-flags"):
        graph = build_red_flags_graph(search_client, analysis_client)
    elif workflow in ("country", "country_risk", "country-risk"):
        graph = build_country_graph(search_client, analysis_client)
    elif workflow in ("assessment_view", "assessment-view", "recommendation"):
        graph = build_assessment_view_graph(search_client, analysis_client)
    elif workflow in ("airline", "airline_summary"):
        graph = build_airline_graph(search_client, analysis_client)
    else:
        graph = build_final_report_graph(search_client, analysis_client)
    result = graph.invoke({
        "assessment_input": AssessmentInput(
            airline=airline,
            msn=msn,
            aircraft_variant=aircraft_variant,
            jurisdiction=jurisdiction,
        )
    })
    report = result["report"]
    print(report, end="")
    if output:
        output.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()