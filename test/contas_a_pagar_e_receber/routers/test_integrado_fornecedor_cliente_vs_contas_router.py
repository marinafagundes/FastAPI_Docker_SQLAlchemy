from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from shared.database import Base
from shared.dependencies import get_db

# Essencial para melhorar a qualidade do código
# Era possível começar a aplicação escrevendo os testes
client = TestClient(app)

# Os testes apontam para um banco de dados local
# Esse arquivo vai conter os dados de teste
# Teste de banco de dados
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Cria uma nova engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Os testes a seguir são integrados, pois vão do controller até o banco de dados
# No caso dos testes, é interessante que o banco seja reiniciado a cada teste
def test_deve_listar_contas_de_um_fornecedor_cliente():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    client.post(
        "/fornecedor-cliente/",
        json={'nome': 'Casa da Musica'}
    )

    client.post(
        "/fornecedor-cliente/",
        json={'nome': 'Adde Treinamento'}
    )

    client.post(
        "/contas-a-pagar-e-receber/",
        json={
            'descricao': 'Curso de Python', 
            'valor': '1000.5', 
            'tipo': 'PAGAR',
            'fornecedor_cliente_id': 2
        }
    )

    client.post(
        "/contas-a-pagar-e-receber/",
        json={
            'descricao': 'Curso de Guitarra', 
            'valor': '5000', 
            'tipo': 'PAGAR',
            'fornecedor_cliente_id': 1
        }
    )

    client.post(
        "/contas-a-pagar-e-receber/",
        json={
            'descricao': 'Curso de Baixo', 
            'valor': '6000', 
            'tipo': 'PAGAR',
            'fornecedor_cliente_id': 1
        }
    )

    response_get_fornecedor_1 = client.get(
        f"/fornecedor-cliente/1/contas-a-pagar-e-receber"
    )

    assert response_get_fornecedor_1.status_code == 200
    assert len(response_get_fornecedor_1.json()) == 2

    response_get_fornecedor_2 = client.get(
        f"/fornecedor-cliente/2/contas-a-pagar-e-receber"
    )

    assert response_get_fornecedor_2.status_code == 200
    assert len(response_get_fornecedor_2.json()) == 1

def test_deve_retornar_uma_lista_vazia_de_contas_de_um_fornecedor_cliente():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    client.post(
        "/fornecedor-cliente/",
        json={'nome': 'Casa da Musica'}
    )

    response_get_fornecedor = client.get(
        f"/fornecedor-cliente/1/contas-a-pagar-e-receber"
    )

    assert response_get_fornecedor.status_code == 200
    assert len(response_get_fornecedor.json()) == 0