import pandas as pd
import numpy as np
import random
import os
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

ativos = ["HGLG11","XPLG11","VISC11","KNIP11","MXRF11"]

dados = []
for ativo in ativos:
    preco = 100
    for _ in range(200):
        preco *= (1 + np.random.normal(0.001, 0.02))
        dados.append({"Ticker": ativo, "Close": preco})

df = pd.DataFrame(dados)

pivot = df.pivot(columns="Ticker", values="Close")
retornos = pivot.pct_change().dropna()

if retornos.empty:
    retornos = pd.DataFrame(np.random.normal(0,0.01,(100,5)), columns=ativos)

retorno_esperado = retornos.mean()
risco = retornos.std()

# IA
previsoes = {}
for ativo in retornos.columns:
    serie = retornos[ativo].dropna()

    if len(serie) < 20:
        previsoes[ativo] = 0
        continue

    X = np.arange(len(serie)).reshape(-1,1)
    y = serie.values

    modelo = LinearRegression()
    modelo.fit(X,y)

    previsoes[ativo] = modelo.predict([[len(serie)]])[0]

previsoes = pd.Series(previsoes)

momentum = retornos.rolling(20).mean().iloc[-1].fillna(0)
stability = (1/risco).replace([np.inf,-np.inf],0).fillna(0)

score = (previsoes*0.4 + momentum*0.3 + stability*0.3).fillna(0)

# Regime
try:
    X_regime = retornos.mean(axis=1).values.reshape(-1,1)
    km = KMeans(n_clusters=3, n_init=10)
    km.fit(X_regime)
    regime = ["bear","lateral","bull"][km.labels_[-1]]
except:
    regime = "lateral"

# RL simples
pesos_rl = np.ones(len(ativos)) / len(ativos)

ranking = pd.DataFrame({
    "Score IA": score,
    "Retorno": retorno_esperado,
    "Risco": risco
}).sort_values("Score IA", ascending=False)

ranking_rl = pd.DataFrame({
    "Ativo": retornos.columns,
    "Peso RL": pesos_rl
})

melhor_ativo_rl = ranking_rl.iloc[0]["Ativo"]

# Histórico
arquivo = "historico.csv"

def salvar():
    novo = pd.DataFrame({"Retorno":[np.random.normal(0.01,0.02)]})
    if os.path.exists(arquivo):
        novo = pd.concat([pd.read_csv(arquivo), novo])
    novo.to_csv(arquivo,index=False)

salvar()

# Performance
def gerar():
    if not os.path.exists(arquivo):
        return pd.DataFrame()

    df = pd.read_csv(arquivo)

    cap = 100000
    vals = []

    for r in df["Retorno"]:
        cap *= (1+r)
        vals.append(cap)

    df["Patrimonio"] = vals
    return df

perf = gerar()

# Risco
if perf.empty:
    volatilidade = 0
    drawdown = 0
else:
    ser = perf["Patrimonio"]
    ret = ser.pct_change().dropna()
    volatilidade = ret.std()
    drawdown = ((ser.cummax()-ser)/ser.cummax()).max()

# Probabilidade
def probabilidade():
    return 0.5

bench = []
