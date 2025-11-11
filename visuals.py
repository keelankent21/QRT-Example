import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def risk_heatmap(risks_df: pd.DataFrame):
    # Crear matriz 5x5 prob vs impact con sumatorio de score
    m = np.zeros((5,5))
    if isinstance(risks_df, pd.DataFrame) and not risks_df.empty:
        tmp = risks_df.copy()
        for col in ["probability","impact","score"]:
            if col not in tmp.columns: return None
        for _, r in tmp.iterrows():
            i = int(max(min(r["impact"],5),1))-1
            p = int(max(min(r["probability"],5),1))-1
            m[4-i, p] += float(r["score"])
    fig, ax = plt.subplots(figsize=(5,4))
    im = ax.imshow(m, aspect="auto")
    ax.set_xticks(range(5)); ax.set_yticks(range(5))
    ax.set_xticklabels([1,2,3,4,5]); ax.set_yticklabels([5,4,3,2,1])
    ax.set_xlabel("Probability"); ax.set_ylabel("Impact")
    ax.set_title("Risk Heatmap (score sum)")
    for y in range(5):
        for x in range(5):
            ax.text(x, y, f"{m[y,x]:.0f}", ha="center", va="center")
    buf = io.BytesIO(); plt.tight_layout(); fig.savefig(buf, format="png"); plt.close(fig)
    buf.seek(0); return buf

def risk_bars(risks_df: pd.DataFrame):
    if not isinstance(risks_df, pd.DataFrame) or risks_df.empty:
        return None
    grp = risks_df.groupby("priority")["score"].sum().reindex(["P1","P2","P3"]).fillna(0)
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(grp.index, grp.values)
    ax.set_title("Risk Score by Priority"); ax.set_ylabel("Score")
    buf = io.BytesIO(); plt.tight_layout(); fig.savefig(buf, format="png"); plt.close(fig)
    buf.seek(0); return buf

def pestel_radar(pestel_df: pd.DataFrame):
    if pestel_df is None or pestel_df.empty or "factor" not in pestel_df.columns:
        return None
    # puntuación simple por nº de puntos (cuantos más puntos, mayor relevancia)
    vals = pestel_df["points"].apply(lambda x: len(x) if isinstance(x, list) else 1)
    labels = pestel_df["factor"].tolist()
    N = len(labels)
    if N == 0: return None
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    vals = vals.tolist(); vals += vals[:1]; angles += angles[:1]
    fig = plt.figure(figsize=(4.8,4.8))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, vals); ax.fill(angles, vals, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title("PESTEL Radar (relative salience)")
    buf = io.BytesIO(); plt.tight_layout(); fig.savefig(buf, format="png"); plt.close(fig)
    buf.seek(0); return buf
