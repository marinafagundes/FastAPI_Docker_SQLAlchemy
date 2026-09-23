def test_criar_e_listar_fornecedor_cliente(client):
    r1 = client.post("/fornecedor-cliente", json={"nome": "CPFL"})
    r2 = client.post("/fornecedor-cliente", json={"nome": "Sanasa"})

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert client.get("/fornecedor-cliente").json() == [
        {"id": 1, "nome": "CPFL"},
        {"id": 2, "nome": "Sanasa"},
    ]

def test_buscar_fornecedor_cliente_por_id(client):
    criado = client.post("/fornecedor-cliente", json={"nome": "CPFL"}).json()
    resposta = client.get(f"/fornecedor-cliente/{criado['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "CPFL"

def test_fornecedor_cliente_inexistente_retorna_404(client):
    resposta = client.get("/fornecedor-cliente/100")
    assert resposta.status_code == 404

def test_atualizar_fornecedor_cliente(client):
    criado = client.post("/fornecedor-cliente", json={"nome": "Extra"}).json()
    resposta = client.put(f"/fornecedor-cliente/{criado['id']}", json={"nome": "Giga Extra"})

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Giga Extra"

def test_excluir_fornecedor_cliente(client):
    criado = client.post("/fornecedor-cliente", json={"nome": "Extra"}).json()
    resposta = client.delete(f"/fornecedor-cliente/{criado['id']}")

    assert resposta.status_code == 204
    assert client.get("/fornecedor-cliente").json() == []

def test_validar_nome_fornecedor_cliente(client):
    assert client.post("/fornecedor-cliente", json={"nome": "A"}).status_code == 422
    assert client.post("/fornecedor-cliente", json={"nome": "A" * 256}).status_code == 422
