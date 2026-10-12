# ui/secao_geracao.py
# ------------------------------------------------------------
# Seção unificada: geração simples (pré-definida) + aleatória
# Mostra sempre a amostra atual do banco + botão de limpeza.
# ------------------------------------------------------------
from datetime import date

import streamlit as st

from core import carregar_base_simples, gerar_base_aleatoria
from core.mongo_client import get_db, limpar_base
from ui.componentes import titulo
from config.settings import (
    QTD_PEDIDOS_PADRAO, DATA_INICIO_PADRAO, DATA_FIM_PADRAO,
    QTD_PRODUTOS_PADRAO, QTD_CLIENTES_PADRAO,
)


# ============================================================
# HELPERS
# ============================================================
def _json_safe(obj):
    """Converte datetime, date e ObjectId em strings para o st.json()."""
    from datetime import datetime as _dt, date as _d
    from bson import ObjectId

    if isinstance(obj, (_dt, _d)):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(i) for i in obj]
    return obj


def _estatisticas_do_banco() -> dict:
    """Lê contagem + amostra das coleções — funciona com qualquer base."""
    db = get_db()
    out = {}
    for col in ["produtos", "clientes", "pedidos"]:
        out[col] = {
            "total":   db[col].count_documents({}),
            "amostra": db[col].find_one() or {},
        }
    return out


# ============================================================
# BLOCO DE ESTATÍSTICAS + LIMPEZA
# ============================================================
def _render_estatisticas():
    """Bloco comum de estatísticas + botão de limpeza."""
    st.markdown("---")
    st.markdown("### 📊 Estatísticas atuais do banco")

    stats = _estatisticas_do_banco()

    # ---------- Cards no topo ----------
    col1, col2, col3 = st.columns(3)
    col1.metric("Produtos", stats["produtos"]["total"])
    col2.metric("Clientes", stats["clientes"]["total"])
    col3.metric("Pedidos",  stats["pedidos"]["total"])

    # ---------- Amostras ----------
    for nome, info in stats.items():
        with st.expander(f"📁 {nome} — {info['total']} documentos", expanded=False):
            if info["total"] == 0:
                st.info("Coleção vazia.")
                continue
            st.markdown("**Estrutura do documento (amostra):**")
            st.json(_json_safe(info["amostra"]))

    # ---------- Botão de limpeza (com confirmação em 2 etapas) ----------
    st.markdown("---")
    st.markdown("### 🗑️ Limpeza da base")

    # Inicializa o estado
    if "confirmar_limpeza" not in st.session_state:
        st.session_state["confirmar_limpeza"] = False

    total_geral = (
        stats["produtos"]["total"]
        + stats["clientes"]["total"]
        + stats["pedidos"]["total"]
    )

    if total_geral == 0:
        st.info("A base já está vazia — nada para limpar.")
        return

    col_btn, col_msg = st.columns([1, 3])

    with col_btn:
        if not st.session_state["confirmar_limpeza"]:
            if st.button("🗑️ Limpar base", use_container_width=True, key="btn_limpar_inicial"):
                st.session_state["confirmar_limpeza"] = True
                st.rerun()
        else:
            if st.button("✅ Confirmar limpeza", use_container_width=True,
                         type="primary", key="btn_confirmar_limpeza"):
                try:
                    limpar_base()
                    st.session_state["confirmar_limpeza"] = False
                    st.session_state["base_carregada"] = False
                    st.success("✅ Base limpa com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao limpar base: {e}")

            if st.button("❌ Cancelar", use_container_width=True, key="btn_cancelar_limpeza"):
                st.session_state["confirmar_limpeza"] = False
                st.rerun()

    with col_msg:
        if st.session_state["confirmar_limpeza"]:
            st.warning(
                f"⚠️ **Atenção:** isso vai apagar **{total_geral} documentos** "
                f"({stats['produtos']['total']} produtos, "
                f"{stats['clientes']['total']} clientes, "
                f"{stats['pedidos']['total']} pedidos). "
                "A operação **não pode ser desfeita**."
            )
        else:
            st.caption(
                "Use este botão para zerar o banco antes de uma nova demonstração. "
                "Será pedida uma confirmação."
            )


# ============================================================
# RENDER
# ============================================================
def render():
    titulo("Geração de Base de Dados",
           "Escolha entre uma base simples (pré-definida) ou uma base aleatória parametrizável")

    col_esq, col_dir = st.columns(2, gap="large")

    # ---------- COLUNA ESQUERDA — Base Simples ----------
    with col_esq:
        st.markdown("### 📦 Base Simples Pré Definida")
        st.caption("Carga do dataset inicial (12 produtos, 10 clientes, 16 pedidos)")
        st.markdown("""
        Esta opção executa o script `mongo_inclusao_v2.js` — a base **mínima**
        que serve para demonstrar os operadores e agregações.
        """)

        if st.button("🚀 Carregar base simples", use_container_width=True, key="btn_simples"):
            with st.spinner("Limpando e recarregando..."):
                try:
                    resultado = carregar_base_simples.executar()
                    st.success(
                        f"Base carregada: {resultado['produtos']} produtos, "
                        f"{resultado['clientes']} clientes, "
                        f"{resultado['pedidos']} pedidos."
                    )
                    st.session_state["base_carregada"] = True
                    st.session_state["confirmar_limpeza"] = False
                except Exception as e:
                    st.error(f"❌ Erro ao carregar base simples: {e}")

    # ---------- COLUNA DIREITA — Base Aleatória ----------
    with col_dir:
        st.markdown("### 🎲 Base de Dados Aleatória")
        st.caption("Gera uma base realista parametrizável (produtos, clientes, pedidos)")

        with st.form("form_geracao_aleatoria"):
            st.markdown("#### ⚙️ Parâmetros")

            sub_col1, sub_col2 = st.columns(2)

            with sub_col1:
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

            with sub_col2:
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
                    try:
                        resumo = gerar_base_aleatoria.executar(
                            qtd_pedidos=qtd_pedidos,
                            qtd_produtos=qtd_produtos,
                            qtd_clientes=qtd_clientes,
                            data_inicio=data_inicio,
                            data_fim=data_fim,
                            limpar=limpar,
                        )
                        st.success(resumo["mensagem"])
                        st.session_state["base_carregada"] = True
                        st.session_state["confirmar_limpeza"] = False
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar base: {e}")

    # ---------- ESTATÍSTICAS + LIMPEZA ----------
    banco_tem_dados = any(
        get_db()[c].count_documents({}) > 0
        for c in ["produtos", "clientes", "pedidos"]
    )

    if st.session_state.get("base_carregada") or banco_tem_dados:
        _render_estatisticas()
