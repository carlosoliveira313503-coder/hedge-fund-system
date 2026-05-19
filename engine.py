import pandas as pd
import numpy as np
import random
import os

from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# =========================
# 1. DADOS SIMULADOS
# =========================

ativos = ["HGLG11", "XPLG11", "VISC11", "KNIP11", "MXRF11"]

dados = []

for ativo in ativos:
    base = 100
    
    for i in range(300):
        base *= (1 + np.random.normal(0.001, 0.02))
        dados.append({
            "Ticker": ativo,
            "Close": base
        })

df = pd.DataFrame(dados)

pivot = df.pivot(columns="Ticker", values="Close")
retornos = pivot.pct_change().dropna()

retorno_esperado = retornos.mean()
risco = retornos.std()

# =========================
# 2. IA PREVISÃO
# =========================

previsoes = {}

for ativo in retornos.columns:
    serie = retornos[ativo].dropna()
    
    if len(serie) < 20:
        previsoes[ativo] = 0
        continue

    X = np.arange(len(serie)).reshape(-1,1)
    y = serie.values

    model = LinearRegression()
    model.fit(X, y)

    previsoes[ativo] = model.predict([[len(serie)]])[0]

previsoes = pd.Series(previsoes)

# =========================
# 3. MOMENTUM + STABILITY
# =========================

momentum = retornos.rolling(20).mean().iloc[-1].fillna(0)
stability = (1 / risco).replace([np.inf, -np.inf], 0).fillna(0)

# =========================
# 4. SCORE
# =========================

score = (previsoes * 0.4 + momentum * 0.3 + stability * 0.3).fillna(0)

# =========================
# 5. REGIME
# =========================

try:
    X_regime = retornos.mean(axis=1).values.reshape(-1,1)
    kmeans = KMeans(n_clusters=3, n_init=10)
    kmeans.fit(X_regime)
    regime = ["bear", "lateral", "bull"][kmeans.labels_[-1]]
except:
    regime = "lateral"

# =========================
# 6. RL
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

    peso = [0, 0.1, 0.2, 0.4][acao]
    pesos_rl.append(peso)

pesos_rl = np.array(pesos_rl)

if pesos_rl.sum() == 0:
    pesos_rl = np.ones(len(ativos)) / len(ativos)
else:
    pesos_rl = pesos_rl / pesos_rl.sum()

# =========================
# 7. RESULTADOS
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

melhor_ativo_rl = ranking_rl.iloc[0]["Ativo"]

# =========================
# 8. HISTÓRICO
# =========================

arquivo_hist = "historico.csv"

def salvar_hist(ativo, retorno):

    novo = pd.DataFrame({
        "Ativo": [ativo],
        "Retorno": [retorno]
    })

    if os.path.exists(arquivo_hist):
        antigo = pd.read_csv(arquivo_hist)
        novo = pd.concat([antigo, novo])

    novo.to_csv(arquivo_hist, index=False)

retorno_real = np.random.normal(0.01, 0.02)
salvar_hist(melhor_ativo_rl, retorno_real)

# =========================
# 9. PERFORMANCE
# =========================

def calcular_performance():

    if not os.path.exists(arquivo_hist):
        return pd.DataFrame()

    df = pd.read_csv(arquivo_hist)

    capital = 100000
    valores = []

    for r in df["Retorno"]:
        capital *= (1 + r)
        valores.append(capital)

    df["Patrimônio"] = valores

    return df

performance = calcular_performance()

# =========================
# 10. BENCHMARK (CDI SIMULADO)
# =========================

def benchmark():

    if performance.empty:
        return []

    base = 100000
    valores = []

    for _ in range(len(performance)):
        base *= (1 + 0.005)
        valores.append(base)

    return valores

benchmark_vals = benchmark()

# =========================
# 11. RISCO REAL
# =========================

def calcular_risco():

    if performance.empty:
        return 0, 0

    serie = performance["Patrimônio"]

    retorno = serie.pct_change().dropna()

    vol = retorno.std()

    drawdown = (serie.cummax() - serie) / serie.cummax()
    max_dd = drawdown.max()

    return vol, max_dd

volatilidade, drawdown = calcular_risco()

# =========================
# 12. MONTE CARLO
# =========================

portfolio_returns = retornos.dot(pesos_rl)

def probabilidade():

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
``
