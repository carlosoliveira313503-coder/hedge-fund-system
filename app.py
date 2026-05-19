import streamlit as st

st.set_page_config(layout="wide")

st.title("🏦 Hedge Fund RL System")

try:
    from engine import (
        ranking,
        ranking_rl,
        melhor_ativo_rl,
        regime,
        probabilidade,
        perf,
        bench,
        volatilidade,
        drawdown
    )

    # =============================
    # PROTEÇÃO INICIAL
    # =============================
    if ranking is None or ranking.empty:
        st.warning("Carregando dados...")
        st.stop()

    # =============================
    # KPIs
    # =============================
    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Regime", str(regime).upper())
    col2.metric("🔥 Melhor Ativo IA", str(ranking.index[0]))
    col3.metric("🎯 Probabilidade", f"{probabilidade():.2%}")

    # =============================
    # DECISÃO
    # =============================
    st.success(f"🚀 AÇÃO RECOMENDADA: COMPRAR {melhor_ativo_rl}")

    # =============================
    # TABS
    # =============================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Ranking IA",
        "🤖 Portfólio RL",
        "💰 Performance",
        "📉 Risco"
    ])

    # ------------------------------
    # TAB 1 - Ranking
    # ------------------------------
    with tab1:
        st.dataframe(ranking, use_container_width=True)

    # ------------------------------
    # TAB 2 - RL
    # ------------------------------
    with tab2:
        st.dataframe(ranking_rl, use_container_width=True)

        try:
            st.bar_chart(ranking_rl.set_index("Ativo"))
        except:
            st.info("Gráfico indisponível")

    # ------------------------------
    # TAB 3 - Performance
    # ------------------------------
    with tab3:

        if perf is None or perf.empty:
            st.warning("Sem histórico ainda")
        else:

            st.subheader("💰 Evolução do Patrimônio")
            st.line_chart(perf["Patrimonio"])

            if isinstance(bench, list) and len(bench) > 0:
                try:
                    import pandas as pd

                    df_comp = pd.DataFrame({
                        "Sistema": perf["Patrimonio"],
                        "Benchmark": bench
                    })

                    st.subheader("📊 Comparação com Benchmark")
                    st.line_chart(df_comp)
                except:
                    st.warning("Benchmark indisponível")

            st.subheader("📋 Histórico")
            st.dataframe(perf)

    # ------------------------------
    # TAB 4 - RISCO
    # ------------------------------
    with tab4:

        colr1, colr2 = st.columns(2)

        colr1.metric("📉 Volatilidade", round(float(volatilidade),4))
        colr2.metric("⚠️ Drawdown Máx", round(float(drawdown),4))

except Exception as e:
    st.error(f"Erro ao carregar sistema: {e}")
