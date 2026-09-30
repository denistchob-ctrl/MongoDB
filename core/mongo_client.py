# core/mongo_client.py
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME, DB_USERNAME

def get_db():
    """Retorna o database configurado."""
    print(f"Conexão : {MONGO_URI}")
    print(f"USERNAME: {DB_USERNAME}")
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def ping():
    """Testa a conexão."""
    try:
        print("Tentando realizar a conexão")
        get_db().command("ping")
        print("Conexão realizada com sucesso")
        return True
    except Exception:
        print("Erro na conexão durante monge_client.py")
        return False

def limpar_base():
    """Remove todas as coleções do projeto."""
    db = get_db()
    for col in ["produtos", "clientes", "pedidos"]:
        db[col].drop()

def estatisticas_colecoes():
    """Retorna um dict com contagem + amostra de cada coleção."""
    db = get_db()
    out = {}
    for col in ["produtos", "clientes", "pedidos"]:
        colecao = db[col]
        out[col] = {
            "total": colecao.count_documents({}),
            "amostra": colecao.find_one() or {},
        }
    return out
