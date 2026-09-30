# ui/secao_proposta.py
import streamlit as st
from ui.componentes import titulo, card, badge

from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError


DB_USERNAME = st.secrets.get("DB_USERNAME", "")
DB_PWD      = st.secrets.get("DB_PWD", "")
DB_HOST     = st.secrets.get("DB_HOST", "")
DB_NAME     = st.secrets.get("DB_NAME", "loja")

if DB_USERNAME and DB_PWD and DB_HOST:
    MONGO_URI = f"mongodb+srv://{DB_USERNAME}:{DB_PWD}@{DB_HOST}/?appName=Cluster0&retryWrites=true&w=majority&authSource=admin"
else:
    MONGO_URI = "mongodb://localhost:27017/"

# Diagnóstico — útil para debug
AMBIENTE = "NUVEM (ATLAS)" if "mongodb+srv" in MONGO_URI else "LOCAL (localhost)"

def render():
    titulo("Usando MongoDB para uma Loja de Produtos de Informática",
           "Projeto de Banco de Dados 2 — Ciência de Dados para Negócios")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        card("📖 Sobre o projeto", """
        Este projeto demonstra o uso do **MongoDB** como banco de dados NoSQL
        aplicado a uma loja de produtos de informática, cobrindo desde a
        **modelagem de dados** até **análises preditivas** com a biblioteca
        **Prophet**.

        O trabalho percorre:
        - **Modelagem** das coleções `produtos`, `clientes` e `pedidos`
          (com itens embutidos).
        - **Operadores** de consulta (`$gt`, `$all`, `$regex`, `$mod`, `$exists`, …).
        - **Agregações** para responder perguntas de negócio.
        - **Séries temporais** de vendas, quantidade e ticket médio.
        - **Backtest** para validar a qualidade das previsões.
        """, destaque=True)

    with col2:
        badge("MongoDB", "azul")
        badge("Prophet", "laranja")
        badge("Streamlit", "azul")
        badge("Ciência de Dados", "verde")

    st.markdown("### 🎯 Objetivos de aprendizagem")
    st.markdown("""
    - Projetar um banco de dados MongoDB para representar um negócio real.
    - Aplicar operadores e agregações que apoiem decisões gerenciais.
    - Desenvolver um exemplo de série temporal com o Prophet.
    - Explicar os resultados à luz do negócio.
    """)

    st.markdown("### 👤 Autor")
    st.markdown("**Denis Tchobnian Cardoso** — RA 2721542522018")

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
        client.admin.command("ping")
        st.sidebar.caption("✅ Conexão e autenticação OK")
        st.sidebar.caption(f">>> {MONGO_URI} <<<")

        db = client["loja"]
        db.teste.insert_one({"ping": 1})
        st.sidebar.caption("✅ Escrita no banco 'loja' OK")
        st.sidebar.caption(db.teste.count_documents({}))
        # db.teste.drop()

    except OperationFailure as e:
        st.sidebar.caption(f"❌ OperationFailure — Código: {e.code}")
        st.sidebar.caption(f"Mensagem completa: {e.details}")
    except ServerSelectionTimeoutError:
        st.sidebar.caption("❌ Timeout — IP Access List bloqueou a conexão")
    except Exception as e:
        st.sidebar.caption(f"❌ Erro inesperado: {type(e).__name__} - {e}")

