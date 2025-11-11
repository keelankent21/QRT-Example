
import io
import pandas as pd

def to_markdown_report(res: dict) -> str:
    sw = res["swot"]
    pestel_md = ""
    if hasattr(res["pestel"], "iterrows"):
        for _, row in res["pestel"].iterrows():
            pts = "\n".join([f"  - {p}" for p in row.get("points", [])])
            pestel_md += f"### {row.get('factor','')}" + "\n" + pts + "\n\n"

    risks_md = ""
    if isinstance(res["risks"], pd.DataFrame) and not res["risks"].empty:
        risks_md = res["risks"].to_markdown(index=False)

    md = f"""# QRT Strategic Analysis

## Executive Summary
{res['executive_summary']}

## PESTEL
{pestel_md}

## SWOT
**Strengths**
- {chr(10).join(sw.get("strengths", []))}

**Weaknesses**
- {chr(10).join(sw.get("weaknesses", []))}

**Opportunities**
- {chr(10).join(sw.get("opportunities", []))}

**Threats**
- {chr(10).join(sw.get("threats", []))}

## Legal & Fiscal
{res['legal_fiscal']}

## Logistics & Infrastructure
{res['logistics']}

## Top Risks
{risks_md}

## Recommendations
- {chr(10).join(res.get("recommendations", []))}
"""
    return md

def risks_to_csv_bytes(df: pd.DataFrame) -> bytes:
    if not isinstance(df, pd.DataFrame) or df.empty:
        df = pd.DataFrame(columns=["category","risk","probability","impact","mitigation","score","priority"])
    return df.to_csv(index=False).encode("utf-8")

def markdown_to_pdf_bytes(md_text: str):
    try:
        from markdown import markdown
        import pdfkit  # requires wkhtmltopdf on host
        html = markdown(md_text)
        pdf = pdfkit.from_string(html, False)
        return pdf
    except Exception:
        return None
