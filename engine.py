import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

ativos = ["HGLG11","XPLG11","VISC11","KNIP11","MXRF11"]

# =========================
# DADOS
# =========================
dados = []
for ativo in ativos:
    preco = 100
    for _ in range(200):
        preco *= (1 + np.random.normal(0.001, 0.02))
        dados.append({"Ticker": ativo, "Close": preco})

df = pd.DataFrame(dados)

pivot = df.pivot(columns="Ticker", values="Close")
retornos = pivot.pct_change().dropna()

# proteção
if retornos.empty:
    retornos = pd.DataFrame(np.random.normal(0,0.01,(100,5)), columns=ativos)

retorno_esperado = retornos.mean()
risco = retornos.std()

# =========================
# IA COM PROTEÇÃO
# =========================
previsoes = {}

for ativo in retornos.columns:
    serie = retornos[ativo].dropna()

    # ✅ PROTEÇÃO TOTAL
    if serie is None or len(serie) == 0:
        previsoes[ativo] = 0
        continue

    if len(serie) < 20:
        previsoes[ativo] = 0
        continue

    try:
        X = np.arange(len(serie)).reshape(-1,1)
        y = serie.values

        model = LinearRegression()
        model.fit(X,y)

        previsoes[ativo] = model.predict([[len(serie)]])[0]

    except:
        previsoes[ativo] = 0

previsoes = pd.Series(previsoes)

momentum = retornos.rolling(20).mean().iloc[-1].fillna(0)
stability = (1/risco).replace([np.inf,-np.inf],0).fillna(0)

score = (previsoes*0.4 + momentum*0.3 + stability*0.3).fillna(0)

# =========================
# REGIME
# =========================
try:
    X_regime = retornos.mean(axis=1).values.reshape(-1,1)
    km = KMeans(n_clusters=3, n_init=10)
    km.fit(X_regime)
    regime = ["bear","lateral","bull"][km.labels_[-1]]
except:
    regime = "lateral"

# =========================
# RL SIMPLES
# =========================
pesos_rl = np.ones(len(ativos))/len(ativos)

ranking = pd.DataFrame({
    "Score IA": score,
    "Retorno": retorno_esperado,
    "Risco": risco
}).sort_values("Score IA", ascending=False)

ranking_rl = pd.DataFrame({
    "Ativo": ranking.index,
    "Peso RL": pesos_rl
})

melhor_ativo_rl = ranking.index[0]

# =========================
# HISTÓRICO
# =========================
arquivo = "historico.csv"

def salvar():
    novo = pd.DataFrame({"Retorno":[np.random.normal(0.01,0.02)]})
    if os.path.exists(arquivo):
        novo = pd.concat([pd.read_csv(arquivo), novo])
    novo.to_csv(arquivo,index=False)

salvar()

# =========================
# PERFORMANCE
# =========================
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

# =========================
# RISCO
# =========================
if perf.empty:
    volatilidade = 0
    drawdown = 0
else:
    serie = perf["Patrimonio"]
    ret = serie.pct_change().dropna()
    volatilidade = ret.std()
    drawdown = ((serie.cummax()-serie)/serie.cummax()).max()

# =========================
# BENCHMARK
# =========================
if perf.empty:
    bench = []
else:
    cap = 100000
    bench = []
    for _ in range(len(perf)):
        cap *= (1+0.005)
        bench.append(cap)

# =========================
# PROBABILIDADE
# =========================
def probabilidade():
    return 0.5
    
