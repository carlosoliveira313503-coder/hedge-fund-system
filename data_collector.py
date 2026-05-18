import yfinance as yf
import sqlite3

ativos = ["HGLG11.SA","XPLG11.SA","VISC11.SA","KNIP11.SA"]
conn = sqlite3.connect("database.db")

for ativo in ativos:
    data = yf.download(ativo, period="5y")
    data = data.reset_index()
    data["Ticker"] = ativo
    data.to_sql("precos", conn, if_exists="append", index=False)

print("Dados atualizados com sucesso")
