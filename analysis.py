
import os, json
import pandas as pd
from typing import Dict, Any
from prompts import SYSTEM_PROMPT, USER_PROMPT
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(messages: list, temperature: float = 0.2) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content

def run_strategic_analysis(country, technology, capacity_mw, client, offtaker, horizon, user_context="", attachments=None):
    attachments_txt = ""
    if attachments:
        for name, content in attachments.items():
            if isinstance(content, (bytes, bytearray)):
                try:
                    content = content.decode("utf-8", errors="ignore")
                except Exception:
                    content = f"[Binary file: {name}, omitted]"
            attachments_txt += f"\n\n### Attachment: {name}\n{content[:5000]}"

    user_msg = USER_PROMPT.format(
        country=country, technology=technology, capacity_mw=capacity_mw,
        client=client, offtaker=offtaker, horizon=horizon,
        user_context=user_context, attachments=attachments_txt
    )

    content = call_llm([
        {"role":"system","content": SYSTEM_PROMPT},
        {"role":"user","content": user_msg}
    ])

    try:
        data = json.loads(content)
    except Exception:
        data = {
            "executive_summary": content,
            "pestel": [],
            "swot": {"strengths":[],"weaknesses":[],"opportunities":[],"threats":[]},
            "risks": [],
            "legal_fiscal": content,
            "logistics": content,
            "recommendations": []
        }

    pestel_df = pd.DataFrame(data.get("pestel", []))
    risks_df = pd.DataFrame(data.get("risks", []))

    if "probability" in risks_df.columns and "impact" in risks_df.columns:
        try:
            risks_df["score"] = risks_df["probability"].astype(float) * risks_df["impact"].astype(float)
            def prio(s):
                s = float(s)
                if s >= 15: return "P1"
                if s >= 7: return "P2"
                return "P3"
            risks_df["priority"] = risks_df["score"].apply(prio)
        except Exception:
            pass

    return {
        "executive_summary": data.get("executive_summary",""),
        "pestel": pestel_df,
        "swot": data.get("swot", {"strengths":[],"weaknesses":[],"opportunities":[],"threats":[]}), 
        "risks": risks_df,
        "legal_fiscal": data.get("legal_fiscal",""),
        "logistics": data.get("logistics",""),
        "recommendations": data.get("recommendations",[])
    }
