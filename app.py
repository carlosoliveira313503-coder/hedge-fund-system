import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🏦 Hedge Fund RL System")

try:
    from engine import (
        ranking,
        ranking_rl,
        melhor_ativo_rl,
        probabilidade,
        regime
    )

    st.subheader("📊 Painel Executivo")

    col1, col2, col3 = st.columns(3)

    col1.metric("Regime", regime)
    col2.metric("Melhor Ativo", ranking.index[0])
    col3.metric("Probabilidade 800k", f"{probabilidade():.2%}")

    st.success(f"🤖 RL RECOMENDA: {melhor_ativo_rl}")

    st.subheader("🔥 Ranking IA")
    st.dataframe(ranking)

    st.subheader("🤖 Decisão RL (Pesos)")
    st.dataframe(ranking_rl)

except Exception as e:
    st.error(f"Erro ao carregar sistema: {e}")
