import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Hedge Fund RL")

# =============================
# HEADER
# =============================
st.markdown("## 🏦 Hedge Fund RL System")
st.markdown("---")

try:
    from engine import (
        ranking,
        ranking_rl,
        melhor_ativo_rl,
        probabilidade,
        regime
    )

    # =============================
    # KPIs
    # =============================
    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Regime de Mercado", regime.upper())
    col2.metric("🔥 Melhor Ativo IA", ranking.index[0])
    col3.metric("🎯 Probabilidade Meta", f"{probabilidade():.2%}")

    st.markdown("---")

    # =============================
    # DECISÃO
    # =============================
    st.success(f"🚀 AÇÃO RECOMENDADA: COMPRAR {melhor_ativo_rl}")

    # =============================
    # TABS (NÍVEL PROFISSIONAL)
    # =============================
    tab1, tab2, tab3 = st.tabs(["📊 Ranking IA", "🤖 Portfólio RL", "📈 Insight"])

    # TAB 1
    with tab1:
        st.dataframe(ranking, use_container_width=True)

    # TAB 2
    with tab2:
        st.dataframe(ranking_rl, use_container_width=True)

    # TAB 3
    with tab3:
        st.write("📌 Sistema está operando com:")
        st.write("- IA preditiva")
        st.write("- Reinforcement Learning")
        st.write("- Otimização de carteira")

        if ranking.iloc[0]["Score IA"] > 0:
            st.success("Mercado favorável segundo IA")
        else:
            st.warning("Mercado com risco elevado")

except Exception as e:
    st.error(f"Erro ao carregar sistema: {e}")
