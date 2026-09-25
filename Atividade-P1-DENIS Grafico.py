# prophet_analise.py
# ------------------------------------------------------------
# Análise de séries temporais com Prophet sobre a base "loja"
#   - Previsão de VENDAS (R$)
#   - Previsão de QUANTIDADE vendida
#   - Previsão de TICKET MÉDIO
#   - Feriados brasileiros incluídos
#   - Gráficos de previsão, componentes e comparativo
# ------------------------------------------------------------
import os
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient
from prophet import Prophet
from prophet.make_holidays import make_holidays_df

# ============================================================
# CONFIGURAÇÃO
# ============================================================
MONGO_URI   = "mongodb://localhost:27017/"
DB_NAME     = "loja"
SAIDA_DIR   = "saida"

PERIODOS_FUTURO = 90        # prever 90 dias à frente
ANO_INICIO = 2026
ANO_FIM    = 2027           # incluir 2027 para os feriados futuros
INTERVALO_CONFIANCA = 0.95

# Status que NÃO entram na conta de vendas
STATUS_EXCLUIDOS = ["Cancelado", "Aguardando pagamento"]

# Cria a pasta de saída
os.makedirs(SAIDA_DIR, exist_ok=True)

# ============================================================
# 1) EXTRAÇÃO DO MONGODB
# ============================================================
print("Conectando ao MongoDB...")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def extrair_serie(pipeline, nome):
    """Executa o pipeline e devolve um DataFrame com ds e y."""
    dados = list(db.pedidos.aggregate(pipeline))
    df = pd.DataFrame(dados)
    if df.empty:
        raise ValueError(f"Série '{nome}' vazia — verifique o MongoDB.")
    df = df.rename(columns={"_id": "ds"})
    df["ds"] = pd.to_datetime(df["ds"])
    df["y"]  = df["y"].astype(float)
    df = df.sort_values("ds").reset_index(drop=True)
    print(f"  {nome}: {len(df)} dias, de {df['ds'].min().date()} a {df['ds'].max().date()}")
    return df


# ---------- Série 1: VALOR (R$) ----------
print("Extraindo séries...")
df_valor = extrair_serie([
    { "$match": { "status_pedido": { "$nin": STATUS_EXCLUIDOS } } },
    { "$group": {
        "_id": { "$dateToString": { "format": "%Y-%m-%d", "date": "$data_pedido" } },
        "y": { "$sum": "$valor_pago" }
    }},
    { "$sort": { "_id": 1 } },
], "valor")

# ---------- Série 2: QUANTIDADE ----------
df_qtd = extrair_serie([
    { "$match": { "status_pedido": { "$nin": STATUS_EXCLUIDOS } } },
    { "$unwind": "$itens" },
    { "$group": {
        "_id": { "$dateToString": { "format": "%Y-%m-%d", "date": "$data_pedido" } },
        "y": { "$sum": "$itens.quantidade" }
    }},
    { "$sort": { "_id": 1 } },
], "quantidade")

# ---------- Série 3: TICKET MÉDIO (valor / quantidade) ----------
df_ticket = df_valor.merge(df_qtd, on="ds", suffixes=("_valor", "_qtd"))
df_ticket["y"] = df_ticket["y_valor"] / df_ticket["y_qtd"]
df_ticket = df_ticket[["ds", "y"]].reset_index(drop=True)
print(f"  ticket:  {len(df_ticket)} dias")

# ---------- Preenchimento de dias faltantes ----------
def preencher_dias(df, fill_value=0):
    """Garante série diária contínua (evita buracos para o Prophet)."""
    return df.set_index("ds").asfreq("D", fill_value=fill_value).reset_index()

df_valor  = preencher_dias(df_valor,  fill_value=0)
df_qtd    = preencher_dias(df_qtd,    fill_value=0)
df_ticket = preencher_dias(df_ticket, fill_value=0)

# ============================================================
# 2) FERIADOS BRASILEIROS
# ============================================================
print("Carregando feriados brasileiros...")
feriados = make_holidays_df(year_list=list(range(ANO_INICIO, ANO_FIM + 1)), country="BR")
print(f"  {len(feriados)} feriados carregados.")


def criar_modelo():
    """Cria um Prophet com configuração padrão para este estudo."""
    return Prophet(
        weekly_seasonality=True,
        yearly_seasonality=True,
        daily_seasonality=False,
        interval_width=INTERVALO_CONFIANCA,
        holidays=feriados,
        changepoint_prior_scale=0.05,
    )


# ============================================================
# 3) TREINAMENTO DOS MODELOS
# ============================================================
print("\nTreinando modelos...")

m_valor  = criar_modelo(); m_valor.fit(df_valor)
m_qtd    = criar_modelo(); m_qtd.fit(df_qtd)
m_ticket = criar_modelo(); m_ticket.fit(df_ticket)

# ============================================================
# 4) PREVISÕES
# ============================================================
print("Gerando previsões...")

def prever(modelo, periodos, nome):
    futuro = modelo.make_future_dataframe(periods=periodos, freq="D")
    prev = modelo.predict(futuro)
    # Salva CSV
    csv_path = os.path.join(SAIDA_DIR, f"previsao_{nome}.csv")
    prev[["ds", "yhat", "yhat_lower", "yhat_upper", "trend"]].to_csv(csv_path, index=False)
    print(f"  {nome}: {len(prev)} linhas → {csv_path}")
    return prev

prev_valor  = prever(m_valor,  PERIODOS_FUTURO, "valor")
prev_qtd    = prever(m_qtd,    PERIODOS_FUTURO, "qtd")
prev_ticket = prever(m_ticket, PERIODOS_FUTURO, "ticket")

# ============================================================
# 5) GRÁFICOS INDIVIDUAIS
# ============================================================
print("\nGerando gráficos individuais...")


def gravar_graficos(modelo, previsao, df_original, titulo, prefixo, unidade):
    # 5.1 — Previsão
    fig1 = modelo.plot(previsao)
    fig1.suptitle(f"{titulo} — Previsão próximos {PERIODOS_FUTURO} dias", fontsize=13)
    plt.xlabel("Data")
    plt.ylabel(unidade)

    # Linha vertical marcando o "hoje"
    ax = fig1.gca()
    ax.axvline(df_original["ds"].max(), color="red", linestyle="--", alpha=0.7, label="Último dado real")
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(os.path.join(SAIDA_DIR, f"{prefixo}_previsao.png"), dpi=120)
    plt.close(fig1)

    # 5.2 — Componentes
    fig2 = modelo.plot_components(previsao)
    fig2.suptitle(f"{titulo} — Componentes", fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(SAIDA_DIR, f"{prefixo}_componentes.png"), dpi=120)
    plt.close(fig2)


gravar_graficos(m_valor,  prev_valor,  df_valor,  "Vendas (R$)",       "01_valor",  "R$")
gravar_graficos(m_qtd,    prev_qtd,    df_qtd,    "Quantidade vendida","03_qtd",    "unidades")
gravar_graficos(m_ticket, prev_ticket, df_ticket, "Ticket médio (R$/un)","05_ticket","R$/un")

# ============================================================
# 6) GRÁFICO COMPARATIVO — TREND DE VALOR × QUANTIDADE
# ============================================================
print("Gerando comparativo de trends...")

# Extrai só os trends do período treinado (periods=0 = só o que já existe)
t_valor = m_valor.predict(m_valor.make_future_dataframe(periods=0))[["ds", "trend"]].copy()
t_qtd   = m_qtd.predict(m_qtd.make_future_dataframe(periods=0))[["ds", "trend"]].copy()

# Normaliza (divide pela média) para poder plotar no mesmo eixo
t_valor["trend_norm"] = t_valor["trend"] / t_valor["trend"].mean()
t_qtd["trend_norm"]   = t_qtd["trend"]   / t_qtd["trend"].mean()

fig_cmp, ax = plt.subplots(figsize=(12, 5))
ax.plot(t_valor["ds"], t_valor["trend_norm"], label="Valor (R$)",  linewidth=2, color="tab:blue")
ax.plot(t_qtd["ds"],   t_qtd["trend_norm"],   label="Quantidade",  linewidth=2, color="tab:orange", linestyle="--")
ax.axhline(1.0, color="gray", linestyle=":", alpha=0.6)
ax.set_title("Comparativo de tendências: Valor × Quantidade (normalizado)")
ax.set_xlabel("Data")
ax.set_ylabel("Tendência normalizada (média = 1)")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(SAIDA_DIR, "07_comparativo_trends.png"), dpi=120)
plt.close(fig_cmp)

# ============================================================
# 7) GRÁFICO COMPARATIVO COMPLETO — 3 SÉRIES NORMALIZADAS
# ============================================================
print("Gerando comparativo completo...")

t_ticket = m_ticket.predict(m_ticket.make_future_dataframe(periods=0))[["ds", "trend"]].copy()
t_ticket["trend_norm"] = t_ticket["trend"] / t_ticket["trend"].mean()

fig_cmp2, ax2 = plt.subplots(figsize=(12, 5))
ax2.plot(t_valor["ds"],  t_valor["trend_norm"],  label="Valor (R$)",       linewidth=2, color="tab:blue")
ax2.plot(t_qtd["ds"],    t_qtd["trend_norm"],    label="Quantidade",       linewidth=2, color="tab:orange", linestyle="--")
ax2.plot(t_ticket["ds"], t_ticket["trend_norm"], label="Ticket médio",     linewidth=2, color="tab:green",  linestyle="-.")
ax2.axhline(1.0, color="gray", linestyle=":", alpha=0.6)
ax2.set_title("Comparativo de tendências: Valor × Quantidade × Ticket médio (normalizado)")
ax2.set_xlabel("Data")
ax2.set_ylabel("Tendência normalizada (média = 1)")
ax2.legend()
plt.tight_layout()
plt.savefig(os.path.join(SAIDA_DIR, "08_comparativo_completo.png"), dpi=120)
plt.close(fig_cmp2)

# ============================================================
# 8) BACKTEST SIMPLES (previsão vs. real nos últimos 30 dias)
# ============================================================
print("\nRodando backtest (últimos 30 dias)...")

def backtest(df, nome):
    corte = df["ds"].max() - pd.Timedelta(days=30)
    treino = df[df["ds"] <= corte]
    teste  = df[df["ds"] > corte].copy()

    if len(treino) < 60 or len(teste) < 10:
        print(f"  {nome}: dados insuficientes para backtest.")
        return None

    m = criar_modelo()
    m.fit(treino)
    fut = m.make_future_dataframe(periods=len(teste), freq="D")
    prev = m.predict(fut)

    resultado = teste.merge(prev[["ds", "yhat"]], on="ds", how="left")

    # Filtra dias com valor real muito baixo (evita explosão do MAPE)
    resultado_valido = resultado[resultado["y"] > 1].copy()

    if resultado_valido.empty:
        print(f"  {nome}: nenhum dia válido para MAPE.")
        mape = None
    else:
        mape = ((resultado_valido["y"] - resultado_valido["yhat"]).abs()
                / resultado_valido["y"]).mean() * 100

    # Métricas absolutas (sempre válidas)
    mae  = (resultado["y"] - resultado["yhat"]).abs().mean()
    rmse = ((resultado["y"] - resultado["yhat"]) ** 2).mean() ** 0.5

    # sMAPE (nunca explode)
    smape = (2 * (resultado["y"] - resultado["yhat"]).abs()
             / (resultado["y"].abs() + resultado["yhat"].abs() + 1e-9)).mean() * 100

    # Erro percentual sobre o TOTAL do período
    total_real = resultado["y"].sum()
    total_prev = resultado["yhat"].sum()
    erro_total = abs(total_real - total_prev) / total_real * 100 if total_real else None

    # Log
    print(f"\n  {nome}:")
    print(f"    MAPE (dias > 1):   {mape:.2f}%" if mape else f"    MAPE:              N/A")
    print(f"    sMAPE:             {smape:.2f}%")
    print(f"    MAE:               {mae:.2f}")
    print(f"    RMSE:              {rmse:.2f}")
    print(f"    Erro no total:     {erro_total:.2f}%" if erro_total else "")

    # Gráfico
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(teste["ds"], teste["y"],         label="Real",     marker="o", color="black")
    ax.plot(resultado["ds"], resultado["yhat"], label="Previsto", marker="x", color="red", linestyle="--")
    titulo_mape = f"MAPE = {mape:.2f}%" if mape else "MAPE = N/A"
    ax.set_title(f"Backtest — {nome} (últimos 30 dias) | sMAPE = {smape:.2f}% | {titulo_mape}")
    ax.set_xlabel("Data")
    ax.set_ylabel(nome)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(SAIDA_DIR, f"09_backtest_{nome.lower().replace(' ', '_')}.png"), dpi=120)
    plt.close(fig)
    return {"mape": mape, "smape": smape, "mae": mae, "rmse": rmse, "erro_total": erro_total}

backtest(df_valor,  "Valor (R$)")
backtest(df_qtd,    "Quantidade")
backtest(df_ticket, "Ticket médio")

# ============================================================
# 9) RESUMO FINAL
# ============================================================
print("\n=== RESUMO ===")
print(f"Valor  — últ. real: R$ {df_valor['y'].iloc[-1]:,.2f} | prev. +{PERIODOS_FUTURO}d: R$ {prev_valor['yhat'].iloc[-1]:,.2f}")
print(f"Qtde   — últ. real: {df_qtd['y'].iloc[-1]:.0f} un. | prev. +{PERIODOS_FUTURO}d: {prev_qtd['yhat'].iloc[-1]:.0f} un.")
print(f"Ticket — últ. real: R$ {df_ticket['y'].iloc[-1]:,.2f} | prev. +{PERIODOS_FUTURO}d: R$ {prev_ticket['yhat'].iloc[-1]:,.2f}")
print(f"\nTodos os arquivos foram salvos em: {os.path.abspath(SAIDA_DIR)}")

client.close()
print("Concluído.")