# teste_conexao.py
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

import streamlit as st
# ---------- CONEXÃO ----------
MONGO_URI = st.secrets.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = st.secrets.get("DB_NAME", "loja")

# Diagnóstico — útil para debug
AMBIENTE = "NUVEM (ATLAS)" if "mongodb+srv" in MONGO_URI else "LOCAL (localhost)"

# # ⚠️ Cole aqui a URI COMPLETA que está nos Secrets do Streamlit
# MONGO_URI = "mongodb+srv://SEU_USUARIO:SUA_SENHA@cluster0.jeoi1gg.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    client.admin.command("ping")
    print("✅ Conexão e autenticação OK")

    # Tenta uma operação de escrita no banco 'loja'
    db = client["loja"]
    db.teste.insert_one({"ping": 1})
    print("✅ Escrita no banco 'loja' OK")
    db.teste.drop()

except OperationFailure as e:
    print(f"❌ OperationFailure — Código: {e.code}")
    print(f"Mensagem completa: {e.details}")
except ServerSelectionTimeoutError:
    print("❌ Timeout — IP Access List bloqueou a conexão")
except Exception as e:
    print(f"❌ Erro inesperado: {type(e).__name__} - {e}")
