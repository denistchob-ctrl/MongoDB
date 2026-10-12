# ui/secao_agregadores.py
import streamlit as st

from core import agregadores_catalogo
from ui._resultado_query import render_resultado
from ui.componentes import titulo


def render():
    titulo("Agregadores",
           "Pipelines que sumarizam dados e apoiam decisões de negócio")

    st.markdown("""
    Escolha um agregador no seletor abaixo. Serão exibidos:
    - o **pipeline** utilizado,
    - uma **explicação** do seu valor para o negócio,
    - o **resultado real** obtido na base atual (até 5 linhas).
    """)

    # ---------- Combobox (título do agregador) ----------
    opcoes = {ag["id"]: ag["titulo"] for ag in agregadores_catalogo.CATALOGO}

    id_selecionado = st.selectbox(
        "📊 Selecione um agregador",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
    )

    item = next(a for a in agregadores_catalogo.CATALOGO if a["id"] == id_selecionado)

    # ---------- Cabeçalho ----------
    st.markdown(f"### {item['titulo']}")

    # ---------- Pipeline ----------
    st.markdown("#### 💻 Pipeline")
    st.code(item["comando"], language="javascript")

    # ---------- Execução ----------
    try:
        resultado = agregadores_catalogo.executar(id_selecionado)
        render_resultado(resultado, mostrar_explicacao=item["explicacao"])
    except Exception as e:
        st.error(f"❌ Erro ao executar o agregador: {e}")
