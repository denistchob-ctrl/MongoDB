# core/operadores_catalogo.py
# ------------------------------------------------------------
# Catálogo dos operadores MongoDB usados no projeto.
# Cada item tem: id, titulo, categoria, comando, colecao, explicacao.
# ------------------------------------------------------------
from core.mongo_client import get_db


# ============================================================
# CATÁLOGO
# ============================================================
CATALOGO = [
    {
        "id": "eq_cliente",
        "titulo": "$eq — Igualdade (clientes)",
        "categoria": "Comparação",
        "colecao": "clientes",
        "comando": 'db.clientes.find( { codigo: { $eq: 100 } } )',
        "filtro": {"codigo": {"$eq": 100}},
        "projecao": None,
        "explicacao": (
            "O operador $eq seleciona documentos em que o campo é IGUAL ao valor "
            "informado. É o operador de comparação mais básico e equivale à "
            "igualdade direta ( campo: valor ). Usado aqui para localizar um "
            "cliente específico pelo seu código."
        ),
    },
    {
        "id": "eq_produto_unidade",
        "titulo": "$eq — Igualdade (unidade de produto)",
        "categoria": "Comparação",
        "colecao": "produtos",
        "comando": 'db.produtos.find( { unidade: { $eq: "CX" } } )',
        "filtro": {"unidade": {"$eq": "CX"}},
        "projecao": None,
        "explicacao": (
            "Seleciona produtos cuja unidade de medida é exatamente 'CX' (caixa). "
            "Útil para separar produtos vendidos em caixa daqueles vendidos em "
            "unidade — afeta cálculo de frete, embalagem e inventário."
        ),
    },
    {
        "id": "ne_forma",
        "titulo": "$ne — Diferente (forma de pagamento)",
        "categoria": "Comparação",
        "colecao": "pedidos",
        "comando": 'db.pedidos.find( { forma_pagamento: { $ne: "PIX" } } )',
        "filtro": {"forma_pagamento": {"$ne": "PIX"}},
        "projecao": None,
        "explicacao": (
            "Retorna pedidos cuja forma de pagamento NÃO é PIX. Permite comparar "
            "o comportamento de clientes que usam meios tradicionais (boleto, "
            "cartão) versus os que adotaram pagamento instantâneo — informação "
            "relevante para o setor financeiro."
        ),
    },
    {
        "id": "lt_cliente",
        "titulo": "$lt — Menor que (clientes)",
        "categoria": "Comparação",
        "colecao": "clientes",
        "comando": 'db.clientes.find( { codigo: { $lt: 102 } } )',
        "filtro": {"codigo": {"$lt": 102}},
        "projecao": None,
        "explicacao": (
            "Retorna clientes com código ESTRITAMENTE MENOR que 102. O $lt é "
            "exclusivo — não inclui o valor de comparação. Útil em relatórios "
            "de faixas de cadastro (ex.: clientes com código antigo)."
        ),
    },
    {
        "id": "lte_produto",
        "titulo": "$lte — Menor ou igual (produtos)",
        "categoria": "Comparação",
        "colecao": "produtos",
        "comando": 'db.produtos.find( { codigo: { $lte: 6 } } )',
        "filtro": {"codigo": {"$lte": 6}},
        "projecao": None,
        "explicacao": (
            "Retorna produtos com código MENOR OU IGUAL a 6. Diferente do $lt, "
            "INCLUI o valor limite. É o operador correto quando o intervalo é "
            "fechado no topo (por exemplo, 'do 1 ao 6, inclusive')."
        ),
    },
    {
        "id": "gt_pedido",
        "titulo": "$gt — Maior que (pedidos)",
        "categoria": "Comparação",
        "colecao": "pedidos",
        "comando": 'db.pedidos.find( { numero_pedido: { $gt: 1010 } } )',
        "filtro": {"numero_pedido": {"$gt": 1010}},
        "projecao": None,
        "explicacao": (
            "Retorna pedidos com número maior que 1010. Comum para extrair "
            "'pedidos recentes' em uma janela temporal — por exemplo, durante "
            "auditoria de um período específico."
        ),
    },
    {
        "id": "gte_itens",
        "titulo": "$gte em subdocumento — Itens com quantidade ≥ 2",
        "categoria": "Comparação em array",
        "colecao": "pedidos",
        "comando": (
            'db.pedidos.find(\n'
            '  { "itens.quantidade": { $gte: 2 } },\n'
            '  { _id: 0, numero_pedido: 1, "itens.codigo_produto": 1, "itens.quantidade": 1 }\n'
            ')'
        ),
        "filtro": {"itens.quantidade": {"$gte": 2}},
        "projecao": {"_id": 0, "numero_pedido": 1,
                     "itens.codigo_produto": 1, "itens.quantidade": 1},
        "explicacao": (
            "Usa a 'dot notation' (itens.quantidade) para acessar um campo dentro "
            "de um array de subdocumentos. Retorna pedidos que possuem ALGUM item "
            "com quantidade ≥ 2. Fundamental em modelos embutidos — é a forma "
            "idiomática do MongoDB navegar por arrays."
        ),
    },
    {
        "id": "all_tags",
        "titulo": "$all — Produtos com as DUAS tags",
        "categoria": "Array",
        "colecao": "produtos",
        "comando": 'db.produtos.find( { tags: { $all: ["informatica", "gamer"] } } )',
        "filtro": {"tags": {"$all": ["informatica", "gamer"]}},
        "projecao": None,
        "explicacao": (
            "$all exige que o array contenha TODOS os elementos informados. "
            "Útil para buscas facetadas ('quero produtos que sejam ao mesmo "
            "tempo informática E gamer'). É mais restritivo que $in."
        ),
    },
    {
        "id": "in_tags",
        "titulo": "$in — Produtos com QUALQUER das tags",
        "categoria": "Array",
        "colecao": "produtos",
        "comando": 'db.produtos.find( { tags: { $in: ["periferico", "gamer"] } } )',
        "filtro": {"tags": {"$in": ["periferico", "gamer"]}},
        "projecao": None,
        "explicacao": (
            "$in casa com documentos em que o array contém PELO MENOS UM dos "
            "valores. É o operador típico para filtros de vitrine ('mostre "
            "periféricos OU gamers')."
        ),
    },
    {
        "id": "nin_tags",
        "titulo": "$nin — Produtos SEM nenhuma das tags",
        "categoria": "Array",
        "colecao": "produtos",
        "comando": 'db.produtos.find( { tags: { $nin: ["gabinete", "fonte"] } } )',
        "filtro": {"tags": {"$nin": ["gabinete", "fonte"]}},
        "projecao": None,
        "explicacao": (
            "$nin é o oposto do $in: retorna documentos cujo array NÃO contém "
            "nenhum dos valores informados. Útil para 'excluir categorias' em "
            "relatórios ou para localizar produtos fora do padrão esperado."
        ),
    },
    {
        "id": "or_status",
        "titulo": "$or — Pedidos com um OU outro status",
        "categoria": "Lógico",
        "colecao": "pedidos",
        "comando": (
            'db.pedidos.find(\n'
            '  { $or: [ { status_pedido: "Aguardando pagamento" },\n'
            '           { status_pedido: "Em processamento" } ] },\n'
            '  { _id: 0, data_pedido: 0, valor_pago: 0, itens: 0 }\n'
            ')'
        ),
        "filtro": {"$or": [
            {"status_pedido": "Aguardando pagamento"},
            {"status_pedido": "Em processamento"},
        ]},
        "projecao": {"_id": 0, "data_pedido": 0, "valor_pago": 0, "itens": 0},
        "explicacao": (
            "$or retorna documentos que satisfazem PELO MENOS UMA das condições. "
            "Aplicado aqui para listar todos os pedidos que estão 'em andamento' "
            "(aguardando pagamento OU em processamento) — uma visão de pipeline."
        ),
    },
    {
        "id": "nor_status",
        "titulo": "$nor — Pedidos que NÃO estão em nenhum dos status",
        "categoria": "Lógico",
        "colecao": "pedidos",
        "comando": (
            'db.pedidos.find(\n'
            '  { $nor: [ { status_pedido: "Entregue" },\n'
            '            { status_pedido: "Cancelado" },\n'
            '            { status_pedido: "Aguardando pagamento" } ] },\n'
            '  { _id: 0, data_pedido: 0, valor_pago: 0, itens: 0,\n'
            '    codigo_cliente: 0, forma_pagamento: 0 }\n'
            ')'
        ),
        "filtro": {"$nor": [
            {"status_pedido": "Entregue"},
            {"status_pedido": "Cancelado"},
            {"status_pedido": "Aguardando pagamento"},
        ]},
        "projecao": {"_id": 0, "data_pedido": 0, "valor_pago": 0, "itens": 0,
                     "codigo_cliente": 0, "forma_pagamento": 0},
        "explicacao": (
            "$nor é a negação do $or: retorna documentos que NÃO casam com "
            "NENHUMA das condições. Aqui serve para isolar 'pedidos que ainda "
            "não terminaram' — nem entregues, nem cancelados."
        ),
    },
    {
        "id": "regex_nome",
        "titulo": "$regex — Nomes que contêm 'Carlos'",
        "categoria": "Texto",
        "colecao": "clientes",
        "comando": 'db.clientes.find( { nome: { $regex: /Carlos/ } },\n'
                   '                   { _id: 0, data_nascimento: 0 } )',
        "filtro": {"nome": {"$regex": "Carlos"}},
        "projecao": {"_id": 0, "data_nascimento": 0},
        "explicacao": (
            "$regex permite buscas por padrão textual. Sem âncora (^ ou $), "
            "casa em QUALQUER posição da string. Aqui, localiza clientes com "
            "'Carlos' em qualquer parte do nome — útil em CRM e busca por "
            "semelhança."
        ),
    },
    {
        "id": "mod_par",
        "titulo": "$mod — Itens com quantidade PAR",
        "categoria": "Aritmético",
        "colecao": "pedidos",
        "comando": (
            'db.pedidos.find(\n'
            '  { "itens.quantidade": { $mod: [2, 0] } },\n'
            '  { _id: 0, numero_pedido: 1, "itens.codigo_produto": 1, "itens.quantidade": 1 }\n'
            ')'
        ),
        "filtro": {"itens.quantidade": {"$mod": [2, 0]}},
        "projecao": {"_id": 0, "numero_pedido": 1,
                     "itens.codigo_produto": 1, "itens.quantidade": 1},
        "explicacao": (
            "$mod aplica o operador módulo (resto da divisão). A sintaxe é "
            "[divisor, resto]. Aqui, [2, 0] retorna itens com quantidade PAR. "
            "É útil em auditorias, sorteios e verificações de padrão."
        ),
    },
    {
        "id": "exists_so",
        "titulo": "$exists — Produtos com campo 'sistema_operacional'",
        "categoria": "Existência",
        "colecao": "produtos",
        "comando": 'db.produtos.find( { "sistema_operacional": { $exists: true } } )',
        "filtro": {"sistema_operacional": {"$exists": True}},
        "projecao": None,
        "explicacao": (
            "$exists verifica se o campo está PRESENTE no documento. Como nem "
            "todo produto tem sistema operacional (só notebooks), este operador "
            "serve para listar apenas os que possuem essa característica — "
            "essencial em bases com campos opcionais."
        ),
    },
]


# ============================================================
# EXECUÇÃO
# ============================================================
def executar(id_operador: str) -> dict:
    """
    Executa o operador pelo id e retorna:
      { 'total': int, 'amostra': list[dict] }
    A amostra é limitada a 5 documentos.
    """
    db = get_db()

    item = next((o for o in CATALOGO if o["id"] == id_operador), None)
    if item is None:
        raise ValueError(f"Operador '{id_operador}' não encontrado no catálogo.")

    colecao = db[item["colecao"]]
    filtro = item["filtro"]
    projecao = item.get("projecao")

    total = colecao.count_documents(filtro)

    cursor = colecao.find(filtro, projecao).limit(5)
    amostra = list(cursor)

    return {"total": total, "amostra": amostra}
