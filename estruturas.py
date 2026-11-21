class No:
    """Nó usado por Lista e Fila: guarda um dado e aponta para o próximo nó."""

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class Lista:
    """Lista encadeada.

    adicionar no fim: O(1)  |  buscar / obter / remover: O(n)
    """

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
        """Devolve o primeiro dado para o qual criterio(dado) é True (ou None)."""
        for dado in self:
            if criterio(dado):
                return dado
        return None

    def remover(self, criterio):
        """Remove e devolve o primeiro dado que satisfaz o critério (ou None)."""
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
    """Fila (FIFO) encadeada: o primeiro a entrar é o primeiro a sair.

    enfileirar / desenfileirar / primeiro: O(1)
    """

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
        """Tira e devolve o primeiro da fila (ou None se estiver vazia)."""
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

    def vazia(self):
        return self.tamanho == 0

    def __len__(self):
        return self.tamanho

    def __iter__(self):
        atual = self.inicio
        while atual is not None:
            yield atual.dado
            atual = atual.proximo