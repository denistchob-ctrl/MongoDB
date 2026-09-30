# core/gerar_base_aleatoria.py
# ------------------------------------------------------------
# Gera uma base realista parametrizável para o Streamlit.
# Adaptado de "Atividade-P1-DENIS GerarBase.py".
# ------------------------------------------------------------
import random
from datetime import datetime, timedelta

from faker import Faker

from core.mongo_client import get_db

# ============================================================
# HELPERS
# ============================================================
fake = Faker("pt_BR")


def _escolher_com_peso(itens_peso):
    valores = [v for v, _ in itens_peso]
    pesos   = [p for _, p in itens_peso]
    return random.choices(valores, weights=pesos, k=1)[0]


def _data_com_sazonalidade(data_inicio: datetime, data_fim: datetime) -> datetime:
    """
    Gera uma data entre data_inicio e data_fim com:
      - Distribuição aproximadamente uniforme ao longo dos meses
      - Menor volume aos sábados/domingos
    """
    delta_total = (data_fim - data_inicio).days
    if delta_total <= 0:
        return data_inicio

    for _ in range(30):
        dia_offset = random.randint(0, delta_total)
        data = data_inicio + timedelta(days=dia_offset)
        if data.weekday() < 5:           # seg-sex
            if random.random() < 0.95:
                return data
        else:                            # fim de semana
            if random.random() < 0.25:
                return data

    return data_inicio + timedelta(days=random.randint(0, delta_total))


# ============================================================
# CATÁLOGO BASE DE PRODUTOS
# ============================================================
def _catalogo_base():
    return [
        # Notebooks
        ("Notebook Dell Inspiron 15",   "notebook",      2500.00, "UN", ["informatica","notebook","dell","premium"]),
        ("Notebook Acer Aspire 5",      "notebook",      2100.00, "UN", ["informatica","notebook","acer"]),
        ("Notebook Lenovo IdeaPad 3",   "notebook",      1900.00, "UN", ["informatica","notebook","lenovo"]),
        ("Notebook Samsung Book",       "notebook",      2300.00, "UN", ["informatica","notebook","samsung"]),
        ("Notebook Apple MacBook Air",  "notebook",      5200.00, "UN", ["informatica","notebook","apple","premium"]),
        ("Notebook Gamer Acer Nitro",   "notebook",      3800.00, "UN", ["informatica","notebook","gamer","acer"]),
        # Monitores
        ("Monitor LG 27'' 4K",          "Audio e Video", 1800.00, "UN", ["informatica","monitor","lg","premium","4k"]),
        ("Monitor Samsung 24'' Full HD","Audio e Video",  700.00, "UN", ["informatica","monitor","samsung"]),
        ("Monitor Gamer 144Hz 27''",    "Audio e Video", 1200.00, "UN", ["informatica","monitor","gamer"]),
        ("Monitor Ultrawide 34''",      "Audio e Video", 2500.00, "UN", ["informatica","monitor","ultrawide","premium"]),
        # Periféricos
        ("Mouse Logitech MX Master 3",  "periferico",     350.00, "UN", ["informatica","periferico","mouse","logitech"]),
        ("Mouse Gamer Razer DeathAdder","periferico",     250.00, "UN", ["informatica","periferico","mouse","razer","gamer"]),
        ("Teclado Mecânico Redragon",   "periferico",     180.00, "UN", ["informatica","periferico","teclado","gamer"]),
        ("Teclado Logitech MX Keys",    "periferico",     450.00, "UN", ["informatica","periferico","teclado","logitech","premium"]),
        ("Webcam Full HD Logitech",     "periferico",     180.00, "UN", ["informatica","periferico","webcam","logitech"]),
        ("Mousepad Gamer XL",           "periferico",      45.00, "UN", ["informatica","periferico","mousepad","gamer"]),
        ("Hub USB-C 7 em 1",            "periferico",      90.00, "UN", ["informatica","periferico","hub","usb-c"]),
        # Áudio e vídeo
        ("Fone Gamer Bluetooth",        "Audio e Video",  150.00, "UN", ["informatica","periferico","audio","gamer","bluetooth"]),
        ("Headset HyperX Cloud II",     "Audio e Video",  320.00, "UN", ["informatica","audio","headset","hyperx"]),
        ("Microfone Condensador USB",   "Audio e Video",  250.00, "UN", ["informatica","audio","microfone","usb"]),
        ("Caixa de Som JBL Go 3",       "Audio e Video",  180.00, "UN", ["informatica","audio","jbl","bluetooth"]),
        # Armazenamento
        ("SSD 1TB Kingston",            "armazenamento",  550.00, "UN", ["informatica","armazenamento","ssd","kingston"]),
        ("SSD NVMe 2TB",                "armazenamento",  750.00, "UN", ["informatica","armazenamento","ssd","nvme"]),
        ("HD Externo 4TB Seagate",      "armazenamento",  480.00, "UN", ["informatica","armazenamento","hd","seagate"]),
        ("Pendrive 128GB Sandisk",      "armazenamento",   80.00, "UN", ["informatica","armazenamento","pendrive","sandisk"]),
        # Componentes
        ("Placa de Vídeo RTX 4060",     "placa_video",   2200.00, "UN", ["informatica","gpu","nvidia"]),
        ("Placa de Vídeo RTX 4070",     "placa_video",   3500.00, "UN", ["informatica","gpu","nvidia","premium"]),
        ("Memória RAM DDR5 16GB",       "memoria",        320.00, "UN", ["informatica","ram","ddr5"]),
        ("Memória RAM DDR4 8GB",        "memoria",        150.00, "UN", ["informatica","ram","ddr4"]),
        ("Placa-Mãe B650M",             "placa_mae",      750.00, "UN", ["informatica","motherboard","amd"]),
        ("Placa-Mãe Z790",              "placa_mae",     1200.00, "UN", ["informatica","motherboard","intel"]),
        ("Processador Intel i7",        "processador",    650.00, "UN", ["informatica","processador","intel","premium"]),
        ("Processador AMD Ryzen 7",     "processador",    720.00, "UN", ["informatica","processador","amd","premium"]),
        # Coolers / energia
        ("Water Cooler 240mm",          "cooler",         380.00, "UN", ["informatica","cooler","water"]),
        ("Kit Ventoinha com 3",         "cooler",         120.00, "CX", ["informatica","cooler","ventoinha"]),
        ("Fonte 600W 80 Plus",          "energia",        350.00, "UN", ["informatica","fonte","energia"]),
        ("Fonte 850W Modular",          "energia",        650.00, "UN", ["informatica","fonte","energia","premium"]),
        ("Nobreak 1500VA",              "energia",        650.00, "UN", ["informatica","nobreak","energia"]),
        # Gabinetes / móveis
        ("Gabinete Gamer",              "gabinete",       130.00, "UN", ["informatica","gabinete","gamer"]),
        ("Gabinete Mid Tower",          "gabinete",       180.00, "UN", ["informatica","gabinete"]),
        ("Cadeira Gamer ThunderX3",     "movel",          950.00, "UN", ["movel","cadeira","gamer","premium"]),
        ("Suporte Monitor Articulado",  "movel",          120.00, "UN", ["informatica","suporte","monitor"]),
        ("Mesa Gamer com LED",          "movel",          850.00, "UN", ["movel","mesa","gamer"]),
        # Cabos / rede
        ("Cabo HDMI 2.1 - 2m",          "cabo",            25.00, "UN", ["informatica","cabo","hdmi"]),
        ("Cabo DisplayPort 2m",         "cabo",            35.00, "UN", ["informatica","cabo","displayport"]),
        ("Cabo USB-C 1m",               "cabo",            20.00, "UN", ["informatica","cabo","usb-c"]),
        ("Roteador Wi-Fi 6 TP-Link",    "rede",           280.00, "UN", ["informatica","roteador","wifi"]),
        ("Switch 8 portas Gigabit",     "rede",           180.00, "UN", ["informatica","switch","rede"]),
        # Impressoras / outros
        ("Impressora Multifuncional HP","impressora",     650.00, "UN", ["informatica","impressora","hp"]),
        ("Scanner Canon",               "impressora",     450.00, "UN", ["informatica","scanner","canon"]),
    ]

# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================
def executar(
    qtd_pedidos: int,
    qtd_produtos: int,
    qtd_clientes: int,
    data_inicio,
    data_fim,
    limpar: bool = True,
) -> dict:
    """
    Gera uma base realista no MongoDB e retorna um resumo serializável.

    Parâmetros
    ----------
    qtd_pedidos : int    — quantidade de pedidos a gerar
    qtd_produtos: int    — quantidade de produtos a gerar
    qtd_clientes: int    — quantidade de clientes a gerar
    data_inicio : date   — data inicial do período
    data_fim    : date   — data final do período
    limpar      : bool   — se True, apaga as coleções antes de gerar
    """
    db = get_db()

    # ---------- Normaliza datas para datetime ----------
    if isinstance(data_inicio, datetime):
        dt_inicio = data_inicio
    else:
        dt_inicio = datetime(data_inicio.year, data_inicio.month, data_inicio.day)

    if isinstance(data_fim, datetime):
        dt_fim = data_fim
    else:
        dt_fim = datetime(data_fim.year, data_fim.month, data_fim.day)

    # ---------- Semente reprodutível (opcional) ----------
    random.seed(42)

    # ---------- 1) LIMPEZA ----------
    if limpar:
        db.produtos.drop()
        db.clientes.drop()
        db.pedidos.drop()

    # Garante índices (recriados sempre que a coleção é recriada)
    db.produtos.create_index("codigo", unique=True)
    db.clientes.create_index("codigo", unique=True)
    db.pedidos.create_index("numero_pedido", unique=True)
    db.pedidos.create_index("data_pedido")
    db.pedidos.create_index("status_pedido")
    db.pedidos.create_index("codigo_cliente")
    db.pedidos.create_index("itens.codigo_produto")

    # ---------- 2) PRODUTOS ----------
    catalogo = _catalogo_base()
    variacoes = ["", " Plus", " Pro", " Lite", " Max", " 2026", " Turbo", " Ultra"]

    produtos = []
    codigo = 1
    while len(produtos) < qtd_produtos:
        for base in catalogo:
            if len(produtos) >= qtd_produtos:
                break
            descricao, categoria, custo, unidade, tags = base
            variacao = random.choice(variacoes)
            fator = random.uniform(0.95, 1.15)

            custo_final = round(custo * fator, 2)
            venda_final = round(custo_final * random.uniform(1.25, 1.55), 2)

            produtos.append({
                "codigo":       codigo,
                "descricao":    descricao + variacao,
                "unidade":      unidade,
                "preco_custo":  custo_final,
                "preco_venda":  venda_final,
                "qtde_estoque": random.randint(5, 120),
                "data_compra":  dt_inicio - timedelta(days=random.randint(30, 180)),
                "categoria":    categoria,
                "tags":         tags,
            })
            codigo += 1

    db.produtos.insert_many(produtos)

    # ---------- 3) CLIENTES ----------
    clientes = []
    for i in range(1, qtd_clientes + 1):
        nasc = fake.date_of_birth(minimum_age=18, maximum_age=75)
        clientes.append({
            "codigo":          100 + i,
            "nome":            fake.name(),
            "rg":              fake.rg(),
            "data_nascimento": datetime(nasc.year, nasc.month, nasc.day),
        })

    db.clientes.insert_many(clientes)

    # ---------- 4) PEDIDOS ----------
    codigos_produtos = [p["codigo"] for p in produtos]
    mapa_preco       = {p["codigo"]: p["preco_venda"] for p in produtos}
    codigos_clientes = [c["codigo"] for c in clientes]

    # Pareto: 20% dos clientes fazem 80% dos pedidos
    qtd_top = max(1, int(qtd_clientes * 0.20))
    clientes_top = random.sample(codigos_clientes, qtd_top)

    STATUS_PESO = [
        ("Entregue",              50),
        ("Em processamento",      18),
        ("Enviado",               15),
        ("Aguardando pagamento",  10),
        ("Cancelado",              7),
    ]

    def forma_por_data(data):
        if data >= datetime(2026, 7, 1):
            return _escolher_com_peso([
                ("Cartão de Crédito", 30),
                ("PIX",               45),
                ("Boleto",            12),
                ("Cartão de Débito",  13),
            ])
        return _escolher_com_peso([
            ("Cartão de Crédito", 40),
            ("PIX",               25),
            ("Boleto",            22),
            ("Cartão de Débito",  13),
        ])

    def gerar_itens():
        qtd_itens = _escolher_com_peso([(1, 50), (2, 30), (3, 15), (4, 5)])
        produtos_sorteados = random.sample(codigos_produtos, qtd_itens)
        itens = []
        for cod_prod in produtos_sorteados:
            quantidade = _escolher_com_peso([(1, 60), (2, 25), (3, 10), (4, 3), (5, 2)])
            preco_unit = mapa_preco[cod_prod]
            itens.append({
                "codigo_produto": cod_prod,
                "quantidade":     quantidade,
                "preco":          round(preco_unit * quantidade, 2),
            })
        return itens

    def escolher_cliente():
        if random.random() < 0.80:
            return random.choice(clientes_top)
        return random.choice(codigos_clientes)

    pedidos = []
    for i in range(qtd_pedidos):
        itens = gerar_itens()
        total_itens = round(sum(x["preco"] for x in itens), 2)

        status = _escolher_com_peso(STATUS_PESO)
        valor_pago = 0 if status in ("Cancelado", "Aguardando pagamento") else total_itens

        data = _data_com_sazonalidade(dt_inicio, dt_fim)

        pedidos.append({
            "numero_pedido":  1001 + i,
            "data_pedido":    data,
            "codigo_cliente": escolher_cliente(),
            "forma_pagamento": forma_por_data(data),
            "status_pedido":  status,
            "valor_pago":     valor_pago,
            "itens":          itens,
        })

    # Inserção em lote para não estourar o limite de 16 MB por comando
    BATCH = 500
    for i in range(0, len(pedidos), BATCH):
        db.pedidos.insert_many(pedidos[i:i + BATCH])

    # ---------- 5) RESUMO SERIALIZÁVEL ----------
    return {
        "mensagem":         "Base gerada com sucesso!",
        "qtd_produtos":     db.produtos.count_documents({}),
        "qtd_clientes":     db.clientes.count_documents({}),
        "qtd_pedidos":      db.pedidos.count_documents({}),
        "periodo_inicio":   dt_inicio.strftime("%Y-%m-%d"),
        "periodo_fim":      dt_fim.strftime("%Y-%m-%d"),
        "amostra_produto":  db.produtos.find_one({}, {"_id": 0}) or {},
        "amostra_cliente":  db.clientes.find_one({}, {"_id": 0}) or {},
        "amostra_pedido":   db.pedidos.find_one({}, {"_id": 0}) or {},
    }