# uicomponentes.py
import streamlit as st
from config.settings import CORES

def titulo(texto, subtitulo=None)
    st.markdown(f# {texto})
    if subtitulo
        st.markdown(f{subtitulo})

def card(titulo, corpo, destaque=False)
    classe = card-destaque if destaque else card-projeto
    st.markdown(f
        div class={classe}
            h3 style=margin-top0{titulo}h3
            div{corpo}div
        div
    , unsafe_allow_html=True)

def badge(texto, tipo=azul)
    cores = {
        azul    (CORES[azul_primario], CORES[azul_claro]),
        laranja (CORES[laranja_escuro], CORES[laranja_claro]),
        verde   (#1a4d2e, CORES[sucesso]),
        vermelho(#5a1e1e, CORES[erro]),
    }
    bg, fg = cores.get(tipo, cores[azul])
    st.markdown(f
        span style=
            background{bg};
            color{fg};
            padding3px 10px;
            border-radius12px;
            font-size.8rem;
            font-weight600;
        {texto}span
    , unsafe_allow_html=True)

def alerta(texto, tipo=info)
    st.info(texto) if tipo == info else st.warning(texto)
