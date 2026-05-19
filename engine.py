import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf

conn = sqlite3.connect("database.db")

def gerar_dados():
    ativos = [
        "HGLG11.SA",
        "XPLG11.SA",
        "VISC11.SA",
        "KNIP11.SA",
        "MXRF11.SA"
    ]

    dados = []

    for ativo in ativos:
        try:
            df = yf.download(ativo, period="1y")

            if not df.empty:
                df = df.reset_index()
                df["Ticker"] = ativo
                dados.append(df)

        except:
            continue

    if len(dados) == 0:
        raise Exception("Erro ao baixar dados")

    final = pd.concat(dados)
    final.to_sql("precos", conn, if_exists="replace", index=False)

    return final


try:
    df = pd.read_sql("SELECT * FROM precos", conn)
    if df.empty:
        df = gerar_dados()
except:
    df = gerar_dados()


df = df.dropna(subset=["Close"])

precos = df.groupby("Ticker")["Close"].last()

retornos = df.groupby("Ticker")["Close"].pct_change()
retornos = retornos.groupby(df["Ticker"]).mean().fillna(0)

risco = df.groupby("Ticker")["Close"].pct_change()
risco = risco.groupby(df["Ticker"]).std().fillna(0)

retornos = retornos.reindex(precos.index).fillna(0)
risco = risco.reindex(precos.index).fillna(0)

score = (retornos * 0.5) - (risco * 0.3)
score = score.fillna(0)

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
