"""Registros criados no fechamento do prontuário: pagamento e consumo."""

FORMAS = ("PIX", "CARTAO", "DINHEIRO")


class Pagamento:
    def __init__(self, nome_pagador, numero_prontuario, forma, parcelas,
                 valor_medicamentos, valor_procedimentos, data_hora):
        self.nome_pagador = nome_pagador
        self.numero_prontuario = numero_prontuario
        self.forma = forma
        self.parcelas = parcelas                      # 1 quando não é cartão parcelado
        self.valor_medicamentos = valor_medicamentos
        self.valor_procedimentos = valor_procedimentos
        self.valor_total = valor_medicamentos + valor_procedimentos
        self.data_hora = data_hora


class Consumo:
    """Quem consumiu o quê: liga tutor e animal a cada medicamento baixado do estoque."""

    def __init__(self, cpf, nome_tutor, nome_animal, numero_prontuario, codigo, produto,
                 quantidade, valor, data_hora):
        self.cpf = cpf
        self.nome_tutor = nome_tutor
        self.nome_animal = nome_animal
        self.numero_prontuario = numero_prontuario
        self.codigo = codigo
        self.produto = produto
        self.quantidade = quantidade
        self.valor = valor                            # valor de venda do que foi baixado
        self.data_hora = data_hora