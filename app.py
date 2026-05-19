from engine import ranking, probabilidade, regime, risco_carteira, pesos_otimos

st.metric("Regime IA", regime)
st.metric("Risco Carteira", round(risco_carteira,4))

st.success(f"🔥 COMPRAR: {ranking.index[0]}")

pesos_df = pd.DataFrame({
    "Ativo": ranking.index,
    "Peso": pesos_otimos
})

st.dataframe(pesos_df)
