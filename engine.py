import pandas as pd
import numpy as np
import random

from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# =========================
# 1. GERAR DADOS (ESTÁVEL)
# =========================

ativos = ["HGLG11", "XPLG11", "VISC11", "KNIP11", "MXRF11"]

dados = []

for ativo in ativos:
    base = 100 + np.random.normal(0, 2)

    for i in range(300):
        base = base * (1 + np.random.normal(0.001, 0.02))
        dados.append({
            "Ticker": ativo,
            "Close": base
        })

df = pd.DataFrame(dados)

# =========================
# 2. MATRIZ DE RETORNOS
# =========================

pivot = df.pivot(columns="Ticker", values="Close")
retornos = pivot.pct_change().dropna()

retorno_esperado = retornos.mean()
risco = retornos.std()

# =========================
# 3. IA DE PREVISÃO
# =========================

previsoes = {}

for ativo in retornos.columns:
    serie = retornos[ativo].dropna()

    if len(serie) < 30:
        previsoes[ativo] = 0
        continue

    X = np.arange(len(serie)).reshape(-1,1)
    y = serie.values

    model = LinearRegression()
    model.fit(X, y)

    previsoes[ativo] = model.predict([[len(serie)]])[0]

previsoes = pd.Series(previsoes)

# =========================
# 4. MOMENTUM + STABILITY
# =========================

momentum = retornos.rolling(20).mean().iloc[-1].fillna(0)
stability = (1 / risco).replace([np.inf, -np.inf], 0).fillna(0)

# =========================
# 5. SCORE IA
# =========================

score = (
    previsoes * 0.4 +
    momentum * 0.3 +
    stability * 0.3
)

# =========================
# 6. REGIME (IA)
# =========================

X_regime = retornos.mean(axis=1).values.reshape(-1,1)

kmeans = KMeans(n_clusters=3, n_init=10, random_state=0)
kmeans.fit(X_regime)

cluster = kmeans.labels_[-1]

if cluster == 0:
    regime = "bear"
elif cluster == 1:
    regime = "lateral"
else:
    regime = "bull"

# =========================
# 7. OTIMIZAÇÃO
# =========================

def otimizar_portfolio(retornos):

    n = len(retornos.columns)
    melhor_sharpe = -999
    melhor_peso = None

    for _ in range(3000):

        pesos = np.random.random(n)
        pesos /= np.sum(pesos)

        retorno = np.sum(retornos.mean() * pesos)
        risco = np.sqrt(np.dot(pesos.T, np.dot(retornos.cov(), pesos)))

        if risco == 0:
            continue

        sharpe = retorno / risco

        if sharpe > melhor_sharpe:
            melhor_sharpe = sharpe
            melhor_peso = pesos

    return melhor_peso

pesos_otimos = otimizar_portfolio(retornos)

# =========================
# 8. REINFORCEMENT LEARNING
# =========================

q_table = {}

def get_state(r, risk):
    return (round(r,4), round(risk,4))

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

for ativo in retornos.columns:

    r = retorno_esperado[ativo]
    rk = risco[ativo]

    state = get_state(r, rk)

    action = escolher_acao(state)

    retorno_real = r + np.random.normal(0, rk)

    reward = retorno_real - rk

    atualizar_q(state, action, reward)

    acoes[ativo] = action

# =========================
# 9. CONVERTER RL → PESOS
# =========================

pesos_rl = []

for ativo in retornos.columns:

    a = acoes[ativo]

    if a == 0:
        peso = 0
    elif a == 1:
        peso = 0.1
    elif a == 2:
        peso = 0.2
    else:
        peso = 0.4

    pesos_rl.append(peso)

pesos_rl = np.array(pesos_rl)

if pesos_rl.sum() > 0:
    pesos_rl = pesos_rl / pesos_rl.sum()

# =========================
# 10. RESULTADOS
# =========================

ranking = pd.DataFrame({
    "Score IA": score,
    "Retorno": retorno_esperado,
    "Risco": risco
}).sort_values("Score IA", ascending=False)

ranking_rl = pd.DataFrame({
    "Ativo": retornos.columns,
    "Peso RL": pesos_rl
}).sort_values("Peso RL", ascending=False)

melhor_ativo_rl = ranking_rl.iloc[0]["Ativo"]

# =========================
# 11. MONTE CARLO
# =========================

portfolio_returns = retornos.dot(pesos_rl)

def probabilidade():

    resultados = []

    media = portfolio_returns.mean()
    desvio = portfolio_returns.std()

    if np.isnan(media):
        media = 0.005

    if np.isnan(desvio):
        desvio = 0.02

    for _ in range(100):
        valor = 100000

        for _ in range(30):
            retorno = np.random.normal(media, desvio)
            valor *= (1 + retorno)

        resultados.append(valor)

    return float(np.mean(np.array(resultados) > 800000))
