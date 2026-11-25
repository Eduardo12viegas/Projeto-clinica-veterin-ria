"""Diagnóstico: árvore de sistemas do animal.

A estrutura Arvore (em estruturas.py) é genérica. Aqui ficam os dados da clínica:
o que cada nó guarda (Componente) e a árvore pré-definida.
"""
from estruturas import Arvore, NoArvore

SAUDAVEL = "Saudável"
ALTERADO = "Alterado"


class Componente:
    """Dado guardado em cada nó: sistema, órgão ou estrutura do animal."""

    def __init__(self, nome, codigo=None):
        self.nome = nome
        self.codigo = codigo        # só os itens finais da hierarquia têm código
        self.estado = SAUDAVEL

    def __str__(self):
        texto = self.nome
        if self.codigo:
            texto += f" [{self.codigo}]"
        return f"{texto} - {self.estado}"


def criar_arvore_animal():
    raiz = NoArvore(Componente("Animal"))

    digestorio = raiz.adicionar_filho(NoArvore(Componente("Sistema digestório")))
    digestorio.adicionar_filho(NoArvore(Componente("Estômago", "DIG-01")))
    digestorio.adicionar_filho(NoArvore(Componente("Intestino", "DIG-02")))

    respiratorio = raiz.adicionar_filho(NoArvore(Componente("Sistema respiratório")))
    respiratorio.adicionar_filho(NoArvore(Componente("Pulmões", "RES-01")))
    respiratorio.adicionar_filho(NoArvore(Componente("Traqueia", "RES-02")))

    pele = raiz.adicionar_filho(NoArvore(Componente("Pele")))
    pele.adicionar_filho(NoArvore(Componente("Pelos", "PEL-01")))
    pele.adicionar_filho(NoArvore(Componente("Unhas", "PEL-02")))

    return Arvore(raiz)


def marcar_alterado(arvore, nome):
    """Procura o componente pelo nome (em pré-ordem) e marca como Alterado."""
    componente = arvore.buscar(lambda c: c.nome.strip().lower() == nome.strip().lower())
    if componente is None:
        raise ValueError(f"Componente '{nome}' não existe na árvore.")
    componente.estado = ALTERADO
    return componente


def exibir(arvore):
    """Mostra a árvore indentada, usando o percurso em pré-ordem."""
    for componente, nivel in arvore.pre_ordem():
        print("    " * nivel + "- " + str(componente))


# Teste rápido: rode `python diagnostico.py`.
if __name__ == "__main__":
    arvore = criar_arvore_animal()
    marcar_alterado(arvore, "estômago")
    marcar_alterado(arvore, "Pele")
    exibir(arvore)
    try:
        marcar_alterado(arvore, "Coração")
    except ValueError as erro:
        print("Erro esperado:", erro)
