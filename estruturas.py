"""Estruturas de dados genéricas, feitas à mão (sem list/dict/deque guardando dados)."""

class No:

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class Lista:
    """Lista encadeada."""

    def __init__(self):
        self.inicio = None
        self.fim = None
        self.tamanho = 0

    def adicionar(self, dado):
        novo = No(dado)
        if self.fim is None:          # lista vazia: o novo nó é início e fim
            self.inicio = novo
        else:
            self.fim.proximo = novo
        self.fim = novo
        self.tamanho += 1

    def buscar(self, criterio):
        for dado in self:
            if criterio(dado):
                return dado
        return None

    def remover(self, criterio):
        anterior, atual = None, self.inicio
        while atual is not None:
            if criterio(atual.dado):
                if anterior is None:                  # era o primeiro nó
                    self.inicio = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                if atual is self.fim:                 # era o último nó
                    self.fim = anterior
                self.tamanho -= 1
                return atual.dado
            anterior, atual = atual, atual.proximo
        return None

    def vazia(self):
        return self.tamanho == 0

    def __len__(self):
        return self.tamanho

    def __iter__(self):
        """Permite usar `for item in lista`."""
        atual = self.inicio
        while atual is not None:
            yield atual.dado
            atual = atual.proximo


class Fila:

    def __init__(self):
        self.inicio = None
        self.fim = None
        self.tamanho = 0

    def enfileirar(self, dado):
        novo = No(dado)
        if self.fim is None:
            self.inicio = novo
        else:
            self.fim.proximo = novo
        self.fim = novo
        self.tamanho += 1

    def desenfileirar(self):
       
        if self.inicio is None:
            return None
        dado = self.inicio.dado
        self.inicio = self.inicio.proximo
        if self.inicio is None:       # a fila esvaziou
            self.fim = None
        self.tamanho -= 1
        return dado

    def primeiro(self):
        """Espia o primeiro da fila sem remover (ou None)."""
        return None if self.inicio is None else self.inicio.dado

    def ultimo(self):
        """Espia o último da fila (o que entrou por último) sem remover (ou None)."""
        return None if self.fim is None else self.fim.dado

    def filtrar(self, manter):
        removidos = Lista()
        for _ in range(self.tamanho):
            dado = self.desenfileirar()
            if manter(dado):
                self.enfileirar(dado)
            else:
                removidos.adicionar(dado)
        return removidos

    def vazia(self):
        return self.tamanho == 0

    def __len__(self):
        return self.tamanho

    def __iter__(self):
        atual = self.inicio
        while atual is not None:
            yield atual.dado
            atual = atual.proximo


class NoArvore:

    def __init__(self, dado):
        self.dado = dado
        self.filhos = Lista()

    def adicionar_filho(self, filho):
        self.filhos.adicionar(filho)
        return filho


class Arvore:

    def __init__(self, raiz):
        self.raiz = raiz

    def pre_ordem(self):
        """Percurso em profundidade (pré-ordem): primeiro o nó, depois os filhos.
        Devolve pares (dado, nivel); o nível serve para indentar na hora de exibir.
        """
        return self._pre_ordem(self.raiz, 0)

    def _pre_ordem(self, no, nivel):
        yield no.dado, nivel
        for filho in no.filhos:
            yield from self._pre_ordem(filho, nivel + 1)

    def buscar(self, criterio):
        """Devolve o primeiro dado (em pré-ordem) que satisfaz criterio(dado), ou None."""
        for dado, _ in self.pre_ordem():
            if criterio(dado):
                return dado
        return None