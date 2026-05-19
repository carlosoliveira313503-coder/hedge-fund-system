import pandas as pd
import numpy as np
import random

from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# =========================
# 1. DADOS (SIMULAÇÃO SEGURA)
# =========================

ativos = ["HGLG11", "XPLG11", "VISC11", "KNIP11", "MXRF11"]

dados = []

for ativo in ativos:
    base = 100 + np.random.normal(0, 2)

    for i in range(200):
        base = base * (1 + np.random.normal(0.001, 0.02))
        dados.append({
            "Ticker": ativo,
            "Close": base
        })

df = pd.DataFrame(dados)

# =========================
# 2. RETORNOS
# =========================

pivot = df.pivot(columns="Ticker", values="Close")
retornos = pivot.pct_change().dropna()

# fallback
if retornos.empty:
    retornos = pd.DataFrame(np.random.normal(0, 0.01, (100, 5)), columns=ativos)

retorno_esperado = retornos.mean()
risco = retornos.std()

# =========================
# 3. IA PREVISÃO (SEGURA)
# =========================

previsoes = {}

for ativo in retornos.columns:

    serie = retornos[ativo].dropna()

    if len(serie) < 20:
        previsoes[ativo] = 0
        continue

    try:
        X = np.arange(len(serie)).reshape(-1,1)
        y = serie.values

        model = LinearRegression()
        model.fit(X, y)

        previsoes[ativo] = model.predict([[len(serie)]])[0]

    except:
        previsoes[ativo] = 0

previsoes = pd.Series(previsoes)

# =========================
# 4. MOMENTUM + STABILITY
# =========================

momentum = retornos.rolling(20).mean().iloc[-1].fillna(0)
stability = (1 / risco).replace([np.inf, -np.inf], 0).fillna(0)

# =========================
# 5. SCORE
# =========================

score = (
    previsoes * 0.4 +
    momentum * 0.3 +
    stability * 0.3
).fillna(0)

# =========================
# 6. REGIME (SEGURA)
# =========================

try:
    X_regime = retornos.mean(axis=1).values.reshape(-1,1)

    kmeans = KMeans(n_clusters=3, n_init=10, random_state=0)
    kmeans.fit(X_regime)

    cluster = kmeans.labels_[-1]

    regime = ["bear", "lateral", "bull"][cluster]

except:
    regime = "lateral"

# =========================
# 7. RL (ROBUSTO)
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

    r = retorno_esperado.get(ativo, 0)
    rk = risco.get(ativo, 0.01)

    state = (round(r,4), round(rk,4))

    acao = escolher_acao(state)

    retorno_real = r + np.random.normal(0, rk)
    reward = retorno_real - rk

    atualizar_q(state, acao, reward)

    acoes[ativo] = acao

    # converter para peso
    if acao == 0:
        peso = 0
    elif acao == 1:
        peso = 0.1
    elif acao == 2:
        peso = 0.2
    else:
        peso = 0.4

    pesos_rl.append(peso)

pesos_rl = np.array(pesos_rl)

# fallback
if pesos_rl.sum() == 0:
    pesos_rl = np.ones(len(ativos)) / len(ativos)
else:
    pesos_rl = pesos_rl / pesos_rl.sum()

# =========================
# 8. RANKINGS (SAFE)
# =========================

ranking = pd.DataFrame({
    "Score IA": score,
    "Retorno": retorno_esperado,
    "Risco": risco
}).fillna(0)

ranking = ranking.sort_values("Score IA", ascending=False)

ranking_rl = pd.DataFrame({
    "Ativo": retornos.columns,
    "Peso RL": pesos_rl
})

ranking_rl = ranking_rl.sort_values("Peso RL", ascending=False)

# fallback FINAL (CRÍTICO)
if ranking_rl.empty:
    ranking_rl = pd.DataFrame({
        "Ativo": ativos,
        "Peso RL": [1/len(ativos)]*len(ativos)
    })

melhor_ativo_rl = ranking_rl.iloc[0]["Ativo"]

# =========================
# 9. MONTE CARLO (SAFE)
# =========================

portfolio_returns = retornos.dot(pesos_rl)

def probabilidade():

    try:
        resultados = []

        media = portfolio_returns.mean()
        desvio = portfolio_returns.std()

        if np.isnan(media): media = 0.005
        if np.isnan(desvio): desvio = 0.02

        for _ in range(100):
            valor = 100000

            for _ in range(30):
                retorno = np.random.normal(media, desvio)
                valor *= (1 + retorno)

            resultados.append(valor)

        return float(np.mean(np.array(resultados) > 800000))

    except:
        return 0.5
