import streamlit as st
from engine import ranking, probabilidade

st.set_page_config(layout="wide")
st.title("🏦 Hedge Fund System")

col1, col2, col3 = st.columns(3)
col1.metric("Melhor Ativo", ranking.index[0])
col2.metric("Score", round(ranking.iloc[0]['Score'],2))
col3.metric("Probabilidade 800k", f"{probabilidade():.2%}")

st.subheader("Top 5 ativos")
st.dataframe(ranking.head(5))
