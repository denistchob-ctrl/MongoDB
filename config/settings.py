# config/settings.py
# =============================================================
# CONFIGURAÇÕES CENTRAIS DO PROJETO
# Altere as cores aqui e TODO o app se ajusta.
# =============================================================

# ---------- CONEXÃO ----------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME   = "loja"

import streamlit as st
# DB_USERNAME = st.secrets.get("DB_USERNAME", "")
# DB_PWD      = st.secrets.get("DB_PWD", "")
# DB_HOST     = st.secrets.get("DB_HOST", "")
# DB_NAME     = st.secrets.get("DB_NAME", "loja")

# if DB_USERNAME and DB_PWD and DB_HOST:
#     MONGO_URI = f"mongodb+srv://{DB_USERNAME}:{DB_PWD}@{DB_HOST}/?appName=Cluster0"
# else:
#     MONGO_URI = "mongodb://localhost:27017/"

# ---------- CONEXÃO ----------
MONGO_URI = st.secrets.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = st.secrets.get("DB_NAME", "loja")

# Diagnóstico — útil para debug
AMBIENTE = "NUVEM (Atlas)" if "mongodb+srv" in MONGO_URI else "LOCAL (localhost)"

# ---------- PALETA ----------
# Tom metálico azul + destaque laranja
CORES = {
    # Fundos
    "fundo":              "#0d1117",
    "fundo_card":         "#161b22",
    "fundo_card_hover":   "#1c2128",

    # Textos
    "texto":              "#e6edf3",
    "texto_suave":        "#8b949e",

    # Azuis (metálico)
    "azul_primario":      "#1f6feb",   # azul do GitHub
    "azul_secundario":    "#388bfd",
    "azul_escuro":        "#0d419d",
    "azul_claro":         "#79c0ff",
    "azul_metalico":      "#4a6fa5",

    # Laranja (destaque)
    "laranja":            "#f0883e",
    "laranja_claro":      "#ffa657",
    "laranja_escuro":     "#bd561d",

    # Semânticas
    "sucesso":            "#3fb950",
    "alerta":             "#d29922",
    "erro":               "#f85149",

    # Gráficos
    "grid":               "#30363d",
    "grafico_linha":      "#388bfd",
    "grafico_prev":       "#f0883e",
    "grafico_incerteza":  "#79c0ff",
}

# ---------- GRÁFICOS ----------
FIG_DPI         = 110
FIG_TAMANHO     = (11, 4)
FIG_TAMANHO_GDE = (12, 6)

# ---------- SÉRIES TEMPORAIS ----------
PERIODOS_FUTURO = 90
ANO_INICIO      = 2026
ANO_FIM         = 2027

STATUS_EXCLUIDOS = ["Cancelado", "Aguardando pagamento"]

# ---------- GERAÇÃO DE DADOS ----------
QTD_PEDIDOS_PADRAO  = 1800
DATA_INICIO_PADRAO  = "2026-01-01"
DATA_FIM_PADRAO     = "2026-09-30"
QTD_PRODUTOS_PADRAO = 96
QTD_CLIENTES_PADRAO = 330
