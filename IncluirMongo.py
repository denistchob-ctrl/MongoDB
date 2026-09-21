import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# 1. Conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["loja"]
vendas = db["vendas"]

# 2. Definição do catálogo baseado no seu schema
catalogo = [
    {
        "produto": "Notebook",
        "categoria": "Eletrônicos",
        "preco_base": 3500
    },
    {
        "produto": "Smartphone",
        "categoria": "Eletrônicos",
        "preco_base": 2000
    },
    {
        "produto": "Cadeira Gamer",
        "categoria": "Móveis",
        "preco_base": 800
    },
    {
        "produto": "Monitor",
        "categoria": "Eletrônicos",
        "preco_base": 1200
    }
]

# 3. Gerar 100 registros com variação entre 01/08/2026 e 15/09/2026
data_inicio = datetime(2026, 8, 1)
novos_registros = []

for _ in range(100):
    # Seleciona um item do catálogo
    item = random.choice(catalogo)
    
    # Sorteia uma data entre 01/08/2026 e 15/09/2026 (46 dias)
    dias_aleatorios = random.randint(0, 45)
    data_venda = data_inicio + timedelta(days=dias_aleatorios)
    
    # Sorteia quantidade (entre 1 e 5 unidades)
    qtd = random.randint(1, 5)
    
    # Pequena variação ocasional no preço (ex: promoções ou descontos)
    fator_preco = random.choice([1.0, 1.0, 1.0, 0.95, 0.90]) 
    preco_final = int(item["preco_base"] * fator_preco)
    
    novos_registros.append({
        "produto": item["produto"],
        "categoria": item["categoria"],
        "preco": preco_final,
        "quantidade": qtd,
        "data": data_venda.strftime("%Y-%m-%d")
    })

# Ordenar por data antes de inserir
novos_registros.sort(key=lambda x: x["data"])

# 4. Inserir no banco de dados
vendas.insert_many(novos_registros)
print(f"Sucesso! {len(novos_registros)} novos registros foram inseridos no MongoDB.")