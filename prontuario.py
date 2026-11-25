"""Prontuário de atendimento: tudo o que acontece com o animal dentro do consultório."""
from datetime import datetime

from diagnostico import criar_arvore_animal
from estruturas import Lista


class ItemMedicamento:
    """Medicamento (ou vacina/material) aplicado. O valor só é calculado no fechamento,
    quando a baixa do estoque diz de qual lote saiu cada unidade."""

    def __init__(self, codigo, nome, quantidade):
        self.codigo = codigo
        self.nome = nome
        self.quantidade = quantidade


class Procedimento:
    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor


class Prontuario:
    def __init__(self, numero, nome_animal, nome_tutor, cpf, veterinario, consultorio, queixa):
        self.numero = numero
        self.nome_animal = nome_animal
        self.nome_tutor = nome_tutor
        self.cpf = cpf
        self.veterinario = veterinario
        self.consultorio = consultorio              # número do consultório ocupado
        self.queixa = queixa
        self.data_hora = datetime.now()
        self.medicamentos = Lista()                 # Lista de ItemMedicamento
        self.procedimentos = Lista()                # Lista de Procedimento
        self.diagnostico = criar_arvore_animal()    # cada prontuário tem a sua árvore
        self.alta = False                           # só fecha depois da alta

    def valor_procedimentos(self):
        total = 0
        for procedimento in self.procedimentos:
            total += procedimento.valor
        return total