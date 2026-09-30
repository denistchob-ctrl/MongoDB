# ui/secao_base_simples.py
import streamlit as st
from core import carregar_base_simples
from ui.componentes import titulo, card

def render():
    titulo("Base de Dados Simples",
           "Carga do dataset inicial (12 produtos, 10 clientes, 16 pedidos)")

    st.markdown("""
    Esta seção executa o script `mongo_inclusao_v2.js` — a base **mínima**
    que serve para demonstrar os operadores e agregações.
    """)

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🚀 Carregar base simples", use_container_width=True):
            with st.spinner("Limpando e recarregando..."):
                resultado = carregar_base_simples.executar()
            # st.success(f"Base carregada: {resultado['produtos']} produtos, "
            #            f"{resultado['clientes']} clientes, "
            #            f"{resultado['pedidos']} pedidos.")
            st.success(
                f"Base carregada: {resultado['total_produtos']} produtos, "
                f"{resultado['total_clientes']} clientes, "
                f"{resultado['total_pedidos']} pedidos."
            )
            st.session_state["base_carregada"] = True

    if st.session_state.get("base_carregada"):
        st.markdown("### 📊 Estatísticas das coleções")

        stats = carregar_base_simples.estatisticas()

        for nome_col, info in stats.items():
            with st.expander(f"📁 {nome_col} — {info['total']} documentos", expanded=False):
                st.markdown(f"**Estrutura do documento:**")
                st.json(info["amostra"])

