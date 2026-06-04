import pandas as pd

def calcular_score(df_mercado):
    """
    Executa a análise quantitativa de arbitragem.
    Normaliza o Score final para uma escala de 0.00 a 10.00 pontos.
    """
    df = df_mercado.copy()
    
    df["P_VP"] = df["P_VP"].fillna(1.0).replace(0, 1.0)
    df["DY_Anual"] = df["DY_Anual"].fillna(0.095)
    
    # Cálculo base de eficiência quantitativa
    score_bruto = (df["DY_Anual"] * 100) * (1 / df["P_VP"])
    
    # 🧮 NORMALIZAÇÃO PREMIUM: Converte o score bruto para a escala de 0.00 a 10.00 pts
    min_s = score_bruto.min()
    max_s = score_bruto.max()
    
    if max_s - min_s > 0:
        # O melhor ganha 10.00 e o menor ganha 5.00 (ajustado para dar excelente estética)
        df["Score"] = 5.0 + ((score_bruto - min_s) / (max_s - min_s)) * 5.0
    else:
        df["Score"] = 10.0
        
    df["Score"] = df["Score"].round(2)
    return df.sort_values(by="Score", ascending=False)

def construir_carteira(df_ranking_carteira, capital_disponivel):
    """
    Usa o modelo de precificação para construir a alocação ideal.
    """
    df = df_ranking_carteira.copy()
    soma_scores = df["Score"].sum()
    
    if soma_scores <= 0:
        df["Peso_Alocacao"] = 1 / len(df)
    else:
        df["Peso_Alocacao"] = df["Score"] / soma_scores
        
    df["Alocacao_Ajustada"] = round(capital_disponivel * df["Peso_Alocacao"], 2)
    return df

def calcular_renda(df_ideal):
    """
    Consolida as métricas projetadas futuras com base na carteira alvo sugerida.
    """
    df = df_ideal.copy()
    df["Renda_Mensal_Ativo"] = (df["Alocacao_Ajustada"] * df["DY_Anual"]) / 12
    
    total_patrimonio = float(df["Alocacao_Ajustada"].sum())
    total_renda_mensal = float(df["Renda_Mensal_Ativo"].sum())
    
    return total_patrimonio, round(total_renda_mensal, 2)

# ==============================================================================
# 🛑 FIM DO BLOCO - ENGINE.PY
# ==============================================================================