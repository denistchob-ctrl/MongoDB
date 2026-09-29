# ui/secao_series.py
import streamlit as st
from core import series_temporais
from textos.explicacoes_series import EXPLICACOES
from ui.componentes import titulo
from config.settings import PERIODOS_FUTURO

def render():
    titulo("Séries Temporais com Prophet",
           f"Previsões de {PERIODOS_FUTURO} dias para valor, quantidade e ticket médio")

    serie = st.selectbox(
        "Escolha a série",
        ["valor", "qtd", "ticket"],
        format_func=lambda x: {"valor":"Valor (R$)","qtd":"Quantidade","ticket":"Ticket médio (R$/un)"}[x],
    )

    exp = EXPLICACOES.get(serie, {})
    if exp:
        st.markdown(f"**📖 Sobre a série:** {exp.get('sobre','')}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📈 Tendência:** {exp.get('tendencia','')}")
            st.markdown(f"**📅 Sazonalidade semanal:** {exp.get('semanal','')}")
        with col2:
            st.markdown(f"**🎄 Feriados:** {exp.get('feriados','')}")
            st.markdown(f"**💡 Aplicação de negócio:** {exp.get('negocio','')}")

    if st.button("🚀 Treinar e prever", use_container_width=True):
        with st.spinner("Treinando Prophet..."):
            resultado = series_temporais.executar(serie, PERIODOS_FUTURO)
        st.session_state[f"serie_{serie}"] = resultado

    resultado = st.session_state.get(f"serie_{serie}")
    if resultado:
        st.markdown("### 📊 Previsão")
        st.pyplot(resultado["fig_previsao"])

        st.markdown("### 🧩 Componentes")
        st.pyplot(resultado["fig_componentes"])

        st.markdown("### 📥 Dados da previsão")
        st.dataframe(resultado["previsao"].tail(15), use_container_width=True)
