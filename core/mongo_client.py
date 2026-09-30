# core/mongo_client.py
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME, DB_USERNAME, DB_PWD
import streamlit as st

def get_db():
    """Retorna o database configurado."""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def ping():
    """Testa a conexão."""
    try:
        get_db().command("ping")
        return True
    except Exception as e:
        return False

def limpar_base():
    """Remove todas as coleções do projeto."""
    db = get_db()
    for col in ["produtos", "clientes", "pedidos"]:
        db[col].drop()

def estatisticas_colecoes():
    """Retorna um dict com contagem + amostra de cada coleção."""
    db = get_db()
    out = {}
    for col in ["produtos", "clientes", "pedidos"]:
        colecao = db[col]
        out[col] = {
            "total": colecao.count_documents({}),
            "amostra": colecao.find_one() or {},
        }
    return out
