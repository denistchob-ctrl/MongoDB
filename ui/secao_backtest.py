# ui/secao_backtest.py
import streamlit as st
from core import backtest
from textos.explicacoes_backtest import EXPLICACOES
from ui.componentes import titulo, badge

def render():
    titulo("Backtest",
           "Validação da qualidade das previsões por granularidade")

    if st.button("🧪 Executar backtest completo", use_container_width=True):
        with st.spinner("Rodando backtest diário, semanal e mensal..."):
            resultado = backtest.executar()
        st.session_state["backtest"] = resultado

    resultado = st.session_state.get("backtest")
    if not resultado:
        st.info("Clique em **Executar backtest completo** para começar.")
        return

    # Tabela
    st.markdown("### 📋 Resultados numéricos")
    st.dataframe(resultado["tabela"], use_container_width=True)

    # Heatmap
    st.markdown("### 🔥 Heatmap consolidado")
    st.pyplot(resultado["fig_heatmap"])

    # Gráfico de linhas
    st.markdown("### 📈 Comparativo entre séries")
    st.pyplot(resultado["fig_linhas"])

    # Explicações editoriais
    st.markdown("### 📖 Interpretação")
    for chave, exp in EXPLICACOES.items():
        with st.expander(f"🔎 {exp['titulo']}", expanded=False):
            badge(exp["categoria"], "laranja")
            st.markdown(exp["corpo"])
