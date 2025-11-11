# analysis.py — QRT Strategic Analyst (Template-based, safe)

import os, json
import pandas as pd
from typing import Dict, Any
from string import Template
from openai import OpenAI

# ----------------------------
# PROMPTS (usa $placeholders)
# ----------------------------
SYSTEM_PROMPT = """You are QRT Strategic Analyst, an expert in utility-scale energy projects (islands & emerging markets).
Return precise, decision-ready outputs. When data is missing, make realistic, clearly-labelled assumptions.
Write in concise professional English. Keep structure and JSON schema exactly as requested."""

USER_PROMPT = Template("""Build a strategic analysis for the following project and return ONLY a JSON object with this schema:
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
- Country: $country
- Technology: $technology
- Capacity (MW): $capacity_mw
- Client: $client
- Offtaker: $offtaker
- Horizon: $horizon

Additional notes from user:
$user_context

Attachments (raw excerpts, if any):
$attachments

Requirements:
- Be specific to the country/technology whenever possible.
- For PESTEL, give 3–5 bullet points per factor + a brief assessment.
- For SWOT, keep 4–6 bullets per quadrant.
- For Risks, include at least 8–12 items spanning: Regulatory, Technical, Financial, Fiscal, Environmental, Logistic, Social/Stakeholder.
- Keep probability/impact on a 1–5 scale.
- In legal_fiscal, summarize permits/licensing + typical VAT/Duty + common RE incentives (if applicable).
- In logistics, cover port clearance days, likely HS-code pitfalls, route surveys, seasonal constraints.
- End with 6–10 crisp recommendations that are actionable this month.
""")

# ---------------------------------
# OpenAI client (secrets o env var)
# ---------------------------------
def _get_openai_key():
    """Busca la API key primero en Streamlit Secrets y luego en variables de entorno."""
    try:
        from streamlit.runtime.secrets import secrets as st_secrets  # en Streamlit Cloud
        key = st_secrets.get("OPENAI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=_get_openai_key())

def call_llm(messages: list, temperature: float = 0.2) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content

# ---------------------------------
# Función principal de análisis
# ---------------------------------
def run_strategic_analysis(
    country: str,
    technology: str,
    capacity_mw: float,
    client: str,
    offtaker: str,
    horizon: str,
    user_context: str = "",
    attachments: Dict[str, Any] = None
) -> Dict[str, Any]:

    # Preparar anexos como texto simple
    attachments_txt = ""
    if attachments:
        for name, content in attachments.items():
            if isinstance(content, (bytes, bytearray)):
                try:
                    content = content.decode("utf-8", errors="ignore")
                except Exception:
                    content = f"[Binary file: {name}, omitted]"
            attachments_txt += f"\n\n### Attachment: {name}\n{content[:5000]}"

    # Construir prompt con Template (evita conflictos con { })
    user_msg = USER_PROMPT.safe_substitute(
        country=country,
        technology=technology,
        capacity_mw=capacity_mw,
        client=client,
        offtaker=offtaker,
        horizon=horizon,
        user_context=user_context or "",
        attachments=attachments_txt or ""
    )

    # Llamada al modelo
    content = call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ])

    # Parseo seguro del JSON devuelto
    try:
        data = json.loads(content)
    except Exception:
        data = {
            "executive_summary": content,
            "pestel": [],
            "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
            "risks": [],
            "legal_fiscal": content,
            "logistics": content,
            "recommendations": []
        }

    # Normalizar tablas
    pestel_df = pd.DataFrame(data.get("pestel", []))
    risks_df = pd.DataFrame(data.get("risks", []))

    # Auto-priorizar riesgos si hay prob/impact
    if "probability" in risks_df.columns and "impact" in risks_df.columns:
        try:
            risks_df["score"] = risks_df["probability"].astype(float) * risks_df["impact"].astype(float)
            def prio(s):
                s = float(s)
                if s >= 15: return "P1"
                if s >= 7:  return "P2"
                return "P3"
            risks_df["priority"] = risks_df["score"].apply(prio)
        except Exception:
            pass

    return {
        "executive_summary": data.get("executive_summary", ""),
        "pestel": pestel_df,
        "swot": data.get("swot", {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}),
        "risks": risks_df,
        "legal_fiscal": data.get("legal_fiscal", ""),
        "logistics": data.get("logistics", ""),
        "recommendations": data.get("recommendations", [])
    }
