
import sqlite3
import pandas as pd
import numpy as np
import os

conn = sqlite3.connect("database.db")

# ✅ criar dados automaticamente se não existir
try:
    df = pd.read_sql("SELECT * FROM precos", conn)
except:
    import data_collector
    conn = sqlite3.connect("database.db")  # reconectar
    df = pd.read_sql("SELECT * FROM precos", conn)

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
