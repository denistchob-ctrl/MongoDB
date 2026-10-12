# ui/secao_operadores.py
import streamlit as st

from core import operadores_catalogo
from ui._resultado_query import render_resultado
from ui.componentes import titulo


def render():
    titulo("Operadores MongoDB",
           "Explore os principais operadores de consulta do MongoDB")

    st.markdown("""
    Escolha um operador no seletor abaixo. Serão exibidos:
    - o **comando** utilizado,
    - uma **explicação** do que ele faz,
    - o **resultado real** obtido na base atual (até 5 linhas).
    """)

    # ---------- Combobox ----------
    opcoes = {op["id"]: op["titulo"] for op in operadores_catalogo.CATALOGO}

    id_selecionado = st.selectbox(
        "🔍 Selecione um operador",
        options=list(opcoes.keys()),
        format_func=lambda x: opcoes[x],
    )

    item = next(op for op in operadores_catalogo.CATALOGO if op["id"] == id_selecionado)

    # ---------- Cabeçalho com badges ----------
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown(f"### {item['titulo']}")
    with col_b:
        st.markdown(
            f"<span style='background:#1f6feb;color:white;padding:4px 10px;"
            f"border-radius:12px;font-size:.8rem;font-weight:600;'>"
            f"{item['categoria']}</span>",
            unsafe_allow_html=True,
        )

    # ---------- Comando ----------
    st.markdown("#### 💻 Comando")
    st.code(item["comando"], language="javascript")

    # ---------- Execução ----------
    try:
        resultado = operadores_catalogo.executar(id_selecionado)
        render_resultado(resultado, mostrar_explicacao=item["explicacao"])
    except Exception as e:
        st.error(f"❌ Erro ao executar o operador: {e}")

