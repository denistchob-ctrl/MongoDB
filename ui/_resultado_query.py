# ui/_resultado_query.py
# ------------------------------------------------------------
# Componente visual comum para exibir resultado de query:
#   - caixa com o comando
#   - caixa com a explicação (opcional)
#   - contador "Retornou xxx linhas"
#   - tabela com até 5 linhas
# ------------------------------------------------------------
import json
from datetime import datetime, date
from bson import ObjectId
import pandas as pd
import streamlit as st


# ============================================================
# HELPERS
# ============================================================
def _to_serializable(obj):
    """Converte datetime / ObjectId em strings para o pandas/JSON."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_serializable(i) for i in obj]
    return obj


def _normalizar_amostra(amostra: list) -> pd.DataFrame:
    """
    Converte lista de dicts (possivelmente com subdocumentos/arrays) em
    um DataFrame achatado, mostrando subdocumentos como JSON compacto.
    """
    if not amostra:
        return pd.DataFrame()

    linhas = []
    for doc in amostra:
        doc_serial = _to_serializable(doc)
        linha = {}
        for k, v in doc_serial.items():
            if isinstance(v, (dict, list)):
                linha[k] = json.dumps(v, ensure_ascii=False)
            else:
                linha[k] = v
        linhas.append(linha)

    return pd.DataFrame(linhas)


# ============================================================
# COMPONENTE PRINCIPAL
# ============================================================
def render_resultado(resultado: dict, mostrar_explicacao: str | None = None):
    """
    Parâmetros
    ----------
    resultado : dict
        Retorno de executar() — deve conter 'total' (int) e 'amostra' (list[dict]).
    mostrar_explicacao : str | None
        Texto opcional a ser exibido em destaque (explicação do operador).
    """
    total = resultado["total"]
    amostra = resultado["amostra"]

    # ---------- Caixa de contador ----------
    if total == 0:
        st.warning("⚠️ **Retornou 0 linhas.** Nenhum documento corresponde ao filtro.")
    elif total == 1:
        st.success("✅ **Retornou 1 linha.**")
    else:
        st.success(f"✅ **Retornou {total} linhas.**")

    # ---------- Explicação (se houver) ----------
    if mostrar_explicacao:
        st.markdown("#### 📖 Explicação")
        st.info(mostrar_explicacao)

    # ---------- Tabela ----------
    st.markdown("#### 📋 Resultado (até 5 linhas)")

    if not amostra:
        st.info("Sem dados para exibir.")
        return

    df = _normalizar_amostra(amostra)

    st.dataframe(
        df,
        use_container_width=True,
        height=min(250, 40 + 35 * len(df)),
    )

    if total > len(amostra):
        st.caption(f"Mostrando as primeiras {len(amostra)} de {total} linhas.")

