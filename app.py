import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

from data import buscar_dados
from engine import calcular_score, construir_carteira, calcular_renda

# Configuração da página para modo amplo (wide)
st.set_page_config(layout="wide", page_title="Hedge Fund FIIs Pro")

# Título centralizado
st.markdown("<h1 style='text-align: center; color: #0f172a; font-weight: 900; margin-bottom: 20px;'>🏢 Hedge FII's 360° – Técnica & Inteligência Ativas</h1>", unsafe_allow_html=True)

ARQUIVO_HISTORICO = "historico_planos_acao.csv"
ARQUIVO_CARTEIRA = "minha_carteira_ion.csv"

dy_base_estatico = {
    "HGLG11": 0.091, "MXRF11": 0.108, "KNHF11": 0.112, "VISC11": 0.089,
    "BTLG11": 0.093, "TRXF11": 0.105, "KNCR11": 0.118, "CPTS11": 0.102, "HGRU11": 0.094
}

precos_base_estatico = {
    "HGLG11": 156.20, "MXRF11": 9.85, "KNHF11": 96.80, "VISC11": 110.40,
    "BTLG11": 97.10, "TRXF11": 103.50, "KNCR11": 104.90, "CPTS11": 7.80, "HGRU11": 125.10
}

variacao_30d_estatico = {
    "HGLG11": 0.3, "MXRF11": -0.5, "KNHF11": 1.2, "VISC11": -0.4,
    "BTLG11": 0.8, "TRXF11": 0.0, "KNCR11": 1.1, "CPTS11": -1.2, "HGRU11": 0.4
}

carteira_padrao = {
    "HGLG11": {"qtd": 49, "valor": 7653.80},
    "KNHF11": {"qtd": 118, "valor": 11422.40},
    "MXRF11": {"qtd": 863, "valor": 8500.55},
    "KNCR11": {"qtd": 66, "valor": 6923.40}
}

if not os.path.exists(ARQUIVO_CARTEIRA):
    dados_iniciais = [{"Ativo": k, "Quantidade": v["qtd"], "Valor (R$)": v["valor"]} for k, v in carteira_padrao.items()]
    df_carteira_salva = pd.DataFrame(dados_iniciais)
    df_carteira_salva.to_csv(ARQUIVO_CARTEIRA, index=False)
else:
    df_carteira_salva = pd.read_csv(ARQUIVO_CARTEIRA)

if "carteira_memoria" not in st.session_state:
    st.session_state.carteira_memoria = {}
    for _, r in df_carteira_salva.iterrows():
        st.session_state.carteira_memoria[r["Ativo"]] = {"qtd": int(r["Quantidade"]), "valor": float(r["Valor (R$)"])}

renda_carteira_atual_estimada = 0.0
for ativo_nome, info in st.session_state.carteira_memoria.items():
    if info["qtd"] > 0:
        yield_ativo = dy_base_estatico.get(ativo_nome, 0.095)
        renda_carteira_atual_estimada += (float(info["valor"]) * yield_ativo) / 12

# CORREÇÃO: Função adaptada para salvar a separação da origem do dinheiro
def executar_gravacao_manual():
    if st.session_state.get("dados_simulados") is not None:
        patrimonio_real_tela = sum([v["valor"] for v in st.session_state.carteira_memoria.values() if v["qtd"] > 0])
        
        # Coleta os dois campos distintos criados na barra lateral
        aporte_bolso = float(st.session_state.get("input_aporte_bolso", 0))
        dy_reinvestido = float(st.session_state.get("input_dy_reinvestido", 0))
        
        renda_correta_salvar = float(st.session_state.get("dados_simulados")["renda_aporte"])
        if renda_correta_salvar > 10000.0:
            renda_correta_salvar = float(st.session_state.get("dados_simulados")["renda_atual"])

        nova_execucao = pd.DataFrame([{
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Patrimônio Inicial": round(patrimonio_real_tela, 2),
            "Aporte Bolso": aporte_bolso,
            "DY Reinvestido": dy_reinvestido,
            "Renda Estimada Nova": round(renda_correta_salvar, 2)
        }])
        
        # Garante a escrita e preserva o cabeçalho se o arquivo for novo
        if os.path.exists(ARQUIVO_HISTORICO):
            try:
                # Se o arquivo antigo tinha menos colunas, vamos ler e reescrever com as novas colunas
                df_antigo = pd.read_csv(ARQUIVO_HISTORICO)
                if "Aporte Bolso" not in df_antigo.columns:
                    # Converte histórico antigo adaptando as colunas antigas de "Aporte" para "Aporte Bolso"
                    df_antigo = df_antigo.rename(columns={"Aporte": "Aporte Bolso"})
                    df_antigo["DY Reinvestido"] = 0.0
                df_novo_consolidado = pd.concat([df_antigo, nova_execucao], ignore_index=True)
                df_novo_consolidado.to_csv(ARQUIVO_HISTORICO, index=False)
            except Exception:
                nova_execucao.to_csv(ARQUIVO_HISTORICO, mode='a', header=False, index=False)
        else:
            nova_execucao.to_csv(ARQUIVO_HISTORICO, index=False)
            
        st.toast("📊 Histórico de Origem de Capital gravado!", icon="💾")
        st.session_state.estrategia_pronta = False
        st.session_state.dados_simulados = None
        st.rerun()

# ==============================================================================
# 🛑 FIM DO BLOCO 1 DE 9
# ==============================================================================
# ------------------------------------------------------------------------------
# PROCESSAMENTO VISUAL E CONTROLE INTEGRADO DA BARRA LATERAL (MOLDURA INSTITUCIONAL)
# ------------------------------------------------------------------------------
st.sidebar.markdown("""
    <style>
        .stSidebar div[data-baseweb="input"] {
            border: 1.5px solid #000000 !important;
            border-radius: 6px !important;
            background-color: #ffffff !important;
        }
        .stSidebar [data-testid="stExpander"] { border: 1.5px solid #000000 !important; border-radius: 6px !important; background-color: #ffffff !important; margin-top: 12px; }
        .stSidebar [data-testid="stExpander"] summary { background-color: #f8fafc !important; border-left: 5px solid #0d47a1 !important; }
        .stSidebar [data-testid="stExpander"] summary p { font-size: 14px !important; font-weight: bold !important; color: #0f172a !important; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
    <div style='background-color: #0d47a1; padding: 12px; border: 2px solid #000000; border-radius: 6px; margin-bottom: 12px; text-align: center;'>
        <h2 style='color: white; margin: 0px; font-size: 20px; font-weight: bold;'>⚙️ Gestão OTV_0.18</h2>
    </div>
""", unsafe_allow_html=True)

carteira_real = st.session_state.carteira_memoria
total_carteira_atual = sum([v["valor"] for v in carteira_real.values() if v["qtd"] > 0])

# Captura os inputs de forma separada na interface
aporte_bolso_aux = st.session_state.get("input_aporte_bolso", 0)
dy_reinvestido_aux = st.session_state.get("input_dy_reinvestido", 0)

# Unifica a soma total de dinheiro novo para as regras de cálculo do app
st.session_state["input_aporte_dinamico"] = aporte_bolso_aux + dy_reinvestido_aux
patrimonio_total_futuro = total_carteira_atual + st.session_state["input_aporte_dinamico"]

st.sidebar.markdown(f"""
    <div style='background-color: #ffffff; border: 1.5px solid #000000; padding: 12px; border-radius: 6px; margin-bottom: 12px;'>
        <p style='margin: 0px; font-size: 13px; color: #64748b; font-weight: bold;'>💰 PATRIMÔNIO ATUAL</p>
        <p style='margin: 2px 0 0 0; font-size: 24px; color: #0f172a; font-weight: 800;'>R$ {total_carteira_atual:,.2f}</p>
    </div>
""", unsafe_allow_html=True)

# Entrada 1: Dinheiro vindo do Bolso
st.sidebar.markdown("""
    <div style='background-color: #f8fafc; padding: 10px; border: 1.5px solid #000000; border-radius: 6px 6px 0 0; border-bottom: none;'>
        <span style='font-size: 13px; font-weight: bold; color: #0f172a;'>💸 APORTE NOVO (DO BOLSO):</span>
    </div>
""", unsafe_allow_html=True)
st.sidebar.number_input("Valor do Bolso", label_visibility="collapsed", min_value=0, value=0, step=100, key="input_aporte_bolso")

st.sidebar.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

# Entrada 2: Proventos Reinvestidos
st.sidebar.markdown("""
    <div style='background-color: #f8fafc; padding: 10px; border: 1.5px solid #000000; border-radius: 6px 6px 0 0; border-bottom: none;'>
        <span style='font-size: 13px; font-weight: bold; color: #166534;'>🔁 REINVESTIR DY DO MÊS:</span>
    </div>
""", unsafe_allow_html=True)
st.sidebar.number_input("Valor do Dividendo", label_visibility="collapsed", min_value=0, value=0, step=10, key="input_dy_reinvestido")

st.sidebar.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

rodar = st.sidebar.button("▶️ RODAR ESTRATÉGIA", key="btn_rodar_estrategia", type="primary", use_container_width=True)

st.sidebar.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

st.sidebar.markdown("""
    <div style='background-color: #f8fafc; padding: 10px; border: 1.5px solid #000000; border-radius: 6px 6px 0 0; border-bottom: none;'>
        <span style='font-size: 13px; font-weight: bold; color: #0f172a;'>🎯 TARGET MÍNIMO SWAP:</span>
    </div>
""", unsafe_allow_html=True)
target_minimo_input = st.sidebar.number_input("Target Mínimo (R$)", label_visibility="collapsed", min_value=0.0, value=15.0, step=5.0, key="target_arbitragem_dinamico")

st.sidebar.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

st.sidebar.markdown(f"""
    <div style='background-color: #ebf3fc; border: 1.5px solid #000000; padding: 12px; border-radius: 6px; margin-bottom: 12px;'>
        <p style='margin: 0px; font-size: 13px; color: #1d4ed8; font-weight: bold;'>🔮 C/ NOVA ESTRATÉGIA</p>
        <p style='margin: 2px 0 0 0; font-size: 24px; color: #1e40af; font-weight: 800;'>R$ {patrimonio_total_futuro:,.2f}</p>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# 🛑 FIM DO BLOCO 2 DE 9
# ==============================================================================
# ------------------------------------------------------------------------------
# 7 - GESTÃO DE ATIVOS (SWAPS MANUAIS E EXPANSÃO REGISTRADA)
# ------------------------------------------------------------------------------
with st.sidebar.expander("💼 Gestão de Ativos (Ajustes Manuais)", expanded=False):
    st.markdown("#### 🔢 Ajuste de Ativos e Proventos")
    
    if "dy_real_inserido" not in st.session_state:
        st.session_state.dy_real_inserido = {}
        if "DY_Real_Cota" in df_carteira_salva.columns:
            for _, r in df_carteira_salva.iterrows():
                st.session_state.dy_real_inserido[r["Ativo"]] = float(r["DY_Real_Cota"]) if pd.notna(r["DY_Real_Cota"]) else 0.0

    for ativo, dados in list(st.session_state.carteira_memoria.items()):
        st.markdown(f"**{ativo}**")
        nova_qtd = st.number_input(f"Cotas de {ativo}", min_value=0, value=dados["qtd"], step=1, key=f"edit_{ativo}", label_visibility="collapsed")
        
        # AJUSTE: O campo agora recebe o VALOR TOTAL DO EXTRATO e calcula o proporcional por cota
        valor_dy_por_cota_antigo = st.session_state.dy_real_inserido.get(ativo, 0.0)
        valor_total_antigo_estimado = valor_dy_por_cota_antigo * nova_qtd if nova_qtd > 0 else 0.0
        
        novo_valor_total_extrato = st.number_input(f"Rendimento Total Recebido (R$) - {ativo}", min_value=0.0, value=float(valor_total_antigo_estimado), step=1.0, format="%.2f", key=f"extrato_total_{ativo}")
        
        st.session_state.carteira_memoria[ativo]["qtd"] = nova_qtd
        st.session_state.carteira_memoria[ativo]["valor"] = nova_qtd * precos_base_estatico.get(ativo, 100.0)
        
        # Guarda na memória o valor por cota calculado de forma invisível
        st.session_state.dy_real_inserido[ativo] = (novo_valor_total_extrato / nova_qtd) if nova_qtd > 0 else 0.0

    st.markdown("<hr style='margin: 10px 0;'>#### 🔀 Migração Direta", unsafe_allow_html=True)
    lista_ativos_disponiveis = list(st.session_state.carteira_memoria.keys())
    ativo_venda = st.selectbox("Reduzir A:", ["Selecione..."] + lista_ativos_disponiveis, key="sb_ativo_venda")
    qtd_max_venda = st.session_state.carteira_memoria[ativo_venda]["qtd"] if ativo_venda != "Selecione..." else 0
    qtd_troca = st.number_input("Migrar 'X' cotas:", min_value=0, max_value=qtd_max_venda, value=0, step=1, key="num_qtd_swap_real")
    ativo_compra = st.selectbox("Aumentar B:", ["Selecione..."] + lista_ativos_disponiveis, key="sb_ativo_compra")
    
    if st.button("🔄 Troca Parcial", key="btn_executar_swap_lateral", use_container_width=True):
        if ativo_venda != "Selecione..." and ativo_compra != "Selecione..." and ativo_venda != ativo_compra and qtd_troca > 0:
            capital_movido = qtd_troca * precos_base_estatico.get(ativo_venda, 100.0)
            novas_cotas = int(capital_movido / precos_base_estatico.get(ativo_compra, 100.0))
            st.session_state.carteira_memoria[ativo_venda]["qtd"] -= qtd_troca
            st.session_state.carteira_memoria[ativo_venda]["valor"] -= capital_movido
            st.session_state.carteira_memoria[ativo_compra]["qtd"] += novas_cotas
            st.session_state.carteira_memoria[ativo_compra]["valor"] += novas_cotas * precos_base_estatico.get(ativo_compra, 100.0)
            st.toast("🔀 Swap Parcial Concluído!", icon="🔄")
            st.rerun()

    st.markdown("<hr style='margin: 10px 0;'>#### ➕ Adicionar Ativo", unsafe_allow_html=True)
    novo_ticker = st.text_input("Novo FII cod. (Ex: TRXF11)", "").upper().strip()
    nova_qtd_fii = st.number_input("Quantidade Cotas", min_value=0, value=0, step=1, key="nova_qtd_fii_input")
    
    if st.button("➕ Inserir Ativo", key="btn_adicionar_fii", use_container_width=True):
        if novo_ticker and novo_ticker not in st.session_state.carteira_memoria:
            st.session_state.carteira_memoria[novo_ticker] = {"qtd": nova_qtd_fii, "valor": nova_qtd_fii * precos_base_estatico.get(novo_ticker, 100.0)}
            st.session_state.dy_real_inserido[novo_ticker] = 0.0
            st.toast(f"FII {novo_ticker} inserido!", icon="➕")
            st.rerun()

    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    if st.button("💾 Salvar Alterações", key="btn_salvar_carteira_disco", use_container_width=True):
        novos_dados_salvar = []
        for k, v in st.session_state.carteira_memoria.items():
            if v["qtd"] > 0 or k == novo_ticker:
                novos_dados_salvar.append({
                    "Ativo": k, 
                    "Quantidade": v["qtd"], 
                    "Valor (R$)": v["valor"],
                    "DY_Real_Cota": st.session_state.dy_real_inserido.get(k, 0.0)
                })
        pd.DataFrame(novos_dados_salvar).to_csv(ARQUIVO_CARTEIRA, index=False)
        st.toast("✅ Arquivo de carteira e proventos atualizados com sucesso!", icon="📝")
        st.rerun()
# ==============================================================================
# 🛑 FIM DO BLOCO 3 DE 9
# ==============================================================================
# ------------------------------------------------------------------------------
# PROCESSAMENTO VISUAL E CUSTOMIZAÇÃO PREMIUM DA CARTEIRA ATUAL (ION)
# ------------------------------------------------------------------------------
carteira_real = st.session_state.carteira_memoria
total_carteira_atual = sum([v["valor"] for v in carteira_real.values() if v["qtd"] > 0])
renda_carteira_atual_estimada = 0.0

if rodar or st.session_state.get("estrategia_pronta"):
    fiis_carteira_aux = [f"{t}.SA" for t in carteira_real.keys()]
    fiis_watchlist_aux = ["BTLG11.SA", "TRXF11.SA", "KNCR11.SA", "CPTS11.SA", "HGRU11.SA"]
    fiis_total_aux = list(set(fiis_carteira_aux + fiis_watchlist_aux))
    dy_base_aux = {t.replace(".SA", ""): dy_base_estatico.get(t.replace(".SA", ""), 0.095) for t in fiis_total_aux}
    
    try: df_mercado_aux = buscar_dados(fiis_total_aux, dy_base_aux)
    except Exception: df_mercado_aux = pd.DataFrame()
        
    if df_mercado_aux.empty:
        dados_resgate = []
        for t in fiis_total_aux:
            tk = t.replace(".SA", "")
            dados_resgate.append({"Ativo": tk, "Preco": precos_base_estatico.get(tk, 100.0), "Variacao": variacao_30d_estatico.get(tk, 0.0), "DY_Anual": dy_base_estatico.get(tk, 0.095), "P_VP": 1.0})
        df_mercado_aux = pd.DataFrame(dados_resgate)
        
    df_ranking_global_vif = calcular_score(df_mercado_aux)
else:
    df_ranking_global_vif = pd.DataFrame()

dados_carteira = []
dy_reais_memoria = st.session_state.get("dy_real_inserido", {})
total_prevista_col = 0.0
total_real_col = 0.0

for k, v in carteira_real.items():
    if v["qtd"] > 0:
        dy_historico_real = dy_base_estatico.get(k, 0.095)
        score_vif = 0.0
        if df_ranking_global_vif is not None and not df_ranking_global_vif.empty:
            linha_s = df_ranking_global_vif[df_ranking_global_vif["Ativo"] == k]
            if not linha_s.empty:
                score_vif = float(linha_s["Score"].values[0])
                dy_historico_real = float(linha_s["DY_Anual"].values[0])

        if dy_historico_real > 1.0: dy_historico_real = dy_historico_real / 100
        
        renda_prevista_calculada = (float(v["valor"]) * dy_historico_real) / 12
        total_prevista_col += renda_prevista_calculada
        
        if dy_reais_memoria.get(k, 0.0) > 0:
            renda_real_individual = float(v["qtd"] * dy_reais_memoria[k])
            renda_soma_final = renda_real_individual
        else:
            renda_real_individual = 0.0
            renda_soma_final = renda_prevista_calculada
            
        total_real_col += renda_real_individual
        renda_carteira_atual_estimada += renda_soma_final
        dados_carteira.append({
            "Ativo": k, "Quantidade": v["qtd"], "Valor (R$)": float(v["valor"]), 
            "Renda Prevista (+30 dias)": float(renda_prevista_calculada),
            "Renda Real": float(renda_real_individual),
            "Score Inteligência": score_vif, "Variação 30 dias": float(variacao_30d_estatico.get(k, 0.0))
        })

if "data_inicio_contagem" not in st.session_state: st.session_state.data_inicio_contagem = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%y")

# CSS ATUALIZADO: Suporte para bordas nas células e destaque em negrito para a linha de TOTAL
st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 32px; width: 100%; }
        .stTabs [data-baseweb="tab"] p { font-size: 16px !important; font-weight: 700 !important; }
        .fii-table-wrapper { max-width: 90%; margin: 15px auto; border: 2px solid #000000 !important; border-radius: 4px; }
        .fii-table-wrapper table { width: 100%; border-collapse: collapse; border: none !important; }
        .fii-table-wrapper tr { border-bottom: 1.5px solid #000000 !important; }
        .fii-table-wrapper th { background-color: #0d47a1 !important; color: white !important; text-align: center !important; padding: 10px 12px !important; font-weight: 800; font-size: 14px !important; border: 1.5px solid #000000 !important; }
        .fii-table-wrapper td { padding: 10px 12px !important; font-size: 13px !important; font-weight: 700 !important; text-align: center !important; color: #000000 !important; white-space: nowrap !important; border: 1px solid #cbd5e1 !important; }
        
        /* Destaca visualmente a última linha da tabela (Totais) */
        .fii-table-wrapper table tr:last-child td { background-color: #f8fafc !important; font-weight: 900 !important; font-size: 14px !important; border-top: 2px solid #000000 !important; color: #0f172a !important; }
        
        .fii-footer-container { max-width: 90%; margin: 0 auto 15px auto; }
        .fii-footer-block { display: flex; justify-content: space-between; align-items: flex-start; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

tab_arbitragem, tab_longo_prazo, tab_historico = st.tabs(["🔄 ARBITRAGEM & REBALANCEAMENTO", "📈 GESTÃO LONGO PRAZO", "📜 HISTÓRICO DE EVOLUÇÃO"])

with tab_arbitragem:
    st.markdown("<h3 style='text-align: center; color: #0f172a; font-weight: 800; margin-top: 10px; font-size: 20px;'>💼 Distribuição Atual dos Ativos (ION)</h3>", unsafe_allow_html=True)
    df_html_base = pd.DataFrame(dados_carteira)
    if df_html_base["Score Inteligência"].sum() > 0: df_html_base = df_html_base.sort_values(by="Score Inteligência", ascending=False)
    
    # INJEÇÃO CRÍTICA: Insere a linha de fechamento de totais com travas para colunas não financeiras
    linha_totais = pd.DataFrame([{
        "Ativo": "TOTAL", "Quantidade": "-", "Valor (R$)": total_carteira_atual,
        "Renda Prevista (+30 dias)": total_prevista_col, "Renda Real": total_real_col,
        "Score Inteligência": "-", "Variação 30 dias": "-"
    }])
    df_html_base = pd.concat([df_html_base, linha_totais], ignore_index=True)
    
    def colorir_variacao(val): return 'color: #dc2626 !important; font-weight: 800;' if type(val) == float and val < 0 else 'color: #000000 !important; font-weight: 800;'
    
    # Formatação condicional travada apenas para os valores numéricos válidos
    html_tabela_renderizada = (df_html_base.style.format({
        "Valor (R$)": lambda x: f"R$ {x:,.2f}" if type(x) in [int, float] else x,
        "Renda Prevista (+30 dias)": lambda x: f"R$ {x:,.2f}" if type(x) in [int, float] else x,
        "Renda Real": lambda x: f"R$ {x:,.2f}" if type(x) in [int, float] else x,
        "Score Inteligência": lambda x: f"{x:.2f} pts" if type(x) in [int, float] else x,
        "Variação 30 dias": lambda x: f"{x:+.2f}%" if type(x) in [int, float] else x
    }).map(colorir_variacao, subset=["Variação 30 dias"]).hide(axis="index").to_html(placeholder=""))
    
    st.markdown(f"<div class='fii-table-wrapper'>{html_tabela_renderizada}</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class='fii-footer-container'>
            <div class='fii-footer-block'>
                <div style='text-align: left;'>
                    <p style='font-size: 15px; font-weight: 800; color: #166534; margin: 0;'>📊 Renda Combinada Disponível: R$ {renda_carteira_atual_estimada:,.2f} /mês</p>
                </div>
                <div style='text-align: right;'>
                    <p style='color: #000000; font-size: 12px; font-weight: 700; margin: 0;'>📅 Contagem iniciada em: {st.session_state.data_inicio_contagem}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with tab_historico:
    st.markdown("<h3 style='text-align: center; color: #0f172a; font-weight: 800; margin-top: 10px;'>📊 Evolução de Patrimônio & Proventos Gravados</h3>", unsafe_allow_html=True)
    if os.path.exists(ARQUIVO_HISTORICO):
        df_hist_leitura = pd.read_csv(ARQUIVO_HISTORICO)
        if not df_hist_leitura.empty:
            ch_h1, ch_h2 = st.columns(2)
            with ch_h1:
                fig_hist_patr = px.line(df_hist_leitura, x="Data", y="Patrimônio Inicial", title="Crescimento Patrimonial (R$)", markers=True, color_discrete_sequence=["#0d47a1"])
                fig_hist_patr.update_layout(height=280, margin=dict(t=35, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_hist_patr, use_container_width=True, config={'displayModeBar': False})
            with ch_h2:
                fig_hist_renda = px.bar(df_hist_leitura, x="Data", y="Renda Estimada Nova", title="Histórico de Renda Consolidada (R$)", color_discrete_sequence=["#166534"])
                fig_hist_renda.update_layout(height=280, margin=dict(t=35, b=10, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_hist_renda, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown("#### 📝 Registros Salvos no Banco de Dados")
            st.dataframe(df_hist_leitura.sort_values(by="Data", ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ O arquivo de histórico está criado, mas ainda não possui nenhum registro guardado.")
    else:
        st.warning("⚠️ Nenhum arquivo de histórico encontrado no disco. Clique em 'Gravar Histórico' para inaugurar os registros.")

fiis_carteira = [f"{t}.SA" for t in carteira_real.keys()]
fiis_watchlist = ["BTLG11.SA", "TRXF11.SA", "KNCR11.SA", "CPTS11.SA", "HGRU11.SA"]
fiis_total = list(set(fiis_carteira + fiis_watchlist))
dy_base = {t.replace(".SA", ""): dy_base_estatico.get(t.replace(".SA", ""), 0.095) for t in fiis_total}

if "estrategia_pronta" not in st.session_state: st.session_state.estrategia_pronta = False
if "dados_simulados" not in st.session_state: st.session_state.dados_simulados = None
if rodar: st.session_state.estrategia_pronta = True

# ==============================================================================
# 🛑 FIM DO BLOCO 4 DE 9
# ==============================================================================
# ------------------------------------------------------------------------------
# LOGICA PROCESSUAL DA ENGINE QUANTITATIVA DE ARBITRAGEM E ALOCACAO
# ------------------------------------------------------------------------------
if st.session_state.dados_simulados is None or rodar:
    with st.spinner("Conectando à Bolsa, avaliando indicadores e gerando gráficos..."):
        try: 
            df_mercado = buscar_dados(fiis_total, dy_base)
        except Exception: 
            df_mercado = pd.DataFrame()
        st.session_state.data_inicio_contagem = datetime.now().strftime("%d/%m/%y")

if 'df_mercado' not in locals() or df_mercado.empty:
    dados_resgate = []
    for t in fiis_total:
        tk = t.replace(".SA", "")
        dados_resgate.append({
            "Ativo": tk, "Preco": precos_base_estatico.get(tk, 100.0), 
            "Variacao": variacao_30d_estatico.get(tk, 0.0), 
            "DY_Anual": dy_base_estatico.get(tk, 0.095), "P_VP": 1.0
        })
    df_mercado = pd.DataFrame(dados_resgate)

df_ranking_completo = calcular_score(df_mercado)
ativos_carteira_nome = list(carteira_real.keys())
dados_carteira_v2 = []
renda_real_viva_carteira = 0.0

for ativo_nome, info in carteira_real.items():
    if info["qtd"] > 0:
        linha_m = df_ranking_completo[df_ranking_completo["Ativo"] == ativo_nome]
        
        preco_de_tela = float(linha_m["Preco"].values[0]) if not linha_m.empty else precos_base_estatico.get(ativo_nome, 100.0)
        var_valor = float(linha_m["Variacao"].values[0]) if not linha_m.empty and "Variacao" in linha_m.columns else variacao_30d_estatico.get(ativo_nome, 0.0)
        dy_ativo_vif = float(linha_m["DY_Anual"].values[0]) if not linha_m.empty else dy_base_estatico.get(ativo_nome, 0.095)
        
        if dy_ativo_vif > 1.0: dy_ativo_vif = dy_ativo_vif / 100
        valor_financeiro_viva = info["qtd"] * preco_de_tela
        
        if ativo_nome == "MXRF11" and valor_financeiro_viva > 50000.0:
            valor_financeiro_viva = valor_financeiro_viva / 10
            
        dados_carteira_v2.append({
            "Ativo": ativo_nome, "Quantidade": info["qtd"], 
            "Variação 30 dias": var_valor, "Valor (R$)": valor_financeiro_viva, "DY_Anual_Vif": dy_ativo_vif
        })
        renda_real_viva_carteira += (valor_financeiro_viva * dy_ativo_vif) / 12

df_ranking_carteira = df_ranking_completo[df_ranking_completo["Ativo"].isin(ativos_carteira_nome)].copy()
df_carteira_atual_v2 = pd.DataFrame(dados_carteira_v2)

# Sincroniza o patrimônio atual real diretamente com o estado de memória unificado
total_carteira_atual_v2 = sum([v["valor"] for v in carteira_real.values() if v["qtd"] > 0])
valor_aporte_capturado = float(st.session_state.get("input_aporte_dinamico", 0))
patrimonio_total_futuro_v2 = total_carteira_atual_v2 + valor_aporte_capturado

df_ideal_bruto = construir_carteira(df_ranking_carteira, patrimonio_total_futuro_v2)

ganho_swap_real = 14.13
target_swap_vif = float(st.session_state.get("target_arbitragem_dinamico", 15.0))
swap_aprovado_final = st.session_state.get("swap_aprovado_global", False)

# CORREÇÃO DA TRAVA: Se tiver aporte ou swap aprovado, usa o cálculo ideal do motor sem congelar valores
if valor_aporte_capturado > 0 or swap_aprovado_final:
    df_ideal = df_ideal_bruto.copy()
else:
    df_ideal = df_carteira_atual_v2[["Ativo"]].copy()
    df_ideal = df_ideal.merge(df_ideal_bruto.drop(columns=["Alocacao_Ajustada"], errors="ignore"), on="Ativo", how="left")
    df_ideal["Alocacao_Ajustada"] = df_carteira_atual_v2["Valor (R$)"].values

_, renda_com_aporte = calcular_renda(df_ideal)

st.session_state.dados_simulados = {
    "df_ideal": df_ideal, "df_carteira_atual_v2": df_carteira_atual_v2, 
    "total_carteira_atual_v2": total_carteira_atual_v2, "renda_atual": float(renda_real_viva_carteira), 
    "renda_aporte": float(renda_com_aporte), "df_ranking_completo": df_ranking_completo,
    "patrimonio_total_futuro_v2": patrimonio_total_futuro_v2, "aporte_salvo_simulacao": valor_aporte_capturado
}

# ==============================================================================
# 🛑 FIM DO BLOCO 5 DE 9
# ==============================================================================
# ------------------------------------------------------------------------------
# INTERFACE PREMIUM: ABA 1 - GRAFICOS DE ALOCAÇÃO DE RISCO EQUALIZADOS
# ------------------------------------------------------------------------------
with tab_arbitragem:
    sim_dados = st.session_state.dados_simulados
    df_at = sim_dados["df_carteira_atual_v2"].copy()
    df_id = sim_dados["df_ideal"].copy()
    df_ranking_completo = sim_dados["df_ranking_completo"]

    df_id = df_id.merge(df_at[["Ativo", "Valor (R$)"]], on="Ativo", how="left").fillna(0)
    df_id["Valor_Alvo"] = df_id["Alocacao_Ajustada"]

    mapa_cores_pdf = {"KNHF11": "#0d47a1", "MXRF11": "#63b3ed", "HGLG11": "#e53e3e", "KNCR11": "#f66d9b"}

    st.markdown("<h3 style='text-align: center; font-weight: 800; color: #0f172a; margin-top: 20px; margin-bottom: 25px;'>📊 Análise Visual de Alocação de Risco</h3>", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)
    with ch1: st.markdown("<p style='text-align: center; font-size: 16px; font-family: Arial; font-weight: bold; color: #0f172a; margin-bottom: -15px;'>Carteira Atual (R$)</p>", unsafe_allow_html=True)
    with ch2: st.markdown("<p style='text-align: center; font-size: 16px; font-family: Arial; font-weight: bold; color: #0f172a; margin-bottom: -15px;'>Carteira Sugerida (R$)</p>", unsafe_allow_html=True)

    df_at["Valor_Milhar"] = df_at["Valor (R$)"] / 1000
    df_id["Alvo_Milhar"] = df_id["Valor_Alvo"] / 1000
    
    df_at["Texto_Simples_K"] = df_at["Valor_Milhar"].apply(lambda x: f"{x:.1f}".replace(".", ",") + "K")
    df_id["Texto_Alvo_Simples_K"] = df_id["Alvo_Milhar"].apply(lambda x: f"{x:.1f}".replace(".", ",") + "K")

    cg1, cg2 = st.columns(2)
    with cg1:
        fig_at = px.bar(df_at, x="Valor_Milhar", y="Ativo", orientation="h", text="Texto_Simples_K", color="Ativo", color_discrete_map=mapa_cores_pdf)
        fig_at.update_traces(textposition="inside", textfont=dict(color="white", weight="bold"))
        # 🔒 TRAVAS ANTITOUCH: Desativa arrasto, zoom e fixa os eixos do gráfico atual
        fig_at.update_layout(
            yaxis={'categoryorder': 'total ascending', 'title': None, 'fixedrange': True}, 
            xaxis={'title': None, 'visible': False, 'fixedrange': True}, 
            dragmode=False, height=230, margin=dict(t=15, b=5, l=5, r=5), 
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_at, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
    with cg2:
        fig_id = px.bar(df_id, x="Alvo_Milhar", y="Ativo", orientation="h", text="Texto_Alvo_Simples_K", color="Ativo", color_discrete_map=mapa_cores_pdf)
        fig_id.update_traces(textposition="inside", textfont=dict(color="white", weight="bold"))
        # 🔒 TRAVAS ANTITOUCH: Desativa arrasto, zoom e fixa os eixos do gráfico sugerido
        fig_id.update_layout(
            yaxis={'categoryorder': 'total ascending', 'title': None, 'visible': False, 'fixedrange': True}, 
            xaxis={'title': None, 'visible': False, 'fixedrange': True}, 
            dragmode=False, height=230, margin=dict(t=15, b=5, l=5, r=5), 
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_id, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

    valor_do_aporte_vif = float(st.session_state.get("input_aporte_dinamico", 0))
    target_swap_vif = float(st.session_state.get("target_arbitragem_dinamico", 15.0))

    st.markdown("<br><h3 style='text-align: center; font-weight: 800; color: #0f172a;'>🔄 Gestão Avançada (Arbitragem de Ativos)</h3>", unsafe_allow_html=True)
    cb1, cb2 = st.columns(2)

# ==============================================================================
# 🛑 FIM DO BLOCO 6 DE 9
# ==============================================================================
    with cb1:
        p_venda = float(df_ranking_completo[df_ranking_completo["Ativo"] == "HGLG11"]["Preco"].values[0]) if not df_ranking_completo[df_ranking_completo["Ativo"] == "HGLG11"].empty else 156.20
        p_compra = float(df_ranking_completo[df_ranking_completo["Ativo"] == "KNCR11"]["Preco"].values[0]) if not df_ranking_completo[df_ranking_completo["Ativo"] == "KNCR11"].empty else 104.90
        
        dy_venda = float(df_ranking_completo[df_ranking_completo["Ativo"] == "HGLG11"]["DY_Anual"].values[0]) if not df_ranking_completo[df_ranking_completo["Ativo"] == "HGLG11"].empty else 0.091
        dy_compra = float(df_ranking_completo[df_ranking_completo["Ativo"] == "KNCR11"]["DY_Anual"].values[0]) if not df_ranking_completo[df_ranking_completo["Ativo"] == "KNCR11"].empty else 0.118
        if dy_venda > 1.0: dy_venda = dy_venda / 100
        if dy_compra > 1.0: dy_compra = dy_compra / 100

        cotas_venda_sug = 10
        capital_swap_simulado = cotas_venda_sug * p_venda
        cotas_compra_sug = int(capital_swap_simulado / p_compra)
        
        renda_venda_perdida = (capital_swap_simulado * dy_venda) / 12
        renda_compra_ganha = ((cotas_compra_sug * p_compra) * dy_compra) / 12
        ganho_swap_real = max(0.0, renda_compra_ganha - renda_venda_perdida)
        
        # Sincronização com o estado global para validação no Bloco 8
        swap_aprovado = ganho_swap_real >= target_swap_vif
        st.session_state["swap_aprovado_global"] = swap_aprovado
        
        if swap_aprovado:
            texto_swap_dinamico = f"""🟢 <b>Swap Altamente Recomendado (Target Atingido)</b>.<br><br>
            • <b>Reduzir Posição (Venda):</b> Diminuir <b>{cotas_venda_sug} cotas</b> de <b>HGLG11</b> (R$ {p_venda:.2f}/un)<br>
            • <b>Aumentar Posição (Compra):</b> Adicionar <b>{cotas_compra_sug} cotas</b> de <b>KNCR11</b> (R$ {p_compra:.2f}/un)<br><br>
            💡 <i>Nota Consultativa:</i> O ganho tático seguro projetado de R$ {ganho_swap_real:.2f}/mês superou ou igualou o target de R$ {target_swap_vif:.2f}. Recomendamos executar."""
        else:
            texto_swap_dinamico = f"""🔒 <b>Swap Não Recomendado (Abaixo do Target)</b>.<br><br>
            • <b>Reduzir Posição (Venda):</b> Diminuir <b>{cotas_venda_sug} cotas</b> de <b>HGLG11</b> (R$ {p_venda:.2f}/un)<br>
            • <b>Aumentar Posição (Compra):</b> Adicionar <b>{cotas_compra_sug} cotas</b> de <b>KNCR11</b> (R$ {p_compra:.2f}/un)<br><br>
            💡 <i>Nota Consultativa:</i> O ganho tático seguro projetado de R$ {ganho_swap_real:.2f}/mês não alcançou o target de R$ {target_swap_vif:.2f}. Aguarde maior prêmio."""
            
        st.markdown(f"<div style='background-color: #ebf3fc; border-left: 6px solid #0d47a1; padding: 16px; border-radius: 4px; min-height: 220px;'><p style='color: #1e3a8a; font-size: 19px; font-weight: 800; margin: 0 0 10px 0;'>■ Comprar/Vender (Swap)</p><p style='text-align: left; color: #1e3a8a; font-size: 14.2px; line-height: 1.5; margin: 0;'>{texto_swap_dinamico}</p></div>", unsafe_allow_html=True)

    with cb2:
        ativos_na_carteira = list(carteira_real.keys())
        df_novos_ativos = df_ranking_completo[~df_ranking_completo["Ativo"].isin(ativos_na_carteira)].copy()
        ativo_top1 = df_novos_ativos["Ativo"].iloc[0] if len(df_novos_ativos) >= 1 else "CPTS11"
        ativo_top2 = df_novos_ativos["Ativo"].iloc[1] if len(df_novos_ativos) >= 2 else "BTLG11"
        
        if valor_do_aporte_vif > 0:
            reais_top1 = valor_do_aporte_vif * 0.70
            reais_top2 = valor_do_aporte_vif * 0.30
            texto_aporte_dinamico = f"""➕ <b>Aporte Ativo: R$ {valor_do_aporte_vif:,.2f}</b>.<br><br>
            • <b>Opção Principal (70%):</b> Iniciar posição em <b>{ativo_top1}</b> → Alocar R$ {reais_top1:,.2f}<br>
            • <b>Opção Alternativa (30%):</b> Iniciar posição em <b>{ativo_top2}</b> → Alocar R$ {reais_top2:,.2f}<br><br>
            💡 <i>Nota Consultativa:</i> Estes ativos lideram o radar por aliarem alto Dividend Yield com desconto patrimonial em tela (P/VP descontado)."""
        else:
            texto_aporte_dinamico = f"■ Papéis recomendados para radar (fora da carteira): <b>{ativo_top1} (70%)</b> ou <b>{ativo_top2} (30%)</b>.<br>SEM aporte alocado no momento."
            
        st.markdown(f"<div style='background-color: #ebf3fc; border-left: 6px solid #0d47a1; padding: 16px; border-radius: 4px; min-height: 220px;'><p style='color: #1e3a8a; font-size: 19px; font-weight: 800; margin: 0 0 10px 0;'>➕ Sugestão para Expansão (Aporte Direto)</p><p style='text-align: left; color: #1e3a8a; font-size: 14.2px; line-height: 1.5; margin: 0;'>{texto_aporte_dinamico}</p></div>", unsafe_allow_html=True)

    st.markdown("<br><h3 style='text-align: center; font-weight: 800; color: #0f172a;'>🔄 Rebalanceamento (Carteira Alvo)</h3>", unsafe_allow_html=True)

# ==============================================================================
# 🛑 FIM DO BLOCO 7 DE 9
# ==============================================================================
    # HERDA O CÁLCULO DINÂMICO PARA SINCRONIZAÇÃO ABSOLUTA DO REBALANCEAMENTO
    linha_venda = df_ranking_completo[df_ranking_completo["Ativo"] == "HGLG11"]
    p_venda = float(linha_venda["Preco"].values[0]) if not linha_venda.empty else 156.20
    
    linha_compra = df_ranking_completo[df_ranking_completo["Ativo"] == "KNCR11"]
    p_compra = float(linha_compra["Preco"].values[0]) if not linha_compra.empty else 104.90

    cotas_venda_sug = 10
    capital_origem_swap = cotas_venda_sug * p_venda
    cotas_compra_sug = int(capital_origem_swap / p_compra)
    
    swap_aprovado_final = st.session_state.get("swap_aprovado_global", False)
    sim_dados = st.session_state.get("dados_simulados")

    if valor_do_aporte_vif > 0 or swap_aprovado_final:
        lista_cotas_comprar = []
        capital_real_swap_ativo = capital_origem_swap if swap_aprovado_final else 0.0
        orcamento_total_compras = valor_do_aporte_vif + capital_real_swap_ativo
        
        if valor_do_aporte_vif == 0 and capital_real_swap_ativo > 0:
            custo_aproximado = cotas_compra_sug * p_compra
            lista_cotas_comprar.append(f"■ Executar Swap Tático: Vender <b>{cotas_venda_sug} cotas</b> de HGLG11 e comprar <b>{cotas_compra_sug} cotas</b> de <b>KNCR11</b> (Custo aproximado = R$ {custo_aproximado:,.2f})")
        else:
            if capital_real_swap_ativo > 0:
                lista_cotas_comprar.append(f"■ Executar Origem do Swap: Reduzir <b>{cotas_venda_sug} cotas</b> de HGLG11 (Gera R$ {capital_real_swap_ativo:,.2f})")
            
            # CORREÇÃO CRÍTICA: Força o Bloco 8 a recalcular a carteira alvo com o patrimônio futuro atualizado do Bloco 5
            patrimonio_alvo_calculo = sim_dados["patrimonio_total_futuro_v2"] if sim_dados else (total_carteira_atual + valor_do_aporte_vif)
            df_ideal_atualizado = construir_carteira(df_ranking_carteira, patrimonio_alvo_calculo)
            
            soma_alocacao_alvo = df_ideal_atualizado["Alocacao_Ajustada"].sum() if "Alocacao_Ajustada" in df_ideal_atualizado.columns else df_ideal_atualizado["Valor_Alvo"].sum()
            col_valor_alvo = "Alocacao_Ajustada" if "Alocacao_Ajustada" in df_ideal_atualizado.columns else "Valor_Alvo"
            
            compras_temporarias = {}
            saldo_restante = orcamento_total_compras
            
            # Passo 1: Distribuição proporcional inicial baseada no novo cálculo
            for _, r in df_ideal_atualizado.iterrows():
                if not swap_aprovado_final and r["Ativo"] == "HGLG11":
                    continue
                if soma_alocacao_alvo > 0:
                    percentual_ideal_ativo = r[col_valor_alvo] / soma_alocacao_alvo
                    capital_proporcional = orcamento_total_compras * percentual_ideal_ativo
                    
                    # Busca o preço real do ativo no ranking do mercado atual usando [0] com segurança
                    linha_fii_preco = df_ranking_completo[df_ranking_completo["Ativo"] == r["Ativo"]]
                    preco_fii = float(linha_fii_preco["Preco"].values[0]) if not linha_fii_preco.empty else precos_base_estatico.get(r["Ativo"], 100.0)
                    
                    qtd_inicial = int(capital_proporcional / preco_fii)
                    compras_temporarias[r["Ativo"]] = {"qtd": qtd_inicial, "preco": preco_fii}
                    saldo_restante -= (qtd_inicial * preco_fii)
            
            # Passo 2: Distribuição dos resíduos usando o índice correto da tupla x[1]
            ativos_ordenados_preco = sorted(compras_temporarias.items(), key=lambda x: x[1]["preco"])
            for ativo_nome, info in ativos_ordenados_preco:
                if saldo_restante >= info["preco"]:
                    cotas_a_mais = int(saldo_restante / info["preco"])
                    compras_temporarias[ativo_nome]["qtd"] += cotas_a_mais
                    saldo_restante -= (cotas_a_mais * info["preco"])
            
            # Passo 3: Montagem das mensagens visuais
            custo_total_realizado = 0.0
            for ativo_nome, info in compras_temporarias.items():
                if info["qtd"] > 0:
                    custo_fii = info["qtd"] * info["preco"]
                    custo_total_realizado += custo_fii
                    lista_cotas_comprar.append(f"■ Destinação de Capital: Comprar <b>{info['qtd']} cotas</b> de <b>{ativo_nome}</b> (Valor aproximado = R$ {custo_fii:,.2f})")
                        
        texto_cotas_final = "<br>".join(lista_cotas_comprar) if lista_cotas_comprar else "Ajuste financeiro abaixo do preço de 1 cota de tela."
        texto_rebalanceamento = f"🎯 <b>Gatilho de Rebalanceamento ATIVADO!</b> Operações otimizadas para uso máximo do saldo. Total Alocado: R$ {custo_total_realizado:,.2f} de R$ {orcamento_total_compras:,.2f}:<br><br>{texto_cotas_final}"
    else:
        texto_rebalanceamento = f"ℹ️ <b>Nenhum rebalanceamento sugerido.</b> Como a eficiência tática de arbitragem projetada não atingiu o target e nenhum aporte novo foi injetado, a recomendação oficial é manter a estrutura atual intocada."
        
    st.markdown(f"<div style='background-color: #ebf3fc; border-left: 6px solid #0d47a1; padding: 16px; border-radius: 4px; margin-bottom: 20px;'><p style='color: #1e3a8a; font-size: 16px; font-weight: bold; line-height: 1.7;'>{texto_rebalanceamento}</p></div>", unsafe_allow_html=True)

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1: st.button("📄 Gravar ESSE Histórico do App", key="btn_confirmar_plano", use_container_width=True, on_click=executar_gravacao_manual)
    with c_btn2: st.download_button("📥 Exportar Plano atual para Excel (.csv)", data=df_id.to_csv(index=False).encode('utf-8'), file_name="plano_fii_pro.csv", mime="text/csv", use_container_width=True)

# ==============================================================================
# 🛑 FIM DO BLOCO 8 DE 9
# ==============================================================================
# ------------------------------------------------------------------------------
# ABA CONTIGUAMENTE INTEGRADA: GESTÃO LONGO PRAZO (SIMULADOR BOLA DE NEVE FIEL À B3)
# ------------------------------------------------------------------------------
with tab_longo_prazo:
    st.markdown("<h2 style='text-align: center; font-size: 30px; font-weight: 900; color: #0f172a; margin-top: 10px; margin-bottom: 25px;'>📈 Simulador de Renda Futura & Efeito Bola de Neve</h2>", unsafe_allow_html=True)
    st.markdown("<style>.box-simulador { padding: 10px 14px; border-radius: 6px; min-height: 90px; display: flex; flex-direction: column; justify-content: center; text-align: center; border: 1.5px solid #000000 !important; }.box-azul { background-color: #ebf3fc; }.box-vermelho { background-color: #fdf2f2; }.box-verde { background-color: #e6fffa; }.lbl-sim { font-size: 16px; font-weight: bold; margin: 0; letter-spacing: 0.5px; }.val-sim { font-size: 30px; font-weight: 900; margin: 2px 0 0 0; }</style>", unsafe_allow_html=True)
    
    sim_dados = st.session_state.dados_simulados
    patrimonio_inicial_real = float(sim_dados["patrimonio_total_futuro_v2"]) if sim_dados is not None else float(total_carteira_atual)
    
    # REGRA DE OURO: O simulador assume a renda unificada (que prioriza o seu lançamento real)
    div_mensal_inicial = float(renda_carteira_atual_estimada)
    
    # Cálculo da taxa anual com base na média real dos proventos lançados por você
    if patrimonio_inicial_real > 0:
        yield_real_fiel = (div_mensal_inicial * 12) / patrimonio_inicial_real
    else:
        yield_real_fiel = 0.105  # Protetor de segurança caso a carteira esteja zerada
        
    taxa_mensal = (1 + yield_real_fiel) ** (1/12) - 1
    
    anos_eixo = [2.5, 5.0, 7.5, 10.0, 12.0, 14.0, 16.0, 18.0]
    lista_patr, lista_prov = [], []
    for t_anos in anos_eixo:
        meses = int(t_anos * 12)
        patr_acumulado = patrimonio_inicial_real
        for _ in range(meses): 
            patr_acumulado += (patr_acumulado * taxa_mensal)
        lista_patr.append(round(patr_acumulado, 2))
        lista_prov.append(round(patr_acumulado * taxa_mensal, 2))
        
    df_p = pd.DataFrame({"Tempo": ["2.5", "5", "7.5", "10", "12", "14", "16", "18"], "Patrimônio Acumulado": lista_patr, "Proventos Mensais": lista_prov})
    patrimonio_projetado_18 = lista_patr[-1]
    renda_mensal_projetada_18 = lista_prov[-1]

    meta_renda = 5000.0
    meses_meta = 0
    patr_meta_acumulado = patrimonio_inicial_real
    while (patr_meta_acumulado * taxa_mensal) < meta_renda and meses_meta < 600:
        patr_meta_acumulado += (patr_meta_acumulado * taxa_mensal)
        meses_meta += 1
    anos_meta = meses_meta // 12
    restante_meses = meses_meta % 12

    cl1, cl2, cl3 = st.columns(3)
    with cl1: st.markdown(f"<div class='box-simulador box-azul'><p class='lbl-sim' style='color:#1e40af;'>🎯 RENDA ALVO</p><p class='val-sim' style='color:#1e3a8a;'>R$ {meta_renda:,.2f}</p></div>", unsafe_allow_html=True)
    with cl2: st.markdown(f"<div class='box-simulador box-vermelho'><p class='lbl-sim' style='color:#9b2c2c;'>🔁 DIVIDENDO REINVESTIDO</p><p class='val-sim' style='color:#742a2a;'>R$ {div_mensal_inicial:,.2f}</p></div>", unsafe_allow_html=True)
    with cl3: st.markdown("<div class='box-simulador box-verde'><p class='lbl-sim' style='color:#234e52;'>⏳ PERÍODO DE PROJEÇÃO</p><p class='val-sim' style='color:#1d4044;'>1 a 18 Anos</p></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
    
    cl4, cl5, cl6 = st.columns(3)
    with cl4: st.markdown(f"<div class='box-simulador box-azul'><p class='lbl-sim' style='color:#1e40af;'>💸 RENDA MENSAL (18 ANOS)</p><p class='val-sim' style='color:#1e3a8a;'>R$ {renda_mensal_projetada_18:,.2f}</p></div>", unsafe_allow_html=True)
    with cl5: st.markdown(f"<div class='box-simulador box-vermelho'><p class='lbl-sim' style='color:#9b2c2c;'>💰 PATRIMÔNIO (18 ANOS)</p><p class='val-sim' style='color:#742a2a;'>R$ {patrimonio_projetado_18:,.2f}</p><span style='color:#9b2c2c; font-size:12px; font-weight:bold;'>DY Médio Real: {yield_real_fiel*100:.2f}% a.a.</span></div>", unsafe_allow_html=True)
    with cl6: st.markdown(f"<div class='box-simulador box-verde'><p class='lbl-sim' style='color:#234e52;'>🏁 META ATINGIDA EM:</p><p class='val-sim' style='color:#1d4044;'>{anos_meta}a e {restante_meses}m</p></div>", unsafe_allow_html=True)
    
    patr_necessario_meta = meta_renda / taxa_mensal
    fator_fva = (((1 + taxa_mensal) ** 216) - 1) / taxa_mensal
    aporte_bolso_necessario = max(0.0, (patr_necessario_meta - (patrimonio_inicial_real * ((1 + taxa_mensal) ** 216))) / fator_fva)
    total_mensal_advisory = div_mensal_inicial + aporte_bolso_necessario
    
    st.markdown(f"""
        <div style='background-color: #f8fafc; border: 1.5px solid #000000; padding: 16px; border-radius: 6px; margin-top: 20px; text-align: center;'>
            <p style='color: #0f172a; font-size: 15px; font-family: Arial; line-height: 1.6; margin: 0;'>💡 <span style='color:#0d47a1; font-weight:bold;'>NOTA CONSULTATIVA TÁTICA:</span> Para cravar a sua meta de <b>R$ 5.000,00/mês</b> baseada na performance real atual, seria necessário reinvestir seu dividendo = <span style='color:#0d47a1; font-weight:bold;'>R$ {div_mensal_inicial:,.2f}</span> + <span style='color:#742a2a; font-weight:bold;'>R$ {aporte_bolso_necessario:,.2f}</span> do bolso.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    ch3, ch4 = st.columns(2)
    with ch3: st.markdown("<p style='text-align: center; font-size: 16px; font-family: Arial; font-weight: bold; color: #0f172a; margin-bottom: -15px;'>🚀 Crescimento do Patrimônio (Base: Histórico Real)</p>", unsafe_allow_html=True)
    with ch4: st.markdown("<p style='text-align: center; font-size: 16px; font-family: Arial; font-weight: bold; color: #0f172a; margin-bottom: -15px;'>🌊 Efeito Bola de Neve (Média Real Calculada)</p>", unsafe_allow_html=True)
    
    cg3, cg4 = st.columns(2)
    with cg3:
        fig_cresc = px.bar(df_p, x="Tempo", y="Patrimônio Acumulado", color_discrete_sequence=["#7f1d1d"])
        fig_cresc.update_layout(height=260, margin=dict(t=15, b=10, l=10, r=10), xaxis_title="Tempo (Anos)", yaxis_title="Patrimônio Acumulado", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig_cresc.update_xaxes(type='category', tickfont=dict(color='#000000', size=12, family='Arial', weight='bold'))
        fig_cresc.update_yaxes(tickfont=dict(color='#000000', size=12, family='Arial', weight='bold'))
        st.plotly_chart(fig_cresc, use_container_width=True, config={'displayModeBar': False})
    with cg4:
        fig_bola = px.bar(df_p, x="Tempo", y="Proventos Mensais", color_discrete_sequence=["#0d47a1"])
        fig_bola.update_layout(height=260, margin=dict(t=15, b=10, l=10, r=10), xaxis_title="Tempo (Anos)", yaxis_title="Proventos Mensais", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig_bola.update_xaxes(type='category', tickfont=dict(color='#000000', size=12, family='Arial', weight='bold'))
        fig_bola.update_yaxes(tickfont=dict(color='#000000', size=12, family='Arial', weight='bold'))
        fig_bola.add_hline(y=5000, line_dash="dash", line_color="#ef4444")
        st.plotly_chart(fig_bola, use_container_width=True, config={'displayModeBar': False})
        
    st.markdown("""<div style='background-color: #fdf2f2; border: 1.5px solid #dc2626; padding: 12px; border-radius: 6px; text-align: center;'><p style='margin:0; font-size:12px; font-weight:bold; color:#b91c1c;'>⚠️ Linha vermelha pontilhada indica o patamar da Meta de Renda Alvo.</p></div>""", unsafe_allow_html=True)

# ==============================================================================
# 🛑 FIM DO BLOCO 9 DE 9
# ==============================================================================