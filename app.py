import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🏦 Hedge Fund RL System")

try:
    from engine import *

    if ranking.empty:
        st.stop()

    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Regime", regime.upper())
    col2.metric("🔥 Melhor Ativo IA", ranking.index[0])
    col3.metric("🎯 Probabilidade", f"{probabilidade():.2%}")

    st.success(f"🚀 AÇÃO RECOMENDADA: COMPRAR {melhor_ativo_rl}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Ranking IA",
        "🤖 Portfólio RL",
        "💰 Performance",
        "📉 Risco",
        "🧠 Estratégia"
    ])

    with tab1:
        st.dataframe(ranking)

    with tab2:
        st.dataframe(ranking_rl)
        st.bar_chart(ranking_rl.set_index("Ativo"))

    with tab3:
        if not perf.empty:
            st.line_chart(perf["Patrimonio"])

            if len(bench) > 0:
                df_comp = pd.DataFrame({
                    "Sistema": perf["Patrimonio"],
                    "Benchmark": bench
                })
                st.line_chart(df_comp)

            st.dataframe(perf)

    with tab4:
        st.metric("📉 Volatilidade", round(volatilidade,4))
        st.metric("⚠️ Drawdown", round(drawdown,4))

    with tab5:
        st.subheader("🧠 Estratégia Operacional")

        top3 = ranking.index[:3]
        pesos = [0.40, 0.35, 0.25]

        carteira = []
        for ativo, peso in zip(top3, pesos):
            carteira.append({
                "Ativo": ativo,
                "Peso": f"{int(peso*100)}%"
            })

        st.dataframe(pd.DataFrame(carteira))

        st.success("✅ Comprar sempre Top 3")

        st.info("""
📊 Pesos: 40% / 35% / 25%  
📅 Rebalancear mensal  
💰 Dividendos → Top 1  
📅 Aporte anual → 50/30/20  
🔴 Vender se sair do Top 3
        """)

except Exception as e:
    st.error(f"Erro: {e}")
