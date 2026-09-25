# Elaborem um banco de dados em MongoDB com um negócio a sua escolha.
# Além do DB e da Collection esse projeto deverá conter pesquisas com pelo menos 70% dos operadores que foram utilizados até a aula de 15-09-26. 
#
# Deverá conter agregações, que sumarizem dados do negócio entregando conhecimento aos administradores. 
#
# Um exemplo com estatisticas de series temporais semelhante ao que foi apresentado na referida aula do dia 15, 
# será um plus consideravel no projeto, se explicado corretamente na apresentação que deve 
# conter todos os participantes da equipe. 
#
# Cada equipe pode ter até 5 participantes e é permitido o trablho individual!

# Objetivos de aprendizagem
# * Projetar um banco de dados em MongoDB para representar um negócio escolhido.
# * Criar e organizar um DB e uma Collection coerentes com o negócio proposto.
# * Aplicar pesquisas usando pelo menos 70% dos operadores estudados até a aula de 15-09-26.
# * Construir agregações que resumam os dados e apoiem a tomada de decisões dos administradores.
# * Explicar corretamente os resultados das pesquisas e das agregações.
# * Desenvolver, como diferencial, um exemplo de estatísticas de séries temporais relacionado ao negócio.

# gerar_pedidos.py
import random
from datetime import datetime, timedelta

from faker import Faker
from pymongo import MongoClient
from pymongo import UpdateOne

# ============================================================
# CONFIGURAÇÃO
# ============================================================
MONGO_URI   = "mongodb://localhost:27017/"
DB_NAME     = "loja"

QTD_PEDIDOS = random.randint(1500, 2000)   # ~1500-2000 pedidos
PCT_JAN_JUN = 0.20                          # 20% jan-jun/2026
PCT_JUL_SET = 0.80                          # 80% jul-set/2026

FAKER_LOCALE = "pt_BR"

# Formas de pagamento e pesos (frequência relativa)
FORMAS_PAGAMENTO = [
    ("Cartão de Crédito", 35),
    ("PIX",               30),
    ("Boleto",            20),
    ("Cartão de Débito",  15),
]

# Status possíveis (todos os que existem no seu dataset)
STATUS_PEDIDO = [
    "Entregue",
    "Em processamento",
    "Enviado",
    "Aguardando pagamento",
    "Cancelado",
]

# ============================================================
# HELPERS
# ============================================================
fake = Faker(FAKER_LOCALE)
random.seed(42)   # reprodutibilidade; remova se quiser aleatoriedade real


def escolher_com_peso(itens_peso):
    """Escolhe um item de uma lista [(valor, peso), ...]."""
    valores = [v for v, _ in itens_peso]
    pesos   = [p for _, p in itens_peso]
    return random.choices(valores, weights=pesos, k=1)[0]


def data_aleatoria_2026():
    """
    Gera data conforme a regra:
      - 20% entre 2026-01-01 e 2026-06-30
      - 80% entre 2026-07-01 e 2026-09-30
    """
    if random.random() < PCT_JAN_JUN:
        inicio = datetime(2026, 1, 1)
        fim    = datetime(2026, 6, 30)
    else:
        inicio = datetime(2026, 7, 1)
        fim    = datetime(2026, 9, 30)

    delta = (fim - inicio).days
    return inicio + timedelta(days=random.randint(0, delta))


# ============================================================
# CONEXÃO
# ============================================================
client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

# ============================================================
# 1) GARANTIR QUE EXISTEM PRODUTOS E CLIENTES SUFICIENTES
# ============================================================
print("Verificando produtos e clientes existentes...")

# ---------- PRODUTOS EXTRA (caso queira ampliar o catálogo) ----------
produtos_extras = [
    # (descricao, unidade, preco_custo, preco_venda, qtde_estoque, categoria, tags)
    ("Placa de Vídeo RTX 4060",      "UN", 2200.00, 2899.00, 12, "placa_video",  ["informatica", "gpu", "nvidia"]),
    ("Placa de Vídeo RTX 4070",      "UN", 3500.00, 4499.00,  8, "placa_video",  ["informatica", "gpu", "nvidia"]),
    ("Memória RAM DDR5 16GB",        "UN",  320.00,  479.00, 35, "memoria",      ["informatica", "ram", "ddr5"]),
    ("Memória RAM DDR4 8GB",         "UN",  150.00,  229.00, 60, "memoria",      ["informatica", "ram", "ddr4"]),
    ("Placa-Mãe B650M",              "UN",  750.00, 1049.00, 18, "placa_mae",    ["informatica", "motherboard", "amd"]),
    ("Placa-Mãe Z790",               "UN", 1200.00, 1699.00, 10, "placa_mae",    ["informatica", "motherboard", "intel"]),
    ("Water Cooler 240mm",           "UN",  380.00,  559.00, 22, "cooler",       ["informatica", "cooler", "water"]),
    ("SSD NVMe 2TB",                 "UN",  750.00, 1049.00, 15, "armazenamento",["informatica", "ssd", "nvme"]),
    ("HD Externo 4TB",               "UN",  480.00,  699.00, 20, "armazenamento",["informatica", "hd", "externo"]),
    ("Webcam Full HD Logitech",      "UN",  180.00,  299.00, 25, "periferico",   ["informatica", "webcam", "logitech"]),
    ("Headset HyperX Cloud II",      "UN",  320.00,  499.00, 30, "Audio e Video",["informatica", "headset", "hyperx"]),
    ("Microfone Condensador USB",    "UN",  250.00,  399.00, 18, "Audio e Video",["informatica", "microfone", "usb"]),
    ("Impressora Multifuncional HP", "UN",  650.00,  949.00, 12, "impressora",   ["informatica", "impressora", "hp"]),
    ("Roteador Wi-Fi 6 TP-Link",     "UN",  280.00,  429.00, 28, "rede",         ["informatica", "roteador", "wifi"]),
    ("Switch 8 portas Gigabit",      "UN",  180.00,  289.00, 20, "rede",         ["informatica", "switch", "rede"]),
    ("Nobreak 1500VA",               "UN",  650.00,  949.00, 14, "energia",      ["informatica", "nobreak", "energia"]),
    ("Hub USB-C 7 em 1",             "UN",   90.00,  159.00, 40, "periferico",   ["informatica", "hub", "usb-c"]),
    ("Suporte Monitor Articulado",   "UN",  120.00,  199.00, 25, "movel",        ["informatica", "suporte", "monitor"]),
    ("Mousepad Gamer XL",            "UN",   45.00,   89.00, 80, "periferico",   ["informatica", "mousepad", "gamer"]),
    ("Cabo DisplayPort 2m",          "UN",   35.00,   69.00, 90, "cabo",         ["informatica", "cabo", "displayport"]),
]

produtos_existentes = list(db.produtos.find({}, {"_id": 0, "codigo": 1}))
codigos_existentes  = {p["codigo"] for p in produtos_existentes}
proximo_codigo      = (max(codigos_existentes) + 1) if codigos_existentes else 1

# Só insere produtos extras se o catálogo estiver pequeno (< 30 produtos)
if len(codigos_existentes) < 30:
    novos_produtos = []
    for desc, un, custo, venda, estoque, categoria, tags in produtos_extras:
        if proximo_codigo in codigos_existentes:
            proximo_codigo += 1
            continue
        novos_produtos.append({
            "codigo":       proximo_codigo,
            "descricao":    desc,
            "unidade":      un,
            "preco_custo":  custo,
            "preco_venda":  venda,
            "qtde_estoque": estoque,
            "data_compra":  datetime(2026, random.randint(1, 6), random.randint(1, 28)),
            "categoria":    categoria,
            "tags":         tags,
        })
        proximo_codigo += 1

    if novos_produtos:
        db.produtos.insert_many(novos_produtos)
        print(f"Inseridos {len(novos_produtos)} produtos extras.")

# Recarrega os produtos (antigos + novos)
produtos = list(db.produtos.find({}, {"_id": 0, "codigo": 1, "preco_venda": 1}))
codigos_produtos = [p["codigo"] for p in produtos]
mapa_preco       = {p["codigo"]: p["preco_venda"] for p in produtos}

# ---------- CLIENTES EXTRA ----------
qtd_clientes_atuais = db.clientes.count_documents({})
if qtd_clientes_atuais < 100:
    clientes_extras = []
    proximo_cliente = 111
    for _ in range(100 - qtd_clientes_atuais):
        nasc = fake.date_of_birth(minimum_age=18, maximum_age=75)
        clientes_extras.append({
            "codigo":          proximo_cliente,
            "nome":            fake.name(),
            "rg":              fake.rg(),
            "data_nascimento": datetime(nasc.year, nasc.month, nasc.day),
        })
        proximo_cliente += 1

    # Upsert para não duplicar em reexecuções
    db.clientes.create_index("codigo", unique=True)
    ops = [
        UpdateOne({"codigo": c["codigo"]}, {"$setOnInsert": c}, upsert=True)
        for c in clientes_extras
    ]
    if ops:
        resultado = db.clientes.bulk_write(ops, ordered=False)
        print(f"Clientes extras: {resultado.upserted_count} inseridos, "
              f"{resultado.modified_count} já existiam.")
            
clientes         = list(db.clientes.find({}, {"_id": 0, "codigo": 1}))
codigos_clientes = [c["codigo"] for c in clientes]

# ============================================================
# 2) GERAÇÃO DOS PEDIDOS
# ============================================================
def gerar_itens():
    """Gera de 1 a 4 itens aleatórios com produtos distintos."""
    qtd_itens = random.randint(1, 4)
    produtos_sorteados = random.sample(codigos_produtos, qtd_itens)

    itens = []
    for cod_prod in produtos_sorteados:
        quantidade = random.randint(1, 5)
        preco_unit = mapa_preco[cod_prod]
        itens.append({
            "codigo_produto": cod_prod,
            "quantidade":     quantidade,
            "preco":          round(preco_unit * quantidade, 2),
        })
    return itens


def gera_pedidos(qtd):
    pedidos = []
    # Continua a numeração após o último pedido existente
    ultimo = db.pedidos.find_one(sort=[("numero_pedido", -1)])
    proximo_numero = (ultimo["numero_pedido"] + 1) if ultimo else 1001

    for i in range(qtd):
        itens = gerar_itens()
        total_itens = round(sum(i["preco"] for i in itens), 2)

        status = random.choice(STATUS_PEDIDO)

        # valor_pago coerente com o status
        if status in ("Cancelado", "Aguardando pagamento"):
            valor_pago = 0
        else:
            valor_pago = total_itens

        pedido = {
            "numero_pedido":  proximo_numero + i,
            "data_pedido":    data_aleatoria_2026(),
            "codigo_cliente": random.choice(codigos_clientes),
            "forma_pagamento": escolher_com_peso(FORMAS_PAGAMENTO),
            "status_pedido":  status,
            "valor_pago":     valor_pago,
            "itens":          itens,
        }
        pedidos.append(pedido)

    return pedidos


print(f"Gerando {QTD_PEDIDOS} pedidos aleatórios...")
pedidos = gera_pedidos(QTD_PEDIDOS)

# ============================================================
# 3) INSERÇÃO EM LOTE
# ============================================================
BATCH_SIZE = 500
inseridos  = 0
for i in range(0, len(pedidos), BATCH_SIZE):
    lote = pedidos[i:i + BATCH_SIZE]
    db.pedidos.insert_many(lote)
    inseridos += len(lote)
    print(f"  → {inseridos}/{len(pedidos)} pedidos inseridos")

# ============================================================
# 4) RESUMO
# ============================================================
print("\n=== RESUMO ===")
print(f"Total de pedidos na base:  {db.pedidos.count_documents({})}")
print(f"Total de produtos na base: {db.produtos.count_documents({})}")
print(f"Total de clientes na base: {db.clientes.count_documents({})}")

# Distribuição por período
pipe = [
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m", "date": "$data_pedido"}},
        "total": {"$sum": 1},
    }},
    {"$sort": {"_id": 1}},
]
print("\nPedidos por mês:")
for r in db.pedidos.aggregate(pipe):
    print(f"  {r['_id']}: {r['total']}")

client.close()
