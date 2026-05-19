import sqlite3
import pandas as pd
import numpy as np
import os
import yfinance as yf

# Conecta banco
conn = sqlite3.connect("database.db")

# Se tabela não existir, cria do zero
try:
    df = pd.read_sql("SELECT * FROM precos", conn)
except:
    ativos = ["HGLG11.SA","XPLG11.SA","VISC11.SA","KNIP11.SA"]
    dados = []

    for ativo in ativos:
        data = yf.download(ativo, period="1y")
        data["Ticker"] = ativo
        data = data.reset_index()
        dados.append(data)

    df = pd.concat(dados)
    df.to_sql("precos", conn, if_exists="replace", index=False)

# Cálculos
precos = df.groupby("Ticker")["Close"].last()
retornos = df.groupby("Ticker")["Close"].pct_change().groupby(df["Ticker"]).mean()
risco = df.groupby("Ticker")["Close"].pct_change().groupby(df["Ticker"]).std()

score = (retornos * 0.5) - (risco * 0.3)

ranking = pd.DataFrame({
    "Preço": precos,
    "Retorno": retornos,
    "Risco": risco,
    "Score": score
}).sort_values("Score", ascending=False)


# Monte Carlo
def probabilidade():
    resultados = []

    for _ in range(200):
        valor = 100000
        for _ in range(60):
            retorno = np.random.normal(retornos.mean(), risco.mean())
            valor *= (1 + retorno)
        resultados.append(valor)

    return np.mean(np.array(resultados) > 800000)
