import pandas as pd
import numpy as np
import random
import os

from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# =========================
# DADOS SIMULADOS
# =========================

ativos = ["HGLG11","XPLG11","VISC11","KNIP11","MXRF11"]

dados = []

for ativo in ativos:
    preco = 100

    for i in range(200):
        preco *= (1 + np.random.normal(0.001, 0.02))
        dados.append({
            "Ticker": ativo,
            "Close": preco
        })

df = pd.DataFrame(dados)

pivot = df.pivot(columns="Ticker", values="Close")
retornos = pivot.pct_change().dropna()

if retornos.empty:
    retornos = pd.DataFrame(np.random.normal(0,0.01,(100,5)), columns=ativos)

retorno_esperado = retornos.mean()
risco = retornos.std()

# =========================
# PREVISÃO IA
# =========================

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

# =========================
# MOMENTUM E STABILITY
# =========================

momentum = retornos.rolling(20).mean().iloc[-1].fillna(0)
stability = (1/risco).replace([np.inf,-np.inf],0).fillna(0)

score = (previsoes*0.4 + momentum*0.3 + stability*0.3).fillna(0)

# =========================
# REGIME
# =========================

try:
    X_regime = retornos.mean(axis=1).values.reshape(-1,1)

    modelo_regime = KMeans(n_clusters=3, n_init=10)
    modelo_regime.fit(X_regime)

    regime = ["bear","lateral","bull"][modelo_regime.labels_[-1]]
except:
    regime = "lateral"

# =========================
# RL
# =========================

q_table = {}

def escolher_acao(state):
    if state not in q_table:
        q_table[state] = [0,0,0,0]

    if random.random() < 0.2:
        return random.randint(0,3)

    return int(np.argmax(q_table[state]))

def atualizar_q(state, action, reward):
    alpha = 0.1
    gamma = 0.9

    atual = q_table[state][action]
    novo = atual + alpha * (reward + gamma * max(q_table[state]) - atual)

    q_table[state][action] = novo


acoes = {}
pesos_rl = []

for ativo in retornos.columns:

    r = retorno_esperado.get(ativo,0)
    rk = risco.get(ativo,0.01)

    state = (round(r,4), round(rk,4))

    acao = escolher_acao(state)

    retorno_real = r + np.random.normal(0, rk)

    reward = retorno_real - rk

    atualizar_q(state, acao, reward)

    acoes[ativo] = acao

    pesos_map = [0,0.1,0.2,0.4]
    pesos_rl.append(pesos_map[acao])

pesos_rl = np.array(pesos_rl)

if pesos_rl.sum() == 0:
    pesos_rl = np.ones(len(ativos)) / len(ativos)
else:
    pesos_rl = pesos_rl / pesos_rl.sum()

# =========================
# RANKING
# =========================

ranking = pd.DataFrame({
    "Score IA": score,
    "Retorno": retorno_esperado,
    "Risco": risco
}).fillna(0).sort_values("Score IA", ascending=False)

ranking_rl = pd.DataFrame({
    "Ativo": retornos.columns,
    "Peso RL": pesos_rl
}).sort_values("Peso RL", ascending=False)

if ranking_rl.empty:
    ranking_rl = pd.DataFrame({
        "Ativo": ativos,
        "Peso RL": [1/len(ativos)]*len(ativos)
    })

melhor_ativo_rl = ranking_rl.iloc[0]["Ativo"]

# =========================
# HISTÓRICO
# =========================

arquivo = "historico.csv"

def salvar(ativo, retorno):
    df_novo = pd.DataFrame({"Ativo":[ativo],"Retorno":[retorno]})

    if os.path.exists(arquivo):
        df_antigo = pd.read_csv(arquivo)
        df_novo = pd.concat([df_antigo, df_novo])

    df_novo.to_csv(arquivo,index=False)

ret_real = np.random.normal(0.01,0.02)
salvar(melhor_ativo_rl, ret_real)

# =========================
# PERFORMANCE
# =========================

def performance():

    if not os.path.exists(arquivo):
        return pd.DataFrame()

    df_hist = pd.read_csv(arquivo)

    capital = 100000
    valores = []

    for r in df_hist["Retorno"]:
        capital *= (1 + r)
        valores.append(capital)

    df_hist["Patrimonio"] = valores

    return df_hist

perf = performance()

# =========================
# BENCHMARK
# =========================

def benchmark():

    if perf.empty:
        return []

    capital = 100000
    valores = []

    for i in range(len(perf)):
        capital *= (1 + 0.005)
        valores.append(capital)

    return valores

bench = benchmark()

# =========================
# RISCO
# =========================

def risco():

    if perf.empty:
        return 0,0

    serie = perf["Patrimonio"]
    retorno = serie.pct_change().dropna()

    vol = retorno.std()

    dd = (serie.cummax() - serie)/serie.cummax()
    max_dd = dd.max()

    return vol, max_dd

volatilidade, drawdown = risco()

# =========================
# MONTE CARLO
# =========================

portfolio = retornos.dot(pesos_rl)

def probabilidade():

    resultados = []

    media = portfolio.mean()
    desvio = portfolio.std()

    if np.isnan(media): media = 0.005
    if np.isnan(desvio): desvio = 0.02

    for i in range(100):
        valor = 100000

        for j in range(30):
            valor *= (1 + np.random.normal(media,desvio))

        resultados.append(valor)

    return float(np.mean(np.array(resultados) > 800000))
