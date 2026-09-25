# gerar_base_realista.py
# ------------------------------------------------------------
# Gera uma base realista para estudo com Prophet / MongoDB:
#   - 3x clientes e produtos
#   - ~1800 pedidos com itens embutidos
#   - Sazonalidade semanal e mensal
#   - Distribuição de Pareto em clientes
#   - Status e forma de pagamento ponderados
# ------------------------------------------------------------
import random
from datetime import datetime, timedelta

from faker import Faker
from pymongo import MongoClient, UpdateOne

# ============================================================
# CONFIGURAÇÃO
# ============================================================
MONGO_URI   = "mongodb://localhost:27017/"
DB_NAME     = "loja"
FAKER_LOCALE = "pt_BR"

QTD_PRODUTOS = 96       # 12 originais × 3 (ou ~96 no total)
QTD_CLIENTES = 330      # 110 × 3
QTD_PEDIDOS  = 1800     # dentro da faixa 1500-2000

DATA_INICIO  = datetime(2026, 1, 1)
DATA_FIM     = datetime(2026, 9, 30)

SEED = 42               # reprodutibilidade

# ============================================================
# HELPERS
# ============================================================
fake = Faker(FAKER_LOCALE)
random.seed(SEED)

def escolher_com_peso(itens_peso):
    valores = [v for v, _ in itens_peso]
    pesos   = [p for _, p in itens_peso]
    return random.choices(valores, weights=pesos, k=1)[0]

def data_com_sazonalidade():
    """
    Gera uma data entre DATA_INICIO e DATA_FIM com:
      - Distribuição uniforme ao longo dos meses (leve viés de crescimento)
      - Menor volume aos sábados/domingos
    """
    # 1) Sorteia um mês com peso levemente crescente (negócio em expansão)
    meses_peso = [
        ("2026-01", 10), ("2026-02", 11), ("2026-03", 12),
        ("2026-04", 13), ("2026-05", 14), ("2026-06", 15),
        ("2026-07", 16), ("2026-08", 17), ("2026-09", 18),
    ]
    mes_str = escolher_com_peso(meses_peso)
    ano, mes = map(int, mes_str.split("-"))

    # 2) Sorteia um dia dentro do mês
    if mes == 2:
        ultimo_dia = 28
    elif mes in (4, 6, 9, 11):
        ultimo_dia = 30
    else:
        ultimo_dia = 31

    # 3) Tenta até achar um dia útil (mais provável) — fim de semana entra com 25%
    for _ in range(20):
        dia = random.randint(1, ultimo_dia)
        data = datetime(ano, mes, dia)
        if data.weekday() < 5:           # seg-sex
            if random.random() < 0.95:   # 95% dos pedidos caem em dias úteis
                return data
        else:
            if random.random() < 0.25:   # 25% de chance de manter se for fim de semana
                return data

    return datetime(ano, mes, random.randint(1, ultimo_dia))

# ============================================================
# CONEXÃO
# ============================================================
client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

# ============================================================
# 1) LIMPEZA E ÍNDICES
# ============================================================
print("Limpando coleções e recriando índices...")

db.pedidos.delete_many({})
db.clientes.delete_many({})
db.produtos.delete_many({})

db.produtos.create_index("codigo", unique=True)
db.clientes.create_index("codigo", unique=True)
db.pedidos.create_index("numero_pedido", unique=True)
db.pedidos.create_index("data_pedido")
db.pedidos.create_index("status_pedido")
db.pedidos.create_index("codigo_cliente")
db.pedidos.create_index("itens.codigo_produto")

# ============================================================
# 2) PRODUTOS (3x a base original)
# ============================================================
print(f"Gerando {QTD_PRODUTOS} produtos...")

# Catálogo base: (descrição, categoria, preco_custo, unidade, tags)
catalogo_base = [
    # Notebooks
    ("Notebook Dell Inspiron 15",   "notebook", 2500.00, "UN", ["informatica","notebook","dell","premium"]),
    ("Notebook Acer Aspire 5",      "notebook", 2100.00, "UN", ["informatica","notebook","acer"]),
    ("Notebook Lenovo IdeaPad 3",   "notebook", 1900.00, "UN", ["informatica","notebook","lenovo"]),
    ("Notebook Samsung Book",       "notebook", 2300.00, "UN", ["informatica","notebook","samsung"]),
    ("Notebook Apple MacBook Air",  "notebook", 5200.00, "UN", ["informatica","notebook","apple","premium"]),
    ("Notebook Gamer Acer Nitro",   "notebook", 3800.00, "UN", ["informatica","notebook","gamer","acer"]),

    # Monitores
    ("Monitor LG 27'' 4K",          "Audio e Video", 1800.00, "UN", ["informatica","monitor","lg","premium","4k"]),
    ("Monitor Samsung 24'' Full HD","Audio e Video",  700.00, "UN", ["informatica","monitor","samsung"]),
    ("Monitor Gamer 144Hz 27''",    "Audio e Video", 1200.00, "UN", ["informatica","monitor","gamer"]),
    ("Monitor Ultrawide 34''",      "Audio e Video", 2500.00, "UN", ["informatica","monitor","ultrawide","premium"]),

    # Periféricos
    ("Mouse Logitech MX Master 3",  "periferico",  350.00, "UN", ["informatica","periferico","mouse","logitech"]),
    ("Mouse Gamer Razer DeathAdder","periferico",  250.00, "UN", ["informatica","periferico","mouse","razer","gamer"]),
    ("Teclado Mecânico Redragon",   "periferico",  180.00, "UN", ["informatica","periferico","teclado","gamer"]),
    ("Teclado Logitech MX Keys",    "periferico",  450.00, "UN", ["informatica","periferico","teclado","logitech","premium"]),
    ("Webcam Full HD Logitech",     "periferico",  180.00, "UN", ["informatica","periferico","webcam","logitech"]),
    ("Mousepad Gamer XL",           "periferico",   45.00, "UN", ["informatica","periferico","mousepad","gamer"]),
    ("Hub USB-C 7 em 1",            "periferico",   90.00, "UN", ["informatica","periferico","hub","usb-c"]),

    # Áudio e vídeo
    ("Fone Gamer Bluetooth",        "Audio e Video", 150.00, "UN", ["informatica","periferico","audio","gamer","bluetooth"]),
    ("Headset HyperX Cloud II",     "Audio e Video", 320.00, "UN", ["informatica","audio","headset","hyperx"]),
    ("Microfone Condensador USB",   "Audio e Video", 250.00, "UN", ["informatica","audio","microfone","usb"]),
    ("Caixa de Som JBL Go 3",       "Audio e Video", 180.00, "UN", ["informatica","audio","jbl","bluetooth"]),

    # Armazenamento
    ("SSD 1TB Kingston",            "armazenamento", 550.00, "UN", ["informatica","armazenamento","ssd","kingston"]),
    ("SSD NVMe 2TB",                "armazenamento", 750.00, "UN", ["informatica","armazenamento","ssd","nvme"]),
    ("HD Externo 4TB Seagate",      "armazenamento", 480.00, "UN", ["informatica","armazenamento","hd","seagate"]),
    ("Pendrive 128GB Sandisk",      "armazenamento",  80.00, "UN", ["informatica","armazenamento","pendrive","sandisk"]),

    # Componentes
    ("Placa de Vídeo RTX 4060",     "placa_video", 2200.00, "UN", ["informatica","gpu","nvidia"]),
    ("Placa de Vídeo RTX 4070",     "placa_video", 3500.00, "UN", ["informatica","gpu","nvidia","premium"]),
    ("Memória RAM DDR5 16GB",       "memoria",      320.00, "UN", ["informatica","ram","ddr5"]),
    ("Memória RAM DDR4 8GB",        "memoria",      150.00, "UN", ["informatica","ram","ddr4"]),
    ("Placa-Mãe B650M",             "placa_mae",    750.00, "UN", ["informatica","motherboard","amd"]),
    ("Placa-Mãe Z790",              "placa_mae",   1200.00, "UN", ["informatica","motherboard","intel"]),
    ("Processador Intel i7",        "processador",  650.00, "UN", ["informatica","processador","intel","premium"]),
    ("Processador AMD Ryzen 7",     "processador",  720.00, "UN", ["informatica","processador","amd","premium"]),

    # Coolers / energia
    ("Water Cooler 240mm",          "cooler",       380.00, "UN", ["informatica","cooler","water"]),
    ("Kit Ventoinha com 3",         "cooler",       120.00, "CX", ["informatica","cooler","ventoinha"]),
    ("Fonte 600W 80 Plus",          "energia",      350.00, "UN", ["informatica","fonte","energia"]),
    ("Fonte 850W Modular",          "energia",      650.00, "UN", ["informatica","fonte","energia","premium"]),
    ("Nobreak 1500VA",              "energia",      650.00, "UN", ["informatica","nobreak","energia"]),

    # Gabinetes / móveis
    ("Gabinete Gamer",              "gabinete",     130.00, "UN", ["informatica","gabinete","gamer"]),
    ("Gabinete Mid Tower",          "gabinete",     180.00, "UN", ["informatica","gabinete"]),
    ("Cadeira Gamer ThunderX3",     "movel",        950.00, "UN", ["movel","cadeira","gamer","premium"]),
    ("Suporte Monitor Articulado",  "movel",        120.00, "UN", ["informatica","suporte","monitor"]),
    ("Mesa Gamer com LED",          "movel",        850.00, "UN", ["movel","mesa","gamer"]),

    # Cabos / rede
    ("Cabo HDMI 2.1 - 2m",          "cabo",          25.00, "UN", ["informatica","cabo","hdmi"]),
    ("Cabo DisplayPort 2m",         "cabo",          35.00, "UN", ["informatica","cabo","displayport"]),
    ("Cabo USB-C 1m",               "cabo",          20.00, "UN", ["informatica","cabo","usb-c"]),
    ("Roteador Wi-Fi 6 TP-Link",    "rede",         280.00, "UN", ["informatica","roteador","wifi"]),
    ("Switch 8 portas Gigabit",     "rede",         180.00, "UN", ["informatica","switch","rede"]),

    # Impressoras / outros
    ("Impressora Multifuncional HP","impressora",   650.00, "UN", ["informatica","impressora","hp"]),
    ("Scanner Canon",               "impressora",   450.00, "UN", ["informatica","scanner","canon"]),
]

# Expande para ~96 produtos: repete o catálogo com pequenas variações de preço
produtos = []
codigo = 1
variacoes = ["", " Plus", " Pro", " Lite", " Max", " 2026", " Turbo", " Ultra"]

while len(produtos) < QTD_PRODUTOS:
    for base in catalogo_base:
        if len(produtos) >= QTD_PRODUTOS:
            break
        descricao, categoria, custo, unidade, tags = base
        variacao = random.choice(variacoes)
        fator    = random.uniform(0.95, 1.15)   # ±15% no preço

        custo_final = round(custo * fator, 2)
        venda_final = round(custo_final * random.uniform(1.25, 1.55), 2)

        produtos.append({
            "codigo":       codigo,
            "descricao":    descricao + variacao,
            "unidade":      unidade,
            "preco_custo":  custo_final,
            "preco_venda":  venda_final,
            "qtde_estoque": random.randint(5, 120),
            "data_compra":  DATA_INICIO - timedelta(days=random.randint(30, 180)),
            "categoria":    categoria,
            "tags":         tags,
        })
        codigo += 1

db.produtos.insert_many(produtos)
print(f"  → {len(produtos)} produtos inseridos.")

# ============================================================
# 3) CLIENTES (3x a base original)
# ============================================================
print(f"Gerando {QTD_CLIENTES} clientes...")

clientes = []
for i in range(1, QTD_CLIENTES + 1):
    nasc = fake.date_of_birth(minimum_age=18, maximum_age=75)
    clientes.append({
        "codigo":          100 + i,                 # 101 a 430
        "nome":            fake.name(),
        "rg":              fake.rg(),
        "data_nascimento": datetime(nasc.year, nasc.month, nasc.day),
    })

db.clientes.insert_many(clientes)
print(f"  → {len(clientes)} clientes inseridos.")

# ============================================================
# 4) PEDIDOS (distribuição realista)
# ============================================================
print(f"Gerando {QTD_PEDIDOS} pedidos...")

# Pool de produtos e preços
codigos_produtos = [p["codigo"] for p in produtos]
mapa_preco       = {p["codigo"]: p["preco_venda"] for p in produtos}
codigos_clientes = [c["codigo"] for c in clientes]

# Pareto: 20% dos clientes fazem 80% dos pedidos
qtd_top = max(1, int(QTD_CLIENTES * 0.20))
clientes_top = random.sample(codigos_clientes, qtd_top)

# Status ponderados (realista)
STATUS_PESO = [
    ("Entregue",              50),
    ("Em processamento",      18),
    ("Enviado",               15),
    ("Aguardando pagamento",  10),
    ("Cancelado",              7),
]

# Formas de pagamento evoluem com o tempo (PIX ganha espaço)
def forma_por_data(data):
    if data >= datetime(2026, 7, 1):
        return escolher_com_peso([
            ("Cartão de Crédito", 30),
            ("PIX",               45),
            ("Boleto",            12),
            ("Cartão de Débito",  13),
        ])
    return escolher_com_peso([
        ("Cartão de Crédito", 40),
        ("PIX",               25),
        ("Boleto",            22),
        ("Cartão de Débito",  13),
    ])


def gerar_itens():
    """
    Gera itens com distribuição realista:
      - 1 item (50%), 2 itens (30%), 3 itens (15%), 4 itens (5%)
      - Quantidade: 1 (60%), 2 (25%), 3 (10%), 4-5 (5%)
    """
    qtd_itens = escolher_com_peso([(1, 50), (2, 30), (3, 15), (4, 5)])
    produtos_sorteados = random.sample(codigos_produtos, qtd_itens)

    itens = []
    for cod_prod in produtos_sorteados:
        quantidade = escolher_com_peso([(1, 60), (2, 25), (3, 10), (4, 3), (5, 2)])
        preco_unit = mapa_preco[cod_prod]
        itens.append({
            "codigo_produto": cod_prod,
            "quantidade":     quantidade,
            "preco":          round(preco_unit * quantidade, 2),
        })
    return itens


def escolher_cliente():
    """80/20: 80% dos pedidos vão para 20% dos clientes."""
    if random.random() < 0.80:
        return random.choice(clientes_top)
    return random.choice(codigos_clientes)


pedidos = []
for i in range(QTD_PEDIDOS):
    itens = gerar_itens()
    total_itens = round(sum(x["preco"] for x in itens), 2)

    status = escolher_com_peso(STATUS_PESO)
    valor_pago = 0 if status in ("Cancelado", "Aguardando pagamento") else total_itens

    data = data_com_sazonalidade()

    pedido = {
        "numero_pedido":  1001 + i,
        "data_pedido":    data,
        "codigo_cliente": escolher_cliente(),
        "forma_pagamento": forma_por_data(data),
        "status_pedido":  status,
        "valor_pago":     valor_pago,
        "itens":          itens,
    }
    pedidos.append(pedido)

# ============================================================
# 5) INSERÇÃO EM LOTE
# ============================================================
BATCH = 500
for i in range(0, len(pedidos), BATCH):
    db.pedidos.insert_many(pedidos[i:i + BATCH])
    print(f"  → {min(i + BATCH, len(pedidos))}/{len(pedidos)} pedidos inseridos")

# ============================================================
# 6) RESUMO
# ============================================================
print("\n=== RESUMO ===")
print(f"Produtos: {db.produtos.count_documents({})}")
print(f"Clientes: {db.clientes.count_documents({})}")
print(f"Pedidos:  {db.pedidos.count_documents({})}")

print("\nPedidos por mês:")
for r in db.pedidos.aggregate([
    {"$group": {
        "_id": {"$dateToString": {"format": "%Y-%m", "date": "$data_pedido"}},
        "total": {"$sum": 1},
    }},
    {"$sort": {"_id": 1}},
]):
    print(f"  {r['_id']}: {r['total']}")

print("\nPedidos por dia da semana:")
dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
for r in db.pedidos.aggregate([
    {"$group": {
        "_id": {"$dayOfWeek": "$data_pedido"},
        "total": {"$sum": 1},
    }},
    {"$sort": {"_id": 1}},
]):
    # $dayOfWeek: 1=Dom, 2=Seg, ..., 7=Sáb
    idx = (r["_id"] + 5) % 7   # converte para Seg=0 ... Dom=6
    print(f"  {dias[idx]}: {r['total']}")

print("\nTop 5 clientes (mais pedidos):")
for r in db.pedidos.aggregate([
    {"$group": {"_id": "$codigo_cliente", "pedidos": {"$sum": 1}}},
    {"$sort": {"pedidos": -1}},
    {"$limit": 5},
]):
    print(f"  cliente {r['_id']}: {r['pedidos']} pedidos")

client.close()
print("\nBase gerada com sucesso.")
