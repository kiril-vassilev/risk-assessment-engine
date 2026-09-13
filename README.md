# Risk Assessment Engine

An evidence-grounded GenAI agent that generates comprehensive **Risk Assessment Reports** for aircraft considered for lease investments to airlines. The system combines web intelligence from Tavily with Azure OpenAI structured reasoning across financial condition, flight operations, market competition, asset liquidity, red flag synthesis, jurisdiction risk (Appendix A), and a final investment recommendation.

## Final Report Structure

1. **Executive Summary**: Overview of airline scale, aircraft asset, principal risks, positive/negative factors, and overall investment view.
2. **Financial Risks**: Revenue, profitability, operating cash flow, liquidity buffers, leverage/debt, lease liabilities, and financial trends.
3. **Operational Risks**: Fleet composition/age/utilization, maintenance & reliability, safety records, and regulatory compliance.
4. **Market and Competitive Risks**: Route competition, passenger demand, fuel price & FX sensitivity, macroeconomic resilience, and geopolitical exposure.
5. **Red Flags**: 3–6 prioritized material vulnerabilities requiring lessor/investor attention with clear rationale.
6. **Aircraft Risk**: Aircraft identity, airline-level context, aircraft-specific risk, and aircraft-type liquidity & remarketing economics.
7. **Assessment View (Recommendation)**: Investment suitability decision (`Suitable`, `Suitable subject to conditions`, `Not suitable`), key factors, recommended lease conditions/mitigants, and detailed rationale.
8. **Appendix A: Country Risk**: Jurisdictional benchmarking table, Cape Town Convention compliance, repossession risk, ICAO safety audit scores, bankruptcy litigation timelines, and geopolitical stability.

*Every section includes a dedicated `Sources` subsection maintaining full auditability and citation traceability.*

## Setup

```powershell
& .\venv\Scripts\python.exe -m pip install -e ".[test]"
Copy-Item .env.example .env
```

Set your `TAVILY_API_KEY` and Azure OpenAI settings in `.env`.

## Usage

Generate the full **Risk Assessment Report** (default workflow):

```powershell
& .\venv\Scripts\python.exe -m risk_assessment_engine.cli --airline "example-airline" --msn "12345" --aircraft-variant "A320-214" --jurisdiction "United States" --output report.txt
```

### Individual Workflows

You can also run any individual assessment capability using `--workflow`:

- `--workflow airline`: Basic airline overview
- `--workflow financial`: Financial risk analysis (Step 2)
- `--workflow operational`: Operational & fleet risk analysis (Step 3)
- `--workflow market`: Market & competitive risk analysis (Step 4)
- `--workflow aircraft`: Aircraft-specific and type-level risk analysis (Step 5)
- `--workflow red_flags`: 3–6 cross-domain synthesized red flags (Step 6)
- `--workflow country`: Appendix A Country & jurisdictional risk analysis (Step 7)
- `--workflow assessment_view`: Final investment recommendation & assessment view (Step 8)
- `--workflow final`: Full end-to-end Risk Assessment Report (default, Step 9)

## Evidence & Grounding Rules

- Every material factual claim is grounded in structured web source evidence (`F###`, `O###`, `M###`, `A###`, `C###`).
- Findings strictly distinguish `FACT` from `ANALYSIS`.
- If reliable evidence cannot be found for any field or metric, it is explicitly reported as `Unavailable`.
- The redacted example reports in `docs/` serve as analytical style/structure guides only and are never used as factual sources.