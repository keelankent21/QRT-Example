
SYSTEM_PROMPT = """You are QRT Strategic Analyst, an expert in utility-scale energy projects (islands & emerging markets).
Return precise, decision-ready outputs. When data is missing, make realistic, clearly-labelled assumptions.
Write in concise professional English. Keep structure and JSON schema exactly as requested."""

USER_PROMPT = """Build a strategic analysis for the following project and return ONLY a JSON object with this schema:
{
  "executive_summary": "string",
  "pestel": [{"factor":"Political","points":["..."],"assessment":"..."}],
  "swot": {
    "strengths": ["..."], "weaknesses": ["..."], "opportunities": ["..."], "threats": ["..."]
  },
  "risks": [{"category":"Regulatory","risk":"...","probability":1-5,"impact":1-5,"mitigation":"..."}],
  "legal_fiscal": "string (permits, licensing, VAT/Duty/Corporate tax, RE incentives, PPA norms)",
  "logistics": "string (ports, customs, road constraints, storage, weather windows)",
  "recommendations": ["..."]
}

Context:
- Country: {country}
- Technology: {technology}
- Capacity (MW): {capacity_mw}
- Client: {client}
- Offtaker: {offtaker}
- Horizon: {horizon}

Additional notes from user:
{user_context}

Attachments (raw excerpts, if any):
{attachments}

Requirements:
- Be specific to the country/technology whenever possible.
- For PESTEL, give 3–5 bullet points per factor + a brief assessment.
- For SWOT, keep 4–6 bullets per quadrant.
- For Risks, include at least 8–12 items spanning: Regulatory, Technical, Financial, Fiscal, Environmental, Logistic, Social/Stakeholder. 
- Keep probability/impact on a 1–5 scale. 
- In legal_fiscal, summarize permits/licensing + typical VAT/Duty + common RE incentives (if applicable).
- In logistics, cover port clearance days, likely HS-code pitfalls, route surveys, seasonal constraints.
- End with 6–10 crisp recommendations that are actionable this month.
"""
