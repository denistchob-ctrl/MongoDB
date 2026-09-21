from pymongo import MongoClient
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# EXEMPLO 1
# # Exemplo de dados fictícios
# df = pd.DataFrame({
#     'ds': pd.date_range(start='2026-08-01', periods=60, freq='D'),
#     'y': [100 + i*2 + (10 if i%7==0 else 0) for i in range(60)]  # inclui um padrão semanal
# })

# # Modelo 1: padrão (weekly_seasonality=True)
# model_weekly = Prophet()
# model_weekly.fit(df)
# future_weekly = model_weekly.make_future_dataframe(periods=30)
# forecast_weekly = model_weekly.predict(future_weekly)
# fig1 = model_weekly.plot(forecast_weekly)

# # Modelo 2: sem sazonalidade semanal
# model_no_weekly = Prophet(weekly_seasonality=False)
# model_no_weekly.fit(df)
# future_no_weekly = model_no_weekly.make_future_dataframe(periods=30)
# forecast_no_weekly = model_no_weekly.predict(future_no_weekly)
# fig2 = model_no_weekly.plot(forecast_no_weekly)

# EXEMPLO 2
# 1. Conexão com MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["loja"]
vendas = db["vendas"]

# 2. Extraindo dados
dados = list(vendas.find({}, {"_id": 0, "data": 1, "preco": 1, "quantidade": 1}))
df = pd.DataFrame(dados)

# 3. Preparando dados para Prophet
df["data"] = pd.to_datetime(df["data"])
df["total_venda"] = df["preco"] * df["quantidade"]

# Prophet exige colunas 'ds' (datas) e 'y' (valores)
df_prophet = df.rename(columns={"data": "ds", "total_venda": "y"})

# 4. Criando e treinando o modelo
modelo = Prophet()
modelo.fit(df_prophet)

# 5. Criando dataframe futuro (previsão para 30 dias)
futuro = modelo.make_future_dataframe(periods=30)
previsao = modelo.predict(futuro)

# 6. Visualização
# fig1 = modelo.plot(previsao)
# plt.show()

# fig2 = modelo.plot_components(previsao)
# plt.show()

#EXEMPLO 3
from prophet.make_holidays import make_holidays_df

# Criar dataframe de feriados brasileiros
feriados = pd.DataFrame({
    'holiday': 'feriado',
    'ds': pd.to_datetime([
        "2026-01-01",  # Ano Novo
        "2026-02-17",  # Carnaval
        "2026-04-21",  # Tiradentes
        "2026-05-01",  # Dia do Trabalho
        "2026-09-07",  # Independência
        "2026-12-25"   # Natal
    ]),
    'lower_window': 0,
    'upper_window': 1
})

# modelo = Prophet(holidays=feriados)
# modelo.fit(df_prophet)

modelo = Prophet(holidays=feriados)
modelo.fit(df_prophet)

# --- Adicione os comandos abaixo para ver o resultado ---
futuro3 = modelo.make_future_dataframe(periods=30)
previsao3 = modelo.predict(futuro3)

fig3 = modelo.plot(previsao3)
plt.show()

fig4 = modelo.plot_components(previsao3)
plt.show()