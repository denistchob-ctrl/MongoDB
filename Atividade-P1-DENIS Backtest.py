# backtest_granularidade.py
# ------------------------------------------------------------
# Backtest do Prophet em 3 granularidades (D, W, M) x 3 séries
#   - Valor (R$)
#   - Quantidade
#   - Ticket médio
#
# Gera:
#   - Gráfico comparativo de sMAPE por série
#   - Heatmap consolidado
#   - Gráficos individuais de cada backtest
#   - CSV com todos os resultados
# ------------------------------------------------------------
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from prophet import Prophet
from prophet.make_holidays import make_holidays_df

# ============================================================
# CONFIGURAÇÃO
# ============================================================
MONGO_URI   = "mongodb://localhost:27017/"
DB_NAME     = "loja"
SAIDA_DIR   = "saida_backtest"

STATUS_EXCLUIDOS = ["Cancelado", "Aguardando pagamento"]

ANO_INICIO = 2026
ANO_FIM    = 2027

# Horizonte do backtest em cada granularidade
HORIZONTE = {
    "diario":  30,   # 30 dias
    "semanal": 4,    # 4 semanas (~28 dias)
    "mensal":  1,    # 1 mês
}

# Frequência do Prophet por granularidade
FREQ = {
    "diario":  "D",
    "semanal": "W",
    "mensal":  "MS",   # month start
}

os.makedirs(SAIDA_DIR, exist_ok=True)

# ============================================================
# 1) EXTRAÇÃO DO MONGODB
# ============================================================
print("Conectando ao MongoDB...")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def extrair_serie(pipeline, nome):
    dados = list(db.pedidos.aggregate(pipeline))
    df = pd.DataFrame(dados)
    if df.empty:
        raise ValueError(f"Série '{nome}' vazia.")
    df = df.rename(columns={"_id": "ds"})
    df["ds"] = pd.to_datetime(df["ds"])
    df["y"]  = df["y"].astype(float)
    return df.sort_values("ds").reset_index(drop=True)


print("Extraindo séries...")
df_valor = extrair_serie([
    { "$match": { "status_pedido": { "$nin": STATUS_EXCLUIDOS } } },
    { "$group": {
        "_id": { "$dateToString": { "format": "%Y-%m-%d", "date": "$data_pedido" } },
        "y": { "$sum": "$valor_pago" }
    }},
    { "$sort": { "_id": 1 } },
], "valor")

df_qtd = extrair_serie([
    { "$match": { "status_pedido": { "$nin": STATUS_EXCLUIDOS } } },
    { "$unwind": "$itens" },
    { "$group": {
        "_id": { "$dateToString": { "format": "%Y-%m-%d", "date": "$data_pedido" } },
        "y": { "$sum": "$itens.quantidade" }
    }},
    { "$sort": { "_id": 1 } },
], "quantidade")

df_ticket = df_valor.merge(df_qtd, on="ds", suffixes=("_valor", "_qtd"))
df_ticket["y"] = df_ticket["y_valor"] / df_ticket["y_qtd"]
df_ticket = df_ticket[["ds", "y"]].reset_index(drop=True)


# ---------- Preenche dias faltantes ----------
def preencher_diario(df):
    return df.set_index("ds").asfreq("D", fill_value=0).reset_index()


df_valor  = preencher_diario(df_valor)
df_qtd    = preencher_diario(df_qtd)
df_ticket = preencher_diario(df_ticket)


# ---------- Reamostragem por granularidade ----------
def reagregar(df_diario, granularidade):
    """
    Converte a série diária para a granularidade desejada,
    usando uma data-âncora explícita (segunda-feira para semanal,
    dia 1 para mensal).
    """
    if granularidade == "diario":
        return df_diario.copy()

    df = df_diario.copy()
    df["ds"] = pd.to_datetime(df["ds"])

    if granularidade == "semanal":
        # Âncora: segunda-feira da semana
        df["ds_ancora"] = df["ds"] - pd.to_timedelta(df["ds"].dt.weekday, unit="D")
    elif granularidade == "mensal":
        # Âncora: primeiro dia do mês
        df["ds_ancora"] = df["ds"].values.astype("datetime64[M]")
    else:
        raise ValueError(f"Granularidade inválida: {granularidade}")

    agg = df.groupby("ds_ancora").agg({"y": "sum"}).reset_index()
    agg = agg.rename(columns={"ds_ancora": "ds"})
    return agg



# ============================================================
# 2) FERIADOS
# ============================================================
print("Carregando feriados brasileiros...")
feriados = make_holidays_df(year_list=list(range(ANO_INICIO, ANO_FIM + 1)), country="BR")


def criar_modelo(granularidade):
    """Cria Prophet com sazonalidades apropriadas à granularidade."""
    if granularidade == "diario":
        return Prophet(
            weekly_seasonality=True,
            yearly_seasonality=True,
            daily_seasonality=False,
            holidays=feriados,
            interval_width=0.95,
            changepoint_prior_scale=0.05,
        )
    if granularidade == "semanal":
        return Prophet(
            weekly_seasonality=False,   # não faz sentido em série semanal
            yearly_seasonality=True,
            daily_seasonality=False,
            holidays=feriados,
            interval_width=0.95,
            changepoint_prior_scale=0.05,
        )
    # mensal
    return Prophet(
        weekly_seasonality=False,
        yearly_seasonality=False,       # poucos pontos mensais
        daily_seasonality=False,
        holidays=feriados,
        interval_width=0.95,
        changepoint_prior_scale=0.05,
    )


# ============================================================
# 3) FUNÇÃO DE BACKTEST
# ============================================================
def calcular_smape(real, prev):
    """sMAPE — varia de 0 a 200%, nunca explode."""
    numerador   = 2 * np.abs(real - prev)
    denominador = np.abs(real) + np.abs(prev) + 1e-9
    return np.mean(numerador / denominador) * 100


def calcular_mape(real, prev):
    """MAPE — só sobre dias com real > 1 (evita explosão)."""
    mask = real > 1
    if mask.sum() == 0:
        return np.nan
    return np.mean(np.abs(real[mask] - prev[mask]) / real[mask]) * 100


def backtest(df, granularidade, nome, gerar_grafico=True):
    """
    Backtest corrigido:
      - Gera a série na granularidade correta
      - Treina/testa com corte proporcional
      - Passa as datas de teste EXPLICITAMENTE ao Prophet
      - Calcula métricas por período E por dia
    """
    # 3.1 — Série na granularidade correta
    df_g = reagregar(df, granularidade)

    # Limite mínimo por granularidade
    minimo = {"diario": 30, "semanal": 10, "mensal": 5}[granularidade]
    if len(df_g) < minimo:
        print(f"  {nome} [{granularidade}]: poucos pontos ({len(df_g)} < {minimo}). Pulando.")
        return None

    # 3.2 — Horizonte e corte
    horizonte = HORIZONTE[granularidade]

    if granularidade == "diario":
        corte = df_g["ds"].max() - pd.Timedelta(days=horizonte)
    elif granularidade == "semanal":
        corte = df_g["ds"].max() - pd.Timedelta(weeks=horizonte)
    else:  # mensal
        corte = df_g["ds"].max() - pd.DateOffset(months=horizonte)

    treino = df_g[df_g["ds"] <= corte].copy()
    teste  = df_g[df_g["ds"] >  corte].copy()

    if len(treino) < 8 or len(teste) < 1:
        print(f"  {nome} [{granularidade}]: dados insuficientes. Pulando.")
        return None

    # 3.3 — Treina
    m = criar_modelo(granularidade)
    m.fit(treino)

    # 3.4 — Previsão: passa as datas de teste EXPLICITAMENTE
    datas_futuras = pd.DataFrame({"ds": teste["ds"].values})
    prev = m.predict(datas_futuras)

    # 3.5 — Alinha por data
    resultado = teste.merge(prev[["ds", "yhat"]], on="ds", how="inner")

    if resultado.empty:
        print(f"  {nome} [{granularidade}]: merge vazio — verifique as datas.")
        return None

    real = resultado["y"].values
    p    = resultado["yhat"].values

    smape = calcular_smape(real, p)
    mape  = calcular_mape(pd.Series(real), pd.Series(p))

    mae  = np.mean(np.abs(real - p))
    rmse = np.sqrt(np.mean((real - p) ** 2))

    total_real = real.sum()
    total_prev = p.sum()
    erro_total = abs(total_real - total_prev) / total_real * 100 if total_real else np.nan

    # 3.6 — Log
    print(f"  {nome:10s} [{granularidade:7s}]  "
          f"sMAPE={smape:6.2f}%  "
          f"MAPE={mape:6.2f}%  "
          f"MAE={mae:10.2f}  "
          f"ErroTotal={erro_total:6.2f}%  "
          f"(treino={len(treino)}, teste={len(teste)})")

    # 3.7 — Gráfico
    if gerar_grafico:
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.plot(treino["ds"], treino["y"],         label="Treino",    color="lightgray", linewidth=1)
        ax.plot(teste["ds"],  teste["y"],           label="Real",      marker="o", color="black")
        ax.plot(resultado["ds"], resultado["yhat"], label="Previsto",  marker="x",
                color="red", linestyle="--")
        ax.axvline(corte, color="blue", linestyle=":", alpha=0.6, label="Corte treino/teste")
        ax.set_title(f"Backtest — {nome} ({granularidade}) | sMAPE = {smape:.2f}%")
        ax.set_xlabel("Data")
        ax.set_ylabel(nome)
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(SAIDA_DIR, f"backtest_{nome.lower()}_{granularidade}.png"), dpi=110)
        plt.close(fig)

    return {
        "serie":         nome,
        "granularidade": granularidade,
        "smape":         smape,
        "mape":          mape,
        "mae":           mae,
        "rmse":          rmse,
        "erro_total":    erro_total,
        "n_treino":      len(treino),
        "n_teste":       len(teste),
    }

def backtest_agregado(df_diario, granularidade, nome, gerar_grafico=True):
    """
    Treina o Prophet em série DIÁRIA e agrega a previsão
    para a granularidade desejada. Evita bugs de frequência.
    """
    # 1) Série diária (com dias faltantes preenchidos)
    df_g = df_diario.copy()
    df_g["ds"] = pd.to_datetime(df_g["ds"])

    # 2) Corte treino/teste na série DIÁRIA
    horizonte_dias = {
        "diario":  30,
        "semanal": 28,     # 4 semanas
        "mensal":  30,     # 1 mês (30 dias)
    }[granularidade]

    corte = df_g["ds"].max() - pd.Timedelta(days=horizonte_dias)

    treino_d = df_g[df_g["ds"] <= corte].copy()
    teste_d  = df_g[df_g["ds"] >  corte].copy()

    if len(treino_d) < 60 or len(teste_d) < 5:
        print(f"  {nome} [{granularidade}]: dados insuficientes. Pulando.")
        return None

    # 3) Treina na série DIÁRIA
    m = criar_modelo("diario")
    m.fit(treino_d)

    # 4) Prevê nas datas do teste
    datas_teste = pd.DataFrame({"ds": teste_d["ds"].values})
    prev_d = m.predict(datas_teste)

    # 5) Junta previsto com real (ambos diários)
    merged = teste_d.merge(prev_d[["ds", "yhat"]], on="ds", how="inner")

    # 6) Agregação — feita na série DIÁRIA já preenchida
    if granularidade == "diario":
        agg = merged.copy()

    elif granularidade == "semanal":
        merged["ds_ancora"] = merged["ds"] - pd.to_timedelta(merged["ds"].dt.weekday, unit="D")

        if nome == "ticket":
            # Ticket: média ponderada (soma valor / soma quantidade)
            # Para isso precisamos das duas séries separadas
            valor_d = df_valor.set_index("ds")["y"]
            qtd_d   = df_qtd.set_index("ds")["y"]

            agg = merged.groupby("ds_ancora").apply(
                lambda g: pd.Series({
                    "y":    valor_d.reindex(g["ds"]).sum() / max(qtd_d.reindex(g["ds"]).sum(), 1e-9),
                    "yhat": g["yhat"].sum() / max(qtd_d.reindex(g["ds"]).sum(), 1e-9),
                })
            ).reset_index()
        else:
            agg = merged.groupby("ds_ancora").agg({"y": "sum", "yhat": "sum"}).reset_index()

        agg = agg.rename(columns={"ds_ancora": "ds"})

    elif granularidade == "mensal":
        merged["ds_ancora"] = merged["ds"].values.astype("datetime64[M]")

        if nome == "ticket":
            valor_d = df_valor.set_index("ds")["y"]
            qtd_d   = df_qtd.set_index("ds")["y"]

            agg = merged.groupby("ds_ancora").apply(
                lambda g: pd.Series({
                    "y":    valor_d.reindex(g["ds"]).sum() / max(qtd_d.reindex(g["ds"]).sum(), 1e-9),
                    "yhat": g["yhat"].sum() / max(qtd_d.reindex(g["ds"]).sum(), 1e-9),
                })
            ).reset_index()
        else:
            agg = merged.groupby("ds_ancora").agg({"y": "sum", "yhat": "sum"}).reset_index()

        agg = agg.rename(columns={"ds_ancora": "ds"})

    # 7) Métricas
    real = agg["y"].values
    p    = agg["yhat"].values

    smape = calcular_smape(real, p)
    mape  = calcular_mape(pd.Series(real), pd.Series(p))

    mae  = np.mean(np.abs(real - p))
    rmse = np.sqrt(np.mean((real - p) ** 2))

    total_real = real.sum()
    total_prev = p.sum()
    erro_total = abs(total_real - total_prev) / total_real * 100 if total_real else np.nan

    print(f"  {nome:10s} [{granularidade:7s}]  "
          f"sMAPE={smape:6.2f}%  MAPE={mape:6.2f}%  "
          f"MAE={mae:10.2f}  ErroTotal={erro_total:5.2f}%  "
          f"(n_agg={len(agg)})")

    # 8) Gráfico
    if gerar_grafico:
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.plot(treino_d["ds"], treino_d["y"], label="Treino", color="lightgray", linewidth=1)
        ax.plot(agg["ds"], agg["y"],      label="Real",     marker="o", color="black")
        ax.plot(agg["ds"], agg["yhat"],   label="Previsto", marker="x",
                color="red", linestyle="--")
        ax.axvline(corte, color="blue", linestyle=":", alpha=0.6, label="Corte treino/teste")
        ax.set_title(f"Backtest — {nome} ({granularidade}) | sMAPE = {smape:.2f}%")
        ax.set_xlabel("Data")
        ax.set_ylabel(nome)
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(SAIDA_DIR, f"backtest_{nome.lower()}_{granularidade}.png"), dpi=110)
        plt.close(fig)

    return {
        "serie":         nome,
        "granularidade": granularidade,
        "smape":         smape,
        "mape":          mape,
        "mae":           mae,
        "rmse":          rmse,
        "erro_total":    erro_total,
        "n_treino":      len(treino_d),
        "n_teste":       len(agg),
    }

# ============================================================
# 4) EXECUTA TODOS OS BACKTESTS
# ============================================================
print("\n=== EXECUTANDO BACKTESTS ===")

series = {
    "valor":   df_valor,
    "qtd":     df_qtd,
    "ticket":  df_ticket,
}

granularidades = ["diario", "semanal", "mensal"]

resultados = []
for nome_serie, df in series.items():
    for g in granularidades:
        r = backtest_agregado(df, g, nome_serie, gerar_grafico=True)
        if r:
            resultados.append(r)

# for nome_serie, df in series.items():
#     for g in granularidades:
#         r = backtest(df, g, nome_serie, gerar_grafico=True)
#         if r:
#             resultados.append(r)

df_resultados = pd.DataFrame(resultados)
df_resultados.to_csv(os.path.join(SAIDA_DIR, "resultados_backtest.csv"), index=False)
print(f"\nResultados salvos em: {SAIDA_DIR}/resultados_backtest.csv")


# ============================================================
# 5) GRÁFICO COMPARATIVO DE sMAPE POR SÉRIE
# ============================================================
print("\nGerando gráficos comparativos...")

for nome_serie in series.keys():
    sub = df_resultados[df_resultados["serie"] == nome_serie]
    if sub.empty:
        continue

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(sub["granularidade"], sub["smape"],
                  color=["#d62728", "#ff7f0e", "#2ca02c"])

    # Rótulos em cima das barras
    for bar, val in zip(bars, sub["smape"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val:.1f}%", ha="center", va="bottom", fontweight="bold")

    ax.set_title(f"sMAPE por granularidade — {nome_serie.upper()}")
    ax.set_xlabel("Granularidade")
    ax.set_ylabel("sMAPE (%)")
    ax.set_ylim(0, max(sub["smape"]) * 1.25)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(SAIDA_DIR, f"comparativo_smape_{nome_serie}.png"), dpi=110)
    plt.close(fig)


# ============================================================
# 6) HEATMAP CONSOLIDADO
# ============================================================
print("Gerando heatmap consolidado...")

# Pivot: linhas = série, colunas = granularidade, valores = sMAPE
pivot = df_resultados.pivot(index="serie", columns="granularidade", values="smape")
# Reordena as colunas
pivot = pivot[["diario", "semanal", "mensal"]]

fig, ax = plt.subplots(figsize=(8, 4))
sns.heatmap(
    pivot,
    annot=True,
    fmt=".1f",
    cmap="RdYlGn_r",     # vermelho = ruim, verde = bom
    cbar_kws={"label": "sMAPE (%)"},
    linewidths=0.5,
    ax=ax,
)
ax.set_title("sMAPE consolidado — Série × Granularidade")
ax.set_xlabel("Granularidade")
ax.set_ylabel("Série")
plt.tight_layout()
plt.savefig(os.path.join(SAIDA_DIR, "heatmap_smape_consolidado.png"), dpi=120)
plt.close(fig)


# ============================================================
# 7) GRÁFICO COMBINADO (linha) — TODAS AS SÉRIES
# ============================================================
print("Gerando gráfico combinado...")

fig, ax = plt.subplots(figsize=(9, 5))
cores = {"valor": "tab:blue", "qtd": "tab:orange", "ticket": "tab:green"}
marcadores = {"valor": "o", "qtd": "s", "ticket": "^"}

for nome_serie in series.keys():
    sub = df_resultados[df_resultados["serie"] == nome_serie].sort_values(
        "granularidade",
        key=lambda s: s.map({"diario": 0, "semanal": 1, "mensal": 2}),
    )
    if sub.empty:
        continue
    ax.plot(sub["granularidade"], sub["smape"],
            marker=marcadores[nome_serie],
            color=cores[nome_serie],
            label=nome_serie.upper(),
            linewidth=2, markersize=10)

ax.set_title("sMAPE por granularidade — Comparativo entre séries")
ax.set_xlabel("Granularidade")
ax.set_ylabel("sMAPE (%)")
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(SAIDA_DIR, "comparativo_series_smape.png"), dpi=120)
plt.close(fig)


# ============================================================
# 8) RESUMO FINAL
# ============================================================
print("\n=== RESUMO ===")
print(df_resultados[["serie", "granularidade", "smape", "mape", "erro_total"]]
      .to_string(index=False))
print(f"\nArquivos gerados em: {os.path.abspath(SAIDA_DIR)}")

client.close()
print("\nConcluído.")