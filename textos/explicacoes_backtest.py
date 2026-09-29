# textos/explicacoes_backtest.py
EXPLICACOES = {
    "diario": {
        "titulo": "Backtest diário",
        "categoria": "Alta variabilidade",
        "corpo": """
        Erro elevado devido ao ruído inerente às vendas diárias.
        Útil apenas para acompanhamento, não para decisão.
        """,
    },
    "semanal": {
        "titulo": "Backtest semanal",
        "categoria": "Uso operacional",
        "corpo": """
        Melhor equilíbrio entre precisão e granularidade.
        Recomendado para reposição de estoque e escala de equipe.
        """,
    },
    "mensal": {
        "titulo": "Backtest mensal",
        "categoria": "Uso estratégico",
        "corpo": """
        Maior precisão. Ideal para orçamento, metas e planejamento financeiro.
        """,
    },
}
