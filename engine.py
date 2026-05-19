import sqlite3
import pandas as pd
import numpy as np
import os
import yfinance as yf

# =========================
# 1. CONEXÃO COM BANCO
# =========================
conn = sqlite3.connect("database.db")

# =========================
# 2. GARANTIR DADOS
# =========================
def carregar_dados():
    try:
        df = pd.read_sql("SELECT * FROM precos", conn)

        # se tabela existe mas está vazia, força recriação
        if df.empty:
            raise Exception("Tabela vazia")

        return df

    except:
        ativos = [
            "HGLG11.SA",
            "XPLG11.SA",
            "VISC11.SA",
            "KNIP11.SA",
            "MXRF11.SA"
        ]

        dados = []

        for ativo in ativos:
            try:
                data = yf.download(ativo, period="1y")

                if not data.empty:
                    data["Ticker"] = ativo
                    data = data.reset_index()
                    dados.append(data)

            except:
                continue

        if len(dados) == 0:
            raise Exception("Falha ao baixar dados")

