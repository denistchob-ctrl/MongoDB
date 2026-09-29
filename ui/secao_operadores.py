# ui/secao_operadores.py
import streamlit as st
from core import executar_operadores
from ui.componentes import titulo, badge

def render():
    titulo("Operadores MongoDB",
           "Demonstração dos principais operadores de consulta")

    st.markdown("""
    Cada operador é apresentado com **descrição**, **comando** e **resultado real**
    obtido a partir da base carregada.
    """)

    operadores = executar_operadores.catalogo()

    for op in operadores:
        with st.expander(f"🔹 {op['nome']} — {op['titulo']}", expanded=False):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Descrição:** {op['descricao']}")
                st.markdown(f"**Comando:**")
                st.code(op["comando"], language="javascript")
            with col2:
                badge(op["categoria"], "laranja")

            st.markdown("**Resultado:**")
            try:
                resultado = executar_operadores.executar(op["id"])
                if isinstance(resultado, list) and len(resultado) > 0:
                    st.dataframe(resultado, use_container_width=True, height=220)
                elif isinstance(resultado, list):
                    st.info("Nenhum documento retornado.")
                else:
                    st.json(resultado)
            except Exception as e:
                st.error(f"Erro: {e}")