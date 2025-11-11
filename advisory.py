from openai import OpenAI
import os

def _get_openai_key():
    try:
        from streamlit.runtime.secrets import secrets as st_secrets
        k = st_secrets.get("OPENAI_API_KEY")
        if k: return k
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")

_client = OpenAI(api_key=_get_openai_key())

SYSTEM = ("You are QRT Advisor Chat, a concise senior consultant for renewable projects. "
          "Answer with short, specific, actionable guidance. If data is unknown, say so and propose how to find it.")

def ask_advisor(user_question: str, context_blob: str) -> str:
    msg = [
        {"role":"system","content": SYSTEM},
        {"role":"user","content": f"Context:\n{context_blob}\n\nQuestion:\n{user_question}"}
    ]
    r = _client.chat.completions.create(model="gpt-4o-mini", messages=msg, temperature=0.2)
    return r.choices[0].message.content
