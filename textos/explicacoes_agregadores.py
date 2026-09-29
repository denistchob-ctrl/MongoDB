# textos/explicacoes_agregadores.py
# ------------------------------------------------------------
# Preencha os campos conforme sua análise de negócio.
# Deixe em branco os que ainda não decidiu.
# ------------------------------------------------------------

EXPLICACOES = {
    "pedidos_por_status": {
        "negocio": "Acompanhar a distribuição dos pedidos ao longo do funil.",
        "setor": "Operações / Atendimento",
        "metrica": "Quantidade de pedidos por status",
        "recomendacao": "Investigar status com acúmulo anormal.",
    },
    "pedidos_por_data": {
        "negocio": "Ver a evolução diária da demanda.",
        "setor": "Planejamento",
        "metrica": "Pedidos por dia",
        "recomendacao": "Ajustar escala de atendimento.",
    },
    "estoque_total": {
        "negocio": "Saber o volume total em estoque.",
        "setor": "Logística",
        "metrica": "Soma de qtde_estoque",
        "recomendacao": "Comparar com giro médio.",
    },
    "estoque_por_categoria": {
        "negocio": "Identificar concentração de capital por categoria.",
        "setor": "Financeiro / Compras",
        "metrica": "Estoque por categoria",
        "recomendacao": "Reduzir estoque parado.",
    },
    "vendas_por_dia": {
        "negocio": "Acompanhar o fluxo diário de vendas.",
        "setor": "Financeiro",
        "metrica": "Total vendido por dia",
        "recomendacao": "Cruzar com metas diárias.",
    },
    "vendas_por_dia_categoria": {
        "negocio": "Ver quais categorias puxam as vendas em cada dia.",
        "setor": "Marketing / Compras",
        "metrica": "Vendas por dia e categoria",
        "recomendacao": "Reforçar estoque das categorias líderes.",
    },
    "ticket_medio_forma": {
        "negocio": "Entender o ticket por forma de pagamento.",
        "setor": "Financeiro",
        "metrica": "Ticket médio por forma",
        "recomendacao": "Incentivar meios com maior ticket.",
    },
    "ticket_medio_dia": {
        "negocio": "Acompanhar o ticket médio diário.",
        "setor": "Financeiro / Marketing",
        "metrica": "Ticket médio por dia",
        "recomendacao": "Definir regras de frete grátis.",
    },
    "produtos_mais_vendidos": {
        "negocio": "Ranquear produtos por receita.",
        "setor": "Compras / Marketing",
        "metrica": "Receita e quantidade por produto",
        "recomendacao": "Priorizar reposição dos top 10.",
    },
}
