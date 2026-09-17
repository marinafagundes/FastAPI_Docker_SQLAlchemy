client.post(
        "/contas-a-pagar-e-receber/",
        json={'descricao': 'Aluguel', 'valor': '1000.5', 'tipo': 'PAGAR'}
    )

    client.post(
        "/contas-a-pagar-e-receber/",
        json={'descricao': 'Salário', 'valor': '5000', 'tipo': 'RECEBER'}
    )