# ui/secao_geracao.py
import streamlit as st
from datetime import date
from core import gerar_base_aleatoria
from ui.componentes import titulo
from config.settings import (
    QTD_PEDIDOS_PADRAO, DATA_INICIO_PADRAO, DATA_FIM_PADRAO,
    QTD_PRODUTOS_PADRAO, QTD_CLIENTES_PADRAO,
)

def render():
    titulo("Geração de Dados Aleatórios",
           "Gera uma base realista parametrizável (produtos, clientes, pedidos)")

    with st.form("form_geracao"):
        st.markdown("### ⚙️ Parâmetros")

        col1, col2 = st.columns(2)

        with col1:
            qtd_pedidos = st.slider(
                "Quantidade de pedidos",
                min_value=100, max_value=5000,
                value=QTD_PEDIDOS_PADRAO, step=100,
            )
            qtd_produtos = st.slider(
                "Quantidade de produtos",
                min_value=12, max_value=300,
                value=QTD_PRODUTOS_PADRAO, step=12,
            )

        with col2:
            data_inicio = st.date_input(
                "Data de início",
                value=date.fromisoformat(DATA_INICIO_PADRAO),
            )
            data_fim = st.date_input(
                "Data de fim",
                value=date.fromisoformat(DATA_FIM_PADRAO),
            )

        qtd_clientes = st.slider(
            "Quantidade de clientes",
            min_value=10, max_value=1000,
            value=QTD_CLIENTES_PADRAO, step=10,
        )

        st.markdown("---")

        col_a, col_b = st.columns(2)
        with col_a:
            limpar = st.checkbox("Limpar base antes de gerar", value=True)
        with col_b:
            enviar = st.form_submit_button("🎲 Gerar base", use_container_width=True)

    if enviar:
        if data_inicio >= data_fim:
            st.error("A data de início deve ser anterior à data de fim.")
        else:
            with st.spinner("Gerando base realista..."):
                resumo = gerar_base_aleatoria.executar(
                    qtd_pedidos=qtd_pedidos,
                    qtd_produtos=qtd_produtos,
                    qtd_clientes=qtd_clientes,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    limpar=limpar,
                )
            st.success("Base gerada com sucesso!")
            st.json(resumo)
