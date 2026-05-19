import pandas as pd
import numpy as np

# =========================
# DADOS (FIOS SIMULADOS ESTÁVEIS)
# =========================

ativos = ["HGLG11", "XPLG11", "VISC11", "KNIP11", "MXRF11"]

dados = []

for ativo in ativos:
    for i in range(200):
        dados.append({
            "Ticker": ativo,
            "Close": 100 + np.random.normal(0, 5)
        })

df = pd.DataFrame(dados)

# =========================
# MÉTRICAS
# =========================

precos = df.groupby("Ticker")["Close"].last()

retornos = df.groupby("Ticker")["Close"].pct_change()
retornos = retornos.groupby(df["Ticker"]).mean()

risco = df.groupby("Ticker")["Close"].pct_change()
risco = risco.groupby(df["Ticker"]).std()

# ✅ CONVERTE PARA SERIES VÁLIDAS
retornos = pd.Series(retornos).fillna(0)
risco = pd.Series(risco).fillna(0)

retornos = retornos.reindex(precos.index).fillna(0)
risco = risco.reindex(precos.index).fillna(0)

score = (retornos * 0.5) - (risco * 0.3)

score = score.reindex(precos.index).fillna(0)

# =========================
# RANKING
# =========================

ranking = pd.DataFrame({
    "Preço": list(precos),
    "Retorno": list(retornos),
    "Risco": list(risco),
    "Score": list(score)
}, index=precos.index)

ranking = ranking.sort_values("Score", ascending=False)

# =========================
# MONTE CARLO
# =========================

def probabilidade():
    resultados = []

    media = retornos.mean()
    desvio = risco.mean()

    if pd.isna(media) or media == 0:
        media = 0.005

    if pd.isna(desvio) or desvio == 0:
        desvio = 0.02

    for _ in range(100):
        valor = 100000

        for _ in range(30):
            retorno = np.random.normal(media, desvio)
            valor *= (1 + retorno)

        resultados.append(valor)

    return float(np.mean(np.array(resultados) > 800000))
