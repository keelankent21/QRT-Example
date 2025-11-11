import io
import pandas as pd

def _df_to_markdown_safe(df: pd.DataFrame) -> str:
    """Convierte un DataFrame a Markdown, incluso si falta 'tabulate'."""
    try:
        import tabulate  # noqa: F401
        return df.to_markdown(index=False)
    except Exception:
        if df is None or df.empty:
            return "_No data._"
        header = " | ".join(df.columns.astype(str))
        sep = " | ".join(["---"] * len(df.columns))
        rows = [" | ".join(map(lambda x: str(x) if x is not None else "", r))
                for r in df.astype(str).values.tolist()]
        preview = "\n".join(rows[:200])
        return f"{header}\n{sep}\n{preview}"

def to_markdown_report(res: dict) -> str:
    sw = res["swot"]
    pestel_md = ""
    if hasattr(res["pestel"], "iterrows"):
        for _, row in res["pestel"].iterrows():
            pts = row.get("points", [])
            pts_md = "\n".join([f"- {p}" for p in pts]) if isinstance(pts, list) else str(pts)
            pestel_md += f"### {row.get('factor','')}\n{pts_md}\n\n"

    risks_md = ""
    if isinstance(res.get("risks"), pd.DataFrame):
        risks_md = _df_to_markdown_safe(res["risks"])

    md = f"""# QRT Strategic Analysis

## Executive Summary
{res.get('executive_summary','')}

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
{res.get('legal_fiscal','')}

## Logistics & Infrastructure
{res.get('logistics','')}

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
    """Convierte Markdown a PDF si pdfkit/wkhtmltopdf están disponibles."""
    try:
        from markdown import markdown
        import pdfkit  # requiere wkhtmltopdf
        html = markdown(md_text)
        return pdfkit.from_string(html, False)
    except Exception:
        return None
