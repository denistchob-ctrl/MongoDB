# Conexão com MongoDB
from datetime import datetime, timedelta            
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["loja"]
vendas = db["vendas"]

hoje = datetime.now()
limite = hoje - timedelta(days=30)
print(f"Hoje: ({hoje})")
print(f"Limite: ({limite})")
print("-"*100)
# para pegar um intervalo de 30 a partir da data do sistema

pipeline = [
    {
        "$addFields": {
            "data_convertida": {
                "$dateFromString": {"dateString": "$data", "format": "%Y-%m-%d"}
            }
        }
    },
    {
        "$match": {
            "data_convertida": {"$gte": limite}
        }
    },
    {
        "$group": {
            "_id": "$produto",
            "total_vendido": {"$sum": {"$multiply": ["$preco", "$quantidade"]}},
            "qtd_itens": {"$sum": "$quantidade"}
        }
    },
    {"$sort": {"total_vendido": -1}}
]

resultados = list(vendas.aggregate(pipeline))

for r in resultados:
    print(f"Produto: {r['_id']}")
    print(f"Total vendido: R$ {r['total_vendido']}")
    print(f"Quantidade de itens: {r['qtd_itens']}")
    print("-" * 30)