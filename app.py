# app.py
import streamlit as st
from ui.styles import aplicar_css
from config.settings import MONGO_URI, DB_NAME, AMBIENTE
from ui import (
    secao_proposta,
    secao_base_simples,
    secao_geracao,
    secao_operadores,
    secao_agregadores,
    secao_series,
    secao_backtest,
)

st.set_page_config(
    page_title="Usando MongoDB para uma Loja de Produtos de Informática",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_css()

# ---------- MENU ----------
st.sidebar.markdown("## 🛒 Menu")
st.sidebar.markdown("---")

secao = st.sidebar.radio(
    "Navegação",
    [
        "🏠 Proposta do Projeto",
        "📦 Base de Dados Simples",
        "🎲 Geração de Dados Aleatórios",
        "🔍 Operadores",
        "📊 Agregadores",
        "📈 Séries Temporais",
        "🧪 Backtest",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption("Banco de Dados 2 — Ciência de Dados para Negócios")
st.sidebar.caption(f"Ambiente: {AMBIENTE}")
st.sidebar.caption(f"DB......: {DB_NAME}")
st.sidebar.caption(f"URI.....: {MONGO_URI[:20]}...")

# ---------- ROTEAMENTO ----------
if   secao == "🏠 Proposta do Projeto":          secao_proposta.render()
elif secao == "📦 Base de Dados Simples":        secao_base_simples.render()
elif secao == "🎲 Geração de Dados Aleatórios":  secao_geracao.render()
elif secao == "🔍 Operadores":                   secao_operadores.render()
elif secao == "📊 Agregadores":                  secao_agregadores.render()
elif secao == "📈 Séries Temporais":             secao_series.render()
elif secao == "🧪 Backtest":                     secao_backtest.render()
