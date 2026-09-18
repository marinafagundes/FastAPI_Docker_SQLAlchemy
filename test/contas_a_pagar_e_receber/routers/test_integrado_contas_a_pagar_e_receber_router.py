from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contas_a_pagar_e_receber.routers.contas_a_pagar_e_receber_router import QUANTIDADE_PERMITIDA_POR_MES
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
        json={'descricao': 'Aluguel', 'valor': '1000.5', 'tipo': 'PAGAR', 'data_previsao': '2022-11-29'}
    )

    client.post(
        "/contas-a-pagar-e-receber/",
        json={'descricao': 'Salário', 'valor': '5000', 'tipo': 'RECEBER', 'data_previsao': '2022-11-29'}
    )

    response = client.get("/contas-a-pagar-e-receber/")
    assert response.status_code == 200
    assert response.json() == [
        {
            'id': 1, 'descricao': 'Aluguel', 'valor': '1000.5', 'tipo': 'PAGAR', 'fornecedor': None, 
            'data_baixa': None, 'valor_baixa': None, 'esta_baixada': False, 'data_previsao': '2022-11-29'
        },

        {
            'id': 2, 'descricao': 'Salário', 'valor': '5000', 'tipo': 'RECEBER', 'fornecedor': None, 
            'valor_baixa': None, 'esta_baixada': False, 'data_previsao': '2022-11-29'
        }
    ]

# No caso do CRUD, começamos pelo teste --> TDD (Test Driven Development)
# Atualização/Update
def test_deve_pegar_por_id():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", 'data_previsao': '2022-11-29'}
    )

    id_da_conta_a_pagar_e_receber = response.json()['id']

    response_get = client.get(
        # Padrão do método PUT na API REST --> acrescentar id na URL
        "/contas-a-pagar-e-receber/{id_da_conta_a_pagar_e_receber}"
    )

    assert response_get.status_code == 200
    assert response_get.json()['valor'] == 333
    assert response_get.json()['tipo'] == "PAGAR"
    assert response_get.json()['descricao'] == "Curso de Python"
    assert response_get.json()['data_previsao'] == "2022-11-29"

def test_deve_retornar_nao_encontrado_para_id_inexistente():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", 'data_previsao': '2022-11-29'}
    )

    response_get = client.get(
        # Padrão do método PUT na API REST --> acrescentar id na URL
        "/contas-a-pagar-e-receber/100"
    )

    assert response_get.status_code == 404

def test_deve_criar_conta_a_pagar_e_receber():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    nova_conta = {
        "descricao": "Curso de Python",
        "valor": 333,
        "tipo": "PAGAR", 
        "data_previsao": "2022-11-29"
    }

    # Criar uma cópia do dicionário para evitar mutação
    nova_conta_copy = nova_conta.copy()

    # Temporariamente (enquanto não está automatizado),
    # Adicionar id manualmente
    nova_conta_copy = nova_conta.copy()
    nova_conta_copy["id"] = 1
    nova_conta_copy["fornecedor"] = None
    nova_conta_copy["data_baixa"] = None
    nova_conta_copy["valor_baixa"] = None
    nova_conta_copy["esta_baixada"] = False

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
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    id_da_conta_a_pagar_e_receber = response.json()['id']

    response_put = client.put(
        # Padrão do método PUT na API REST --> acrescentar id na URL
        "/contas-a-pagar-e-receber/{id_da_conta_a_pagar_e_receber}",
        json={"descricao": "Curso de Python", "valor": 111, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    assert response_put.status_code == 200
    assert response_put.json()['valor'] == 111

def test_deve_retornar_nao_encontrado_para_id_inexistente_na_atualizacao():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    response_put = client.put(
        "/contas-a-pagar-e-receber/100",
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    assert response_put.status_code == 404

# Delete
def test_deve_remover_conta_a_pagar_e_receber():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    id_da_conta_a_pagar_e_receber = response.json()['id']

    response_delete = client.delete(
        # Padrão do método DELETE na API REST --> acrescentar id na URL, não precisa de body
        "/contas-a-pagar-e-receber/{id_da_conta_a_pagar_e_receber}"
    )

    assert response_delete.status_code == 204

def test_deve_retornar_nao_encontrado_para_id_inexistente_na_remocao():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    response_delete = client.delete(
        "/contas-a-pagar-e-receber/100"
    )

    assert response_delete.status_code == 404

def test_deve_retornar_erro_quando_exceder_a_descricao():
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "0123456789012345678901234567890", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","descricao"]

def test_deve_retornar_erro_quando_a_descricao_for_menor_do_que_o_necessario():
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "01", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","descricao"]

def test_deve_retornar_erro_quando_o_valor_for_zero_ou_menor():
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Test", "valor": 0, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","valor"]

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Test", "valor": -1, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )
    
    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","valor"]

def test_deve_retornar_erro_quando_o_tipo_for_invalido():
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Test", "valor": 100, "tipo": "INVALIDO", "data_previsao": "2022-11-29"}
    )

    assert response.status_code == 422
    assert response.json()['detail'][0]['loc'] == ["body","tipo"]
    
def test_deve_criar_conta_a_pagar_e_receber_fornecedor_cliente_id():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    novo_fornecedor_cliente = {
        "nome": "Casa da Música"
    }

    client.post(
        "/fornecedor-cliente/",
        json=novo_fornecedor_cliente
    )

    nova_conta = {
        "descricao": "Curso de Guitarra",
        "valor": 250,
        "tipo": "PAGAR",
        "fornecedor_cliente_id": 1,
        "data_previsao": "2022-11-29"
    }

    # Criar uma cópia do dicionário para evitar mutação
    nova_conta_copy = nova_conta.copy()

    # Temporariamente (enquanto não está automatizado),
    # Adicionar id manualmente
    nova_conta_copy = nova_conta.copy()
    nova_conta_copy["id"] = 1
    nova_conta_copy["fornecedor"] = {
        "id": 1,
        "nome": "Casa da Música"
    }
    nova_conta_copy["data_baixa"] = None
    nova_conta_copy["valor_baixa"] = None
    nova_conta_copy["esta_baixada"] = False

    del nova_conta_copy["fornecedor_cliente_id"]

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json=nova_conta
    )

    assert response.status_code == 201
    assert response.json() == nova_conta_copy

def test_deve_retornar_erro_ao_inserir_uma_nova_conta_com_fornecedor_invalido():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    nova_conta = {
        "descricao": "Curso de Guitarra",
        "valor": 250,
        "tipo": "PAGAR", 
        "fornecedor_cliente_id": 1001, 
        "data_previsao": "2022-11-29"
    }
   
    response = client.post(
        "/contas-a-pagar-e-receber/",
        json=nova_conta
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Esse fornecedor não existe no banco de dados"

def test_deve_atualizar_conta_a_pagar_e_receber_com_fornecedor_cliente_id():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    novo_fornecedor_cliente = {
        "nome": "Código e CIA"
    }
    
    client.post(
        "/fornecedor-cliente/",
        json=novo_fornecedor_cliente
    )

    response = client.post(
            "/contas-a-pagar-e-receber/",
            json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
        )
    
    id_da_conta_a_pagar_e_receber = response.json()['id']
    
    response_put = client.put(
        # Padrão do método PUT na API REST --> acrescentar id na URL
        "/contas-a-pagar-e-receber/{id_da_conta_a_pagar_e_receber}",
        json={"descricao": "Curso de Python", "valor": 111, "tipo": "PAGAR", "fornecedor_cliente_id": 1, "data_previsao": "2022-11-29"}
        )
    
    assert response_put.status_code == 200
    assert response_put.json()['fornecedor_cliente_id'] == {"id": 1, "nome": "Código e CIA"}

def test_deve_retornar_erro_ao_atualizar_uma_nova_conta_com_fornecedor_invalido():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    response = client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )
        
    id_da_conta_a_pagar_e_receber = response.json()['id']
        
    response_put = client.put(
        # Padrão do método PUT na API REST --> acrescentar id na URL
        "/contas-a-pagar-e-receber/{id_da_conta_a_pagar_e_receber}",
        json={"descricao": "Curso de Python", "valor": 111, "tipo": "PAGAR", "fornecedor_cliente_id": 1001, "data_previsao": "2022-11-29"}
    )
        
    assert response_put.status_code == 200
    assert response_put.json()['fornecedor_cliente_id'] == {"id": 1, "nome": "Código e CIA"}

    assert response_put.status_code == 422
    assert response_put.json()["detail"] == "Esse fornecedor não existe no banco de dados"

def test_deve_baixar_conta():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )
        
    response_acao = client.post(
        "/contas-a-pagar-e-receber/1/baixar"
    )
        
    assert response_acao.status_code == 200
    assert response_acao.json()["esta_baixada"] is True
    assert response_acao.json()["valor"] == 333

def test_deve_baixar_conta_modificada():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    client.post(
        "/contas-a-pagar-e-receber/",
        json={"descricao": "Curso de Python", "valor": 333, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    client.post(
        "/contas-a-pagar-e-receber/1/baixar"
    )

    client.put(
        # Padrão do método PUT na API REST --> acrescentar id na URL
        "/contas-a-pagar-e-receber/1",
        json={"descricao": "Curso de Python", "valor": 444, "tipo": "PAGAR", "data_previsao": "2022-11-29"}
    )

    response_acao = client.post(
        "/contas-a-pagar-e-receber/1/baixar"
    )
        
    assert response_acao.status_code == 200
    assert response_acao.json()["esta_baixada"] is True
    assert response_acao.json()["valor"] == 444
    assert response_acao.json()["valor_baixa"] == 444

def test_limite_de_registros_mensais():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    respostas = []

    for i in range(0, QUANTIDADE_PERMITIDA_POR_MES + 1):
        resposta = client.post(
            "/contas-a-pagar-e-receber",
            json={
                'descricao': 'Curso Python',
                'valor': 200,
                'tipo': 'PAGAR',
                'data_previsao': '2022-11-29'
            }
        )

        respostas.append(resposta)

    ultima_resposta = respostas.pop()
    assert ultima_resposta.status_code == 422
    assert ultima_resposta.json()['detail'] == "Você não pode mais lançar contas para esse mês"
    assert all([r.status_code == 201 for r in respostas]) is True

def test_relatorio_gastos_previstos_por_mes_de_um_ano():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    valor = 10 
    mes = 1

    for i in range(1, 49):
        # Preenche com 0 à esquerda
        # Caso tenha menos de 2 dígitos
        mes_com_zero = str(mes).zfill(2)

        data = f"2022-{mes_com_zero}-01"
        client.post(
            "/contas-a-pagar-e-receber",
            json={
                'descricao': 'Teste',
                'valor': valor,
                'tipo': 'PAGAR',
                'data_previsao': data
            }
        )

        valor += 10

        if i % 4 == 0:
            mes += 1

    resposta = client.get(
        "contas-a-pagar-e-receber/previsao-gastos-do-mes"
    )

    assert resposta.status_code == 200
    resultados = resposta.json()
    assert len(resposta.json()) == 12

    valor = 0
    idx = 0
    valor_total = 0
    for i in range(1, 49):
        valor += 10
        valor_total += valor

        if i % 4 == 0:
            assert resultados[idx]['valor_total'] == valor_total
            valor_total = 0
            idx += 1

def test_relatorio_gastos_previstos_por_mes_sem_registros_no_banco():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    resposta = client.get(
        "contas-a-pagar-e-receber/previsao-gastos-do-mes"
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 0

def test_relatorio_gastos_previstos_por_mes_de_um_ano_sem_registros():
    Base.metadata.dropall(bind=engine)
    Base.metadata.createall(bind=engine)

    resposta = client.get(
        "contas-a-pagar-e-receber/previsao-gastos-do-mes/ano=1990"
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 0