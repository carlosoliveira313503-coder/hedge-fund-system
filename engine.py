import pandas as pd
import numpy as np

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
# 3. IA DE PREVISÃO (REGRESSÃO)
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

    futuro = model.predict([[len(serie)]])[0]

    previsoes[ativo] = futuro

previsoes = pd.Series(previsoes)

# =========================
# 4. MOMENTUM + STABILITY
# =========================

momentum = retornos.rolling(20).mean().iloc[-1].fillna(0)
stability = (1 / risco).replace([np.inf, -np.inf], 0).fillna(0)

# =========================
# 5. SCORE MULTI-FATOR
# =========================

score = (
    previsoes * 0.4 +
    momentum * 0.3 +
    stability * 0.3
)

score = score.fillna(0)

# =========================
# 6. DETECÇÃO DE REGIME (IA)
# =========================

X_regime = retornos.mean(axis=1).values.reshape(-1,1)

kmeans = KMeans(n_clusters=3, n_init=10, random_state=0)
kmeans.fit(X_regime)

cluster = kmeans.labels_[-1]

if cluster == 0:
