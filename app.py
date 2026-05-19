import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🏦 Hedge Fund RL System")

try:
    from engine import *

    if ranking.empty:
        st.warning("Carregando dados...")
        st.stop()

    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Regime", regime.upper())
    col2.metric("🔥 Melhor Ativo IA", ranking.index[0])
    col3.metric("🎯 Probabilidade", f"{probabilidade():.2%}")

    st.success(f"🚀 AÇÃO RECOMENDADA: COMPRAR {melhor_ativo_rl}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Ranking IA",
        "🤖 Portfólio RL",
        "💰 Performance",
        "📉 Risco"
    ])

    with tab1:
        st.dataframe(ranking)

    with tab2:
        st.dataframe(ranking_rl)
        st.bar_chart(ranking_rl.set_index("Ativo"))

    with tab3:
        if perf.empty:
            st.warning("Sem histórico ainda")
        else:
            st.line_chart(perf["Patrimonio"])

            if len(bench) > 0:
                df_compare = pd.DataFrame({
                    "Sistema": perf["Patrimonio"],
                    "Benchmark": bench
                })
                st.line_chart(df_compare)

            st.dataframe(perf)

    with tab4:
        st.metric("📉 Volatilidade", round(volatilidade,4))
        st.metric("⚠️ Drawdown Máx", round(drawdown,4))

except Exception as e:
    st.error(f"Erro ao carregar sistema: {e}")
