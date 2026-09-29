# uistyles.py
import streamlit as st
from config.settings import CORES

def aplicar_css()
    css = f
    style
         ---- BASE ---- 
        .stApp {{
            background linear-gradient(180deg, {CORES['fundo']} 0%, #0a0e14 100%);
            color {CORES['texto']};
        }}

         ---- SIDEBAR ---- 
        section[data-testid=stSidebar] {{
            background-color {CORES['fundo_card']};
            border-right 1px solid {CORES['azul_escuro']};
        }}

         ---- TÍTULOS ---- 
        h1, h2, h3 {{
            color {CORES['texto']};
        }}
        h1 {{
            border-bottom 2px solid {CORES['laranja']};
            padding-bottom .3rem;
        }}
        h2 {{
            border-left 4px solid {CORES['azul_primario']};
            padding-left .5rem;
        }}

         ---- CARDS ---- 
        .card-projeto {{
            background-color {CORES['fundo_card']};
            border 1px solid {CORES['azul_escuro']};
            border-radius 8px;
            padding 1.2rem;
            margin-bottom 1rem;
        }}
        .card-projetohover {{
            background-color {CORES['fundo_card_hover']};
            border-color {CORES['laranja']};
        }}

        .card-destaque {{
            background linear-gradient(135deg, {CORES['azul_escuro']} 0%, {CORES['fundo_card']} 100%);
            border-left 4px solid {CORES['laranja']};
            padding 1rem;
            border-radius 6px;
        }}

         ---- BOTÕES ---- 
        .stButton  button {{
            background-color {CORES['azul_primario']};
            color white;
            border 1px solid {CORES['azul_secundario']};
            border-radius 6px;
        }}
        .stButton  buttonhover {{
            background-color {CORES['laranja']};
            border-color {CORES['laranja_claro']};
            color white;
        }}

         ---- CÓDIGO ---- 
        code {{
            color {CORES['laranja_claro']};
            background-color #010409;
        }}

         ---- MÉTRICAS ---- 
        div[data-testid=stMetricValue] {{
            color {CORES['azul_claro']};
        }}
        div[data-testid=stMetricLabel] {{
            color {CORES['texto_suave']};
        }}

         ---- DATAFRAME ---- 
        .stDataFrame {{
            border 1px solid {CORES['azul_escuro']};
            border-radius 6px;
        }}
    style
    
    st.markdown(css, unsafe_allow_html=True)
