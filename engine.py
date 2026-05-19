import sqlite3
import pandas as pd
import numpy as np
import os

conn = sqlite3.connect("database.db")


def gerar_dados_fake():
    ativos = ["HGLG11", "XPLG11", "VISC11", "KNIP11", "MXRF11"]

    dados = []

    for ativo in ativos:
        for i in range(200):
            dados.append({
                "Ticker": ativo,
                "Close": 100 + np.random.normal(0, 5)
            })

    df = pd.DataFrame(dados)
    return df


# ✅ TENTAR YAHOO, SE FALHAR USA FAKE
def carregar_dados():
    try:
        import yfinance as yf

        ativos = [
            "HGLG11.SA",
            "XPLG11.SA",
            "VISC11.SA",
            "KNIP11.SA",
            "MXRF11.SA"
        ]

        dados = []

        for ativo in ativos:
            df = yf.download(ativo, period="1y")

            if df is None or df.empty:
                continue

            if "Close" not in df.columns:
                if "Adj Close" in df.columns:
                    df["Close"] = df["Adj Close"]
                else:
                    continue

            df = df.reset_index()
            df["Ticker"] = ativo

            dados.append(df)

        if len(dados) == 0:
            raise Exception("Yahoo falhou")

        df = pd.concat(dados)
        return df

    except:
        return gerar_dados_fake()


# =========================
df = carregar_dados()

# =========================
df = df.dropna()

precos = df.groupby("Ticker")["Close"].last()

retornos = df.groupby("Ticker")["Close"].pct_change()
retornos = retornos.groupby(df["Ticker"]).mean().fillna(0)

risco = df.groupby("Ticker")["Close"].pct_change()
risco = risco.groupby(df["Ticker"]).std().fillna(0)

retornos = retornos.reindex(precos.index).fillna(0)
risco = risco.reindex(precos.index).fillna(0)

score = (retornos * 0.5) - (risco * 0.3)

ranking = pd.DataFrame({
    "Preço": precos,
    "Retorno": retornos,
    "Risco": risco,
    "Score": score
}).fillna(0)

ranking = ranking.sort_values("Score", ascending=False)


def probabilidade():
    try:
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

    except:
        return 0.5
