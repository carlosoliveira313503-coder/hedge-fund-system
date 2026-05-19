import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# 1. CRIAR / CONECTAR BANCO
# =========================
conn = sqlite3.connect("database.db")

# =========================
# 2. FUNÇÃO PARA GERAR DADOS
# =========================
def gerar_dados():
    ativos = [
        "HGLG11.SA",
        "XPLG11.SA",
        "VISC11.SA",
        "KNIP11.SA",
