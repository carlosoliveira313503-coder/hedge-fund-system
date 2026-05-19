import streamlit as st

st.set_page_config(layout="wide")

st.title("🏦 Hedge Fund System")

try:
    from engine import ranking, probabilidade

    col1, col2, col3 = st.columns(3)

    col1.metric("Melhor Ativo", ranking.index[0])
    col2.metric("Score", round(ranking.iloc[0]["Score"], 3))
    col3.metric("Probabilidade 800k", f"{probabilidade():.2%}")

    st.subheader("Top Ativos")
    st.dataframe(ranking)

except Exception as e:
    st.error(f"Erro ao carregar sistema: {e}")
