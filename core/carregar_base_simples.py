# core/carregar_base_simples.py
from core.mongo_client import get_db, ping

# ============================================================
# DADOS DA BASE SIMPLES (Mongo-Inclusao v2)
# ============================================================
PRODUTOS = [
    {"codigo": 1, "descricao": "Notebook Dell Inspiron 15", "unidade": "UN",
         "preco_custo": 2500.00, "preco_venda": 3499.90, "qtde_estoque": 15,
         "data_compra": "2026-01-15", "sistema_operacional": "Windows"},
    {"codigo": 2, "descricao": "Mouse Logitech MX Master 3", "unidade": "UN", "preco_custo": 350.00, "preco_venda": 549.90, "qtde_estoque": 40,
            "data_compra": "2026-02-10"},
    {"codigo": 3, "descricao": "Teclado Mecânico Redragon", "unidade": "UN", "preco_custo": 180.00, "preco_venda": 299.90, "qtde_estoque": 25,
            "data_compra": "2026-02-20"},
    {"codigo": 4, "descricao": "Monitor LG 27'' 4K", "unidade": "UN", "preco_custo": 1800.00, "preco_venda": 2499.00, "qtde_estoque": 8,
            "data_compra": "2026-03-05"},
    {"codigo": 5, "descricao": "Cabo HDMI 2.1 - 2 metros", "unidade": "UN", "preco_custo": 25.00, "preco_venda": 59.90, "qtde_estoque": 120,
            "data_compra": "2026-03-12"},
    {"codigo": 6, "descricao": "Cadeira Gamer ThunderX3", "unidade": "UN", "preco_custo": 950.00, "preco_venda": 1499.00, "qtde_estoque": 10,
            "data_compra": "2026-03-25"},
    {"codigo": 7, "descricao": "Fone Gamer Bluetooth", "unidade": "UN", "preco_custo": 150.00, "preco_venda": 249.00, "qtde_estoque": 30,
            "data_compra": "2026-04-10"},
    {"codigo": 8, "descricao": "SSD 1tb", "unidade": "UN", "preco_custo": 550.00, "preco_venda": 759.00, "qtde_estoque": 10,
            "data_compra": "2026-04-10"},
    {"codigo": 9, "descricao": "Kit Ventoinha com 3", "unidade": "CX", "preco_custo": 120.00, "preco_venda": 219.00, "qtde_estoque": 20,
            "data_compra": "2026-05-12"},
    {"codigo": 10, "descricao": "Fonte 600w", "unidade": "UN", "preco_custo": 350.00, "preco_venda": 449.00, "qtde_estoque": 30,
            "data_compra": "2026-05-12"},
    {"codigo": 11, "descricao": "Gabinete Gamer", "unidade": "UN", "preco_custo": 130.00, "preco_venda": 229.00, "qtde_estoque": 30,
            "data_compra": "2026-06-15"},
    {"codigo": 12, "descricao": "Processador Intel i7", "unidade": "UN", "preco_custo": 650.00, "preco_venda": 799.00, "qtde_estoque": 20,
            "data_compra": "2026-06-15"}
]

CLIENTES = [
    {"codigo": 101, "nome": "João Carlos Silva", "rg": "12.345.678-9", "data_nascimento": "1985-06-12"},
    {"codigo": 102, "nome": "Maria Fernanda Souza", "rg": "23.456.789-0", "data_nascimento": "1990-09-25"},
    {"codigo": 103, "nome": "Pedro Henrique Almeida", "rg": "34.567.890-1", "data_nascimento": "1978-03-08"},
    {"codigo": 104, "nome": "Ana Beatriz Oliveira", "rg": "45.678.901-2", "data_nascimento": "1995-11-30"},
    {"codigo": 105, "nome": "Carlos Eduardo Ramos", "rg": "56.789.012-3", "data_nascimento": "1982-07-19"},
    {"codigo": 106, "nome": "Pedro Luiz", "rg": "13.123.124-4", "data_nascimento": "1981-02-05"},
    {"codigo": 107, "nome": "João Rafael", "rg": "14.234.235-5", "data_nascimento": "1980-04-10"},
    {"codigo": 108, "nome": "Levy Lima", "rg": "15.345.346-6", "data_nascimento": "1979-05-12"},
    {"codigo": 109, "nome": "Thiago Arruda", "rg": "16.456.457-7", "data_nascimento": "1978-06-15"},
    {"codigo": 110, "nome": "Alberto Cesar", "rg": "17.567.568-8", "data_nascimento": "1977-07-20"}
]

PEDIDOS = [
    {"numero_pedido": 1001, "data_pedido": "2026-04-01", "codigo_cliente": 101, "forma_pagamento": "Cartão de Crédito", "status_pedido": "Entregue", "valor_pago": 4049.80,
     "itens": [
         {"codigo_produto": 1, "quantidade": 1, "preco": 3499.90},
         {"codigo_produto": 2, "quantidade": 1, "preco": 549.90},
     ]},
    {"numero_pedido": 1002, "data_pedido": "2026-04-05", "codigo_cliente": 102, "forma_pagamento": "PIX", "status_pedido": "Entregue", "valor_pago": 1099.00,
     "itens": [ {"codigo_produto": 2, "quantidade": 2, "preco": 549.90} ]},
    {"numero_pedido": 1003, "data_pedido": "2026-04-10", "codigo_cliente": 103, "forma_pagamento": "Boleto", "status_pedido": "Em processamento", "valor_pago": 2499.00,
     "itens": [ {"codigo_produto": 4, "quantidade": 1, "preco": 2499.00} ]},
    {"numero_pedido": 1004, "data_pedido": "2026-04-15", "codigo_cliente": 101, "forma_pagamento": "Cartão de Débito", "status_pedido": "Enviado", "valor_pago": 299.90,
     "itens": [ {"codigo_produto": 3, "quantidade": 1, "preco": 299.90} ]},
    {"numero_pedido": 1005, "data_pedido": "2026-04-20", "codigo_cliente": 104, "forma_pagamento": "PIX", "status_pedido": "Aguardando pagamento", "valor_pago": 0,
     "itens": [ {"codigo_produto": 5, "quantidade": 5, "preco": 299.50} ]},
    {"numero_pedido": 1006, "data_pedido": "2026-04-25", "codigo_cliente": 105, "forma_pagamento": "Cartão de Crédito", "status_pedido": "Cancelado", "valor_pago": 0,
     "itens": [ {"codigo_produto": 6, "quantidade": 2, "preco": 1499.00} ]},
    {"numero_pedido": 1007, "data_pedido": "2026-04-05", "codigo_cliente": 107, "forma_pagamento": "PIX", "status_pedido": "Em processamento", "valor_pago": 549.90,
     "itens": [ {"codigo_produto": 2, "quantidade": 1, "preco": 549.90} ]},
    {"numero_pedido": 1008, "data_pedido": "2026-04-10", "codigo_cliente": 106, "forma_pagamento": "Boleto", "status_pedido": "Entregue", "valor_pago": 2499.00,
     "itens": [ {"codigo_produto": 4, "quantidade": 1, "preco": 2499.00} ]},
    {"numero_pedido": 1009, "data_pedido": "2026-04-15", "codigo_cliente": 108, "forma_pagamento": "Cartão de Débito", "status_pedido": "Aguardando pagamento", "valor_pago": 0,
     "itens": [ {"codigo_produto": 6, "quantidade": 2, "preco": 1499.00} ]},
    {"numero_pedido": 1010, "data_pedido": "2026-04-20", "codigo_cliente": 109, "forma_pagamento": "PIX", "status_pedido": "Enviado", "valor_pago": 759.00,
     "itens": [ {"codigo_produto": 8, "quantidade": 1, "preco": 759.00} ]},
    {"numero_pedido": 1011, "data_pedido": "2026-04-25", "codigo_cliente": 110, "forma_pagamento": "Cartão de Crédito", "status_pedido": "Entregue", "valor_pago": 3044.00,
     "itens": [
         {"codigo_produto": 10, "quantidade": 5, "preco": 2245.00},
         {"codigo_produto": 12, "quantidade": 1, "preco": 799.00}
     ]},
    {"numero_pedido": 1012, "data_pedido": "2026-04-05", "codigo_cliente": 106, "forma_pagamento": "PIX", "status_pedido": "Cancelado", "valor_pago": 0,
     "itens": [ {"codigo_produto": 1, "quantidade": 2, "preco": 3499.90} ]},
    {"numero_pedido": 1013, "data_pedido": "2026-04-10", "codigo_cliente": 103, "forma_pagamento": "Boleto", "status_pedido": "Enviado", "valor_pago": 299.90,
     "itens": [ {"codigo_produto": 3, "quantidade": 1, "preco": 299.90} ]},
    {"numero_pedido": 1014, "data_pedido": "2026-04-15", "codigo_cliente": 105, "forma_pagamento": "Cartão de Débito", "status_pedido": "Em processamento", "valor_pago": 59.90,
     "itens": [ {"codigo_produto": 5, "quantidade": 2, "preco": 59.90} ]},
    {"numero_pedido": 1015, "data_pedido": "2026-04-20", "codigo_cliente": 104, "forma_pagamento": "PIX", "status_pedido": "Cancelado", "valor_pago": 0,
     "itens": [
         {"codigo_produto": 7, "quantidade": 1, "preco": 249.00},
         {"codigo_produto": 9, "quantidade": 1, "preco": 219.00}
     ]},
    {"numero_pedido": 1016, "data_pedido": "2026-04-25", "codigo_cliente": 107, "forma_pagamento": "Cartão de Crédito", "status_pedido": "Aguardando pagamento", "valor_pago": 0,
     "itens": [
         {"codigo_produto": 11, "quantidade": 5, "preco": 1145.00},
         {"codigo_produto": 1, "quantidade": 1, "preco": 3499.90},
         {"codigo_produto": 2, "quantidade": 2, "preco": 549.90}
     ]}
]


# Tags + categorias (mesmo que no seu .js)
UPDATES_TAGS = [
    (1, ["informatica", "notebook", "dell", "premium"], "notebook"),
    (2, ["informatica", "periferico", "mouse", "logitech"], "periferico"),

    (3, ["informatica", "periferico", "teclado", "gamer"], "periferico"),
    (4, ["informatica", "monitor", "lg", "premium", "4k"], "Audio e Video"),
    (5, ["informatica", "cabo", "hdmi"], "cabo"),
    (6, ["movel"      , "cadeira", "gamer", "premium"], "movel"),
    (7, ["informatica", "periferico", "audio", "gamer", "bluetooth"], "Audio e Video"),
    (8, ["informatica", "armazenamento", "ssd"], "armazenamento"),
    (9, ["informatica", "cooler", "ventoinha"], "cooler"),
    (10, ["informatica", "fonte", "energia"], "energia"),
    (11, ["informatica", "gabinete", "gamer"], "gabinete"),
    (12, ["informatica", "processador", "intel", "premium"], "processador")
]

def executar() -> dict:
    """Limpa e insere a base simples. Retorna as contagens."""
    db = get_db()

    # 1) Limpa
    try:
        db.produtos.drop()
    except Exception as e:
        pass

    try:
        db.clientes.drop()
    except Exception as e:
        pass

    try:
        db.pedidos.drop()
    except Exception as e:
        pass

    # 2) Converte strings em datetime (obrigatório para o MongoDB)
    from datetime import datetime
    for p in PRODUTOS:
        p["data_compra"] = datetime.fromisoformat(p["data_compra"])
    for c in CLIENTES:
        c["data_nascimento"] = datetime.fromisoformat(c["data_nascimento"])
    for p in PEDIDOS:
        p["data_pedido"] = datetime.fromisoformat(p["data_pedido"])

    # 3) Insere
    db.produtos.insert_many(PRODUTOS)
    db.clientes.insert_many(CLIENTES)
    db.pedidos.insert_many(PEDIDOS)

    # 4) Aplica tags e categorias
    for codigo, tags, categoria in UPDATES_TAGS:
        db.produtos.update_one(
            {"codigo": codigo},
            {"$set": {"tags": tags, "categoria": categoria}},
        )

    # 5) Retorna as contagens com as chaves que a UI espera
    return {
        "produtos": db.produtos.count_documents({}),
        "clientes": db.clientes.count_documents({}),
        "pedidos":  db.pedidos.count_documents({}),
    }


def estatisticas() -> dict:
    """Retorna contagem + amostra de cada coleção."""
    db = get_db()
    out = {}
    for col in ["produtos", "clientes", "pedidos"]:
        out[col] = {
            "total":   db[col].count_documents({}),
            "amostra": db[col].find_one() or {},
        }
    return out
