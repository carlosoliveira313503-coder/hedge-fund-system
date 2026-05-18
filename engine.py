import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect("database.db")
df = pd.read_sql("SELECT * FROM precos", conn)

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


def monte_carlo():
    resultados = []
    for _ in range(300):
        valor = 100000
        for _ in range(120):
            retorno = np.random.normal(retornos.mean(), risco.mean())
            valor *= (1 + retorno)
        resultados.append(valor)
    return resultados


def probabilidade():
    resultados = monte_carlo()
    return np.mean(np.array(resultados) > 800000)
