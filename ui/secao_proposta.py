# ui/secao_proposta.py
import streamlit as st
from ui.componentes import titulo, card, badge

def render():
    titulo("Usando MongoDB para uma Loja de Produtos de Informática",
           "Projeto de Banco de Dados 2 — Ciência de Dados para Negócios")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        card("📖 Sobre o projeto", """
        Este projeto demonstra o uso do **MongoDB** como banco de dados NoSQL
        aplicado a uma loja de produtos de informática, cobrindo desde a
        **modelagem de dados** até **análises preditivas** com a biblioteca
        **Prophet**.

        O trabalho percorre:
        - **Modelagem** das coleções `produtos`, `clientes` e `pedidos`
          (com itens embutidos).
        - **Operadores** de consulta (`$gt`, `$all`, `$regex`, `$mod`, `$exists`, …).
        - **Agregações** para responder perguntas de negócio.
        - **Séries temporais** de vendas, quantidade e ticket médio.
        - **Backtest** para validar a qualidade das previsões.
        """, destaque=True)

    with col2:
        badge("MongoDB", "azul")
        badge("Prophet", "laranja")
        badge("Streamlit", "azul")
        badge("Ciência de Dados", "verde")

    st.markdown("### 🎯 Objetivos de aprendizagem")
    st.markdown("""
    - Projetar um banco de dados MongoDB para representar um negócio real.
    - Aplicar operadores e agregações que apoiem decisões gerenciais.
    - Desenvolver um exemplo de série temporal com o Prophet.
    - Explicar os resultados à luz do negócio.
    """)

    st.markdown("### 👤 Autor")
    st.markdown("**Denis Tchobnian Cardoso** — RA 2721542522018")
