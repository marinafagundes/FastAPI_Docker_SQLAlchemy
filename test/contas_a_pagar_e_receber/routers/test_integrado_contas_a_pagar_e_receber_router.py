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
def test_deve_listar_contas_a_pagar_e_receber():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    client.post(
        "/contas-a-pagar-e-receber/",
        json={'descricao': 'Aluguel', 'valor': '1000.5', 'tipo': 'PAGAR'}
    )

    client.post(
        "/contas-a-pagar-e-receber/",
        json={'descricao': 'Salário', 'valor': '5000', 'tipo': 'RECEBER'}
    )

    response = client.get("/contas-a-pagar-e-receber/")
    assert response.status_code == 200
    assert response.json() == [
        {'id': 1, 'descricao': 'Aluguel', 'valor': '1000.5', 'tipo': 'PAGAR'},
        {'id': 2, 'descricao': 'Salário', 'valor': '5000', 'tipo': 'RECEBER'}
    ]

def test_deve_criar_conta_a_pagar_e_receber():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    nova_conta = {
        "descricao": "Curso de Python",
        "valor": 333,
        "tipo": "PAGAR"
    }

    # Criar uma cópia do dicionário para evitar mutação
    nova_conta_copy = nova_conta.copy()

    # Temporariamente (enquanto não está automatizado),
    # Adicionar id manualmente
    nova_conta_copy = nova_conta.copy()
    nova_conta_copy["id"] = 1
    nova_conta_copy["valor"] = str(nova_conta_copy["valor"])

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json=nova_conta
    )

    assert response.status_code == 201
    assert response.json() == nova_conta_copy

# No caso do CRUD, começamos pelo teste --> TDD (Test Driven Development)
# Atualização/Update
def test_deve_atualizar_conta_a_pagar_e_receber():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR"}
    )

    id_da_conta_a_pagar_e_receber = response.json()['id']

    response_put = client.put(
        # Padrão do método PUT na API REST --> acrescentar id na URL
        "/contas-a-pagar-e-receber/{id_da_conta_a_pagar_e_receber}",
        json={"descricao": "Curso de Python", "valor": 111, "tipo": "PAGAR"}
    )

    assert response_put.status_code == 200



def test_deve_retornar_erro_quando_exceder_a_descricao():
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "0123456789012345678901234567890", "valor": 333, "tipo": "PAGAR"}
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","descricao"]

def test_deve_retornar_erro_quando_a_descricao_for_menor_do_que_o_necessario():
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "01", "valor": 333, "tipo": "PAGAR"}
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","descricao"]

def test_deve_retornar_erro_quando_o_valor_for_zero_ou_menor():
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Test", "valor": 0, "tipo": "PAGAR"}
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","valor"]

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Test", "valor": -1, "tipo": "PAGAR"}
    )
    
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","valor"]

def test_deve_retornar_erro_quando_o_tipo_for_invalido():
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Test", "valor": 100, "tipo": "INVALIDO"}
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","tipo"]
    


