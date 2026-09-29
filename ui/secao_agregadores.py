# ui/secao_agregadores.py
import streamlit as st
from core import executar_agregadores
from textos.explicacoes_agregadores import EXPLICACOES
from ui.componentes import titulo, badge

def render():
    titulo("Agregadores",
           "Pipelines que sumarizam dados e apoiam decisões")

    agregadores = executar_agregadores.catalogo()

    for ag in agregadores:
        with st.expander(f"📊 {ag['titulo']}", expanded=False):
            st.markdown(f"**Descrição técnica:** {ag['descricao']}")
            st.markdown(f"**Comando:**")
            st.code(ag["pipeline"], language="javascript")

            # Bloco editorial (editável em textos/explicacoes_agregadores.py)
            exp = EXPLICACOES.get(ag["id"], {})
            if exp:
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**💼 Utilidade de negócio:** {exp.get('negocio','—')}")
                    st.markdown(f"**🎯 Setor beneficiado:** {exp.get('setor','—')}")
                with col2:
                    st.markdown(f"**📈 Métrica gerada:** {exp.get('metrica','—')}")
                    st.markdown(f"**💡 Recomendação:** {exp.get('recomendacao','—')}")

            st.markdown("**Resultado:**")
            try:
                df = executar_agregadores.executar(ag["id"])
                st.dataframe(df, use_container_width=True, height=280)
            except Exception as e:
                st.error(f"Erro: {e}")
