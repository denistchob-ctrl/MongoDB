def executar(serie: str, periodos: int) -> dict:
    """Treina Prophet e retorna:
       {'fig_previsao': Figure, 'fig_componentes': Figure,
        'previsao': DataFrame}."""