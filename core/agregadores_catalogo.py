# core/agregadores_catalogo.py
# ------------------------------------------------------------
# Catálogo dos pipelines de agregação usados no projeto.
# Cada item tem: id, titulo, comando, colecao, pipeline, explicacao.
# ------------------------------------------------------------
from datetime import datetime
from core.mongo_client import get_db


# ============================================================
# CATÁLOGO
# ============================================================
CATALOGO = [
    {
        "id": "count_produtos",
        "titulo": "Total de produtos cadastrados",
        "colecao": "produtos",
        "comando": "db.produtos.countDocuments()",
        "pipeline": None,       # caso especial: countDocuments
        "modo": "count",
        "explicacao": (
            "Forma mais simples de agregação: totalizar documentos de uma coleção. "
            "Dá ao administrador uma visão imediata do tamanho do catálogo."
        ),
    },
    {
        "id": "count_clientes",
        "titulo": "Total de clientes cadastrados",
        "colecao": "clientes",
        "comando": "db.clientes.countDocuments()",
        "pipeline": None,
        "modo": "count",
        "explicacao": (
            "Indicador de base de clientes. Serve como métrica de crescimento "
            "e base para cálculos de ticket médio por cliente."
        ),
    },
    {
        "id": "count_pedidos",
        "titulo": "Total de pedidos no sistema",
        "colecao": "pedidos",
        "comando": "db.pedidos.countDocuments()",
        "pipeline": None,
        "modo": "count",
        "explicacao": (
            "Volume total de pedidos registrados. É o primeiro número que o "
            "gestor olha para saber o tamanho da operação."
        ),
    },
    {
        "id": "pedidos_por_status",
        "titulo": "Pedidos por status",
        "colecao": "pedidos",
        "comando": (
            "db.pedidos.aggregate([\n"
            "  { $group: { _id: '$status_pedido', Quantidade: { $sum: 1 } } }\n"
            "])"
        ),
        "pipeline": [
            {"$group": {"_id": "$status_pedido", "Quantidade": {"$sum": 1}}},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Distribuição dos pedidos ao longo do funil (Entregue, Em processamento, "
            "Enviado, Aguardando pagamento, Cancelado). Serve para identificar "
            "gargalos e priorizar tratativas com clientes."
        ),
    },
    {
        "id": "pedidos_por_data",
        "titulo": "Pedidos por data",
        "colecao": "pedidos",
        "comando": (
            "db.pedidos.aggregate([\n"
            "  { $group: {\n"
            "      _id: { $dateToString: { format: '%Y-%m-%d', date: '$data_pedido' } },\n"
            "      Quantidade: { $sum: 1 }\n"
            "  } },\n"
            "  { $sort: { _id: 1 } }\n"
            "])"
        ),
        "pipeline": [
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$data_pedido"}},
                "Quantidade": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Evolução diária do volume de pedidos. Permite ver tendência, "
            "sazonalidade semanal e picos — insumo direto para planejamento "
            "de estoque e escala de atendimento."
        ),
    },
    {
        "id": "estoque_total",
        "titulo": "Quantidade geral de produto em estoque",
        "colecao": "produtos",
        "comando": (
            "db.produtos.aggregate([\n"
            "  { $group: { _id: null, Quantidade: { $sum: '$qtde_estoque' } } }\n"
            "])"
        ),
        "pipeline": [
            {"$group": {"_id": None, "Quantidade": {"$sum": "$qtde_estoque"}}},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Soma total de unidades em estoque. Visão macro para decisões de "
            "compra, capital de giro e capacidade de armazenagem."
        ),
    },
    {
        "id": "estoque_categoria",
        "titulo": "Estoque por categoria",
        "colecao": "produtos",
        "comando": (
            "db.produtos.aggregate([\n"
            "  { $group: {\n"
            "      _id: '$categoria',\n"
            "      Quantidade: { $sum: '$qtde_estoque' },\n"
            "      Produtos: { $sum: 1 }\n"
            "  } }\n"
            "])"
        ),
        "pipeline": [
            {"$group": {
                "_id": "$categoria",
                "Quantidade": {"$sum": "$qtde_estoque"},
                "Produtos": {"$sum": 1},
            }},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Concentração de estoque por categoria. Identifica onde está o "
            "capital parado e onde há excesso ou falta de itens — insumo "
            "para o time de compras."
        ),
    },
    {
        "id": "vendas_dia",
        "titulo": "Vendas por dia (R$)",
        "colecao": "pedidos",
        "comando": (
            "db.pedidos.aggregate([\n"
            "  { $match: { status_pedido: { $nin: ['Cancelado', 'Aguardando pagamento'] } } },\n"
            "  { $group: {\n"
            "      _id: { $dateToString: { format: '%Y-%m-%d', date: '$data_pedido' } },\n"
            "      Qtde_Pedidos: { $sum: 1 },\n"
            "      Total_Vendas: { $sum: '$valor_pago' }\n"
            "  } },\n"
            "  { $sort: { _id: 1 } }\n"
            "])"
        ),
        "pipeline": [
            {"$match": {"status_pedido": {"$nin": ["Cancelado", "Aguardando pagamento"]}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$data_pedido"}},
                "Qtde_Pedidos": {"$sum": 1},
                "Total_Vendas": {"$sum": "$valor_pago"},
            }},
            {"$sort": {"_id": 1}},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Fluxo diário de vendas em reais, excluindo pedidos cancelados ou "
            "não pagos. Visão central do financeiro e do gestor comercial."
        ),
    },
    {
        "id": "vendas_dia_categoria",
        "titulo": "Vendas por dia agrupado por categoria",
        "colecao": "pedidos",
        "comando": (
            "db.pedidos.aggregate([\n"
            "  { $match: { status_pedido: { $nin: ['Cancelado', 'Aguardando pagamento'] } } },\n"
            "  { $unwind: '$itens' },\n"
            "  { $lookup: { from: 'produtos', localField: 'itens.codigo_produto',\n"
            "               foreignField: 'codigo', as: 'produto' } },\n"
            "  { $unwind: '$produto' },\n"
            "  { $group: {\n"
            "      _id: { data: { $dateToString: { format: '%Y-%m-%d', date: '$data_pedido' } },\n"
            "             categoria: '$produto.categoria' },\n"
            "      Total_Vendas: { $sum: '$itens.preco' },\n"
            "      Qtde_Itens: { $sum: '$itens.quantidade' }\n"
            "  } },\n"
            "  { $sort: { '_id.data': 1, '_id.categoria': 1 } },\n"
            "  { $project: { _id: 0, Data: '$_id.data', Categoria: '$_id.categoria',\n"
            "                Total_Vendas: 1, Qtde_Itens: 1 } }\n"
            "])"
        ),
        "pipeline": [
            {"$match": {"status_pedido": {"$nin": ["Cancelado", "Aguardando pagamento"]}}},
            {"$unwind": "$itens"},
            {"$lookup": {
                "from": "produtos",
                "localField": "itens.codigo_produto",
                "foreignField": "codigo",
                "as": "produto",
            }},
            {"$unwind": "$produto"},
            {"$group": {
                "_id": {
                    "data": {"$dateToString": {"format": "%Y-%m-%d", "date": "$data_pedido"}},
                    "categoria": "$produto.categoria",
                },
                "Total_Vendas": {"$sum": "$itens.preco"},
                "Qtde_Itens": {"$sum": "$itens.quantidade"},
            }},
            {"$sort": {"_id.data": 1, "_id.categoria": 1}},
            {"$project": {
                "_id": 0,
                "Data": "$_id.data",
                "Categoria": "$_id.categoria",
                "Total_Vendas": 1,
                "Qtde_Itens": 1,
            }},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Cruza data × categoria: mostra quais categorias puxam as vendas em "
            "cada dia. É a base para o marketing decidir campanhas segmentadas "
            "e para o comprador ajustar mix de produtos."
        ),
    },
    {
        "id": "ticket_forma",
        "titulo": "Ticket médio por forma de pagamento",
        "colecao": "pedidos",
        "comando": (
            "db.pedidos.aggregate([\n"
            "  { $match: { status_pedido: { $nin: ['Cancelado', 'Aguardando pagamento'] } } },\n"
            "  { $group: { _id: '$forma_pagamento',\n"
            "              Total_Vendas: { $sum: '$valor_pago' },\n"
            "              Qtde_Pedidos: { $sum: 1 } } },\n"
            "  { $project: { _id: 0,\n"
            "                Forma_Pagamento: '$_id',\n"
            "                Total_Vendas: 1, Qtde_Pedidos: 1,\n"
            "                Ticket_Medio: { $divide: ['$Total_Vendas', '$Qtde_Pedidos'] } } },\n"
            "  { $sort: { Ticket_Medio: -1 } }\n"
            "])"
        ),
        "pipeline": [
            {"$match": {"status_pedido": {"$nin": ["Cancelado", "Aguardando pagamento"]}}},
            {"$group": {
                "_id": "$forma_pagamento",
                "Total_Vendas": {"$sum": "$valor_pago"},
                "Qtde_Pedidos": {"$sum": 1},
            }},
            {"$project": {
                "_id": 0,
                "Forma_Pagamento": "$_id",
                "Total_Vendas": 1,
                "Qtde_Pedidos": 1,
                "Ticket_Medio": {"$divide": ["$Total_Vendas", "$Qtde_Pedidos"]},
            }},
            {"$sort": {"Ticket_Medio": -1}},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Ticket médio por forma de pagamento. Mostra qual meio traz clientes "
            "de maior valor — insumo para o financeiro negociar taxas com "
            "adquirentes e para o marketing incentivar o meio mais rentável."
        ),
    },
    {
        "id": "ticket_dia",
        "titulo": "Ticket médio por dia",
        "colecao": "pedidos",
        "comando": (
            "db.pedidos.aggregate([\n"
            "  { $match: { status_pedido: { $nin: ['Cancelado', 'Aguardando pagamento'] } } },\n"
            "  { $group: { _id: { $dateToString: { format: '%Y-%m-%d', date: '$data_pedido' } },\n"
            "              Total_Vendas: { $sum: '$valor_pago' },\n"
            "              Qtde_Pedidos: { $sum: 1 } } },\n"
            "  { $project: { _id: 0, Periodo: '$_id', Total_Vendas: 1, Qtde_Pedidos: 1,\n"
            "                Ticket_Medio: { $divide: ['$Total_Vendas', '$Qtde_Pedidos'] } } },\n"
            "  { $sort: { Periodo: 1 } }\n"
            "])"
        ),
        "pipeline": [
            {"$match": {"status_pedido": {"$nin": ["Cancelado", "Aguardando pagamento"]}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$data_pedido"}},
                "Total_Vendas": {"$sum": "$valor_pago"},
                "Qtde_Pedidos": {"$sum": 1},
            }},
            {"$project": {
                "_id": 0,
                "Periodo": "$_id",
                "Total_Vendas": 1,
                "Qtde_Pedidos": 1,
                "Ticket_Medio": {"$divide": ["$Total_Vendas", "$Qtde_Pedidos"]},
            }},
            {"$sort": {"Periodo": 1}},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Ticket médio diário. Base para o marketing definir regras de frete "
            "grátis, cashback e promoções — só faz sentido quando o ticket "
            "médio do dia justifica o benefício."
        ),
    },
    {
        "id": "produtos_mais_vendidos",
        "titulo": "Produtos mais vendidos",
        "colecao": "pedidos",
        "comando": (
            "db.pedidos.aggregate([\n"
            "  { $match: { status_pedido: { $nin: ['Cancelado', 'Aguardando pagamento'] } } },\n"
            "  { $unwind: '$itens' },\n"
            "  { $group: { _id: '$itens.codigo_produto',\n"
            "              Qtde_Vendida: { $sum: '$itens.quantidade' },\n"
            "              Receita: { $sum: '$itens.preco' } } },\n"
            "  { $lookup: { from: 'produtos', localField: '_id',\n"
            "               foreignField: 'codigo', as: 'produto' } },\n"
            "  { $unwind: '$produto' },\n"
            "  { $project: { _id: 0, Codigo: '$_id', Descricao: '$produto.descricao',\n"
            "                Categoria: '$produto.categoria',\n"
            "                Qtde_Vendida: 1, Receita: 1 } },\n"
            "  { $sort: { Receita: -1 } }\n"
            "])"
        ),
        "pipeline": [
            {"$match": {"status_pedido": {"$nin": ["Cancelado", "Aguardando pagamento"]}}},
            {"$unwind": "$itens"},
            {"$group": {
                "_id": "$itens.codigo_produto",
                "Qtde_Vendida": {"$sum": "$itens.quantidade"},
                "Receita": {"$sum": "$itens.preco"},
            }},
            {"$lookup": {
                "from": "produtos",
                "localField": "_id",
                "foreignField": "codigo",
                "as": "produto",
            }},
            {"$unwind": "$produto"},
            {"$project": {
                "_id": 0,
                "Codigo": "$_id",
                "Descricao": "$produto.descricao",
                "Categoria": "$produto.categoria",
                "Qtde_Vendida": 1,
                "Receita": 1,
            }},
            {"$sort": {"Receita": -1}},
        ],
        "modo": "aggregate",
        "explicacao": (
            "Ranking de produtos por receita e quantidade. Insumo direto para "
            "reposição de estoque, negociação com fornecedores e priorização "
            "de campanhas de marketing nos itens que mais giram."
        ),
    },
]


# ============================================================
# EXECUÇÃO
# ============================================================
def executar(id_agregador: str) -> dict:
    """
    Executa o agregador pelo id e retorna:
      { 'total': int, 'amostra': list[dict] }
    A amostra é limitada a 5 linhas.
    """
    db = get_db()

    item = next((a for a in CATALOGO if a["id"] == id_agregador), None)
    if item is None:
        raise ValueError(f"Agregador '{id_agregador}' não encontrado.")

    colecao = db[item["colecao"]]

    # ---- Caso especial: count ----
    if item["modo"] == "count":
        total = colecao.count_documents({})
        return {
            "total": total,
            "amostra": [{"total": total}],
        }

    # ---- Caso padrão: aggregate ----
    resultados = list(colecao.aggregate(item["pipeline"]))
    total = len(resultados)
    amostra = resultados[:5]

    return {"total": total, "amostra": amostra}
