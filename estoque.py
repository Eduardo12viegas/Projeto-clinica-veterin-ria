"""Estoque de medicamentos, vacinas e materiais.
Combinação de estruturas: Lista + Fila."""
from datetime import date

from estruturas import Fila, Lista


class Lote:
    """Uma compra do produto: pode ter fornecedor, preços e datas diferentes de outra."""

    def __init__(self, fornecedor, preco_compra, preco_venda, data_compra, validade,
                 quantidade):
        self.fornecedor = fornecedor
        self.preco_compra = preco_compra
        self.preco_venda = preco_venda
        self.data_compra = data_compra
        self.validade = validade
        self.quantidade = quantidade


class Produto:
    def __init__(self, nome, codigo, minimo):
        self.nome = nome
        self.codigo = codigo
        self.minimo = minimo        # abaixo disso o sistema emite alerta
        self.lotes = Fila()         # Fila de Lote: o mais antigo fica na frente

    def quantidade_total(self):
        """Soma a quantidade de todos os lotes. O(l), l = nº de lotes do produto."""
        total = 0
        for lote in self.lotes:
            total += lote.quantidade
        return total


class Perda:
    """Registro de um lote descartado por estar vencido."""

    def __init__(self, codigo, produto, quantidade, custo, validade, data_descarte):
        self.codigo = codigo
        self.produto = produto
        self.quantidade = quantidade
        self.custo = custo
        self.validade = validade
        self.data_descarte = data_descarte


class Estoque:
    def __init__(self):
        self.produtos = Lista()     # Lista de Produto (cada um com sua Fila de Lote)
        self.perdas = Lista()       # Lista de Perda

    # ------------------------------------------------------------------- compras
    def buscar_produto(self, codigo):
        """Busca por código. O(n), n = nº de produtos."""
        codigo = codigo.strip().upper()
        return self.produtos.buscar(lambda p: p.codigo == codigo)

    def registrar_compra(self, nome, codigo, fornecedor, preco_compra, preco_venda,
                         quantidade, validade, data_compra=None, minimo=None):
        """Registra um lote novo. Se o produto já existe, o lote entra no fim da fila dele."""
        data_compra = data_compra or date.today()
        codigo = codigo.strip().upper()
        if not nome.strip() or not codigo:
            raise ValueError("Informe o nome e o código do produto.")
        if quantidade <= 0:
            raise ValueError("A quantidade comprada deve ser maior que zero.")
        if preco_compra < 0 or preco_venda < 0:
            raise ValueError("Os preços não podem ser negativos.")
        if validade < data_compra:
            raise ValueError("A validade não pode ser anterior à data da compra.")

        produto = self.buscar_produto(codigo)
        if produto is None:
            produto = Produto(nome.strip(), codigo, 1 if minimo is None else minimo)
            self.produtos.adicionar(produto)
        elif minimo is not None:
            produto.minimo = minimo
        produto.lotes.enfileirar(Lote(fornecedor.strip(), preco_compra, preco_venda,
                                      data_compra, validade, quantidade))
        return produto

    # ------------------------------------------------------------------- validade
    def descartar_vencidos(self, hoje=None):
        """Tira de cada fila os lotes vencidos e registra cada um como perda."""
        hoje = hoje or date.today()
        for produto in self.produtos:
            vencidos = produto.lotes.filtrar(lambda lote: lote.validade >= hoje)
            for lote in vencidos:
                self.perdas.adicionar(Perda(produto.codigo, produto.nome, lote.quantidade,
                                            lote.quantidade * lote.preco_compra,
                                            lote.validade, hoje))

    # --------------------------------------------------------------------- saídas
    def baixar(self, codigo, quantidade, hoje=None):
        """Dá baixa consumindo primeiro o lote mais antigo, depois o seguinte, e assim
        por diante. Devolve o valor de venda do que saiu (será usado no prontuário)."""

        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        self.descartar_vencidos(hoje)       # vencido nunca pode ser usado
        produto = self._produto_ou_erro(codigo)
        if produto.quantidade_total() < quantidade:
            raise ValueError(f"Estoque insuficiente de {produto.nome}: "
                             f"{produto.quantidade_total()} un disponíveis.")
        return self._consumir(produto, quantidade)

    def _consumir(self, produto, quantidade):
        restante, valor = quantidade, 0
        while restante > 0:
            lote = produto.lotes.primeiro()         # sempre o mais antigo
            usar = min(restante, lote.quantidade)
            lote.quantidade -= usar
            valor += usar * lote.preco_venda
            restante -= usar
            if lote.quantidade == 0:                # lote esgotado: sai da fila
                produto.lotes.desenfileirar()
        return valor

    # ---------------------------------------------------------- ajuste e alertas
    def ajustar_quantidade(self, codigo, nova_quantidade, hoje=None):
        """Ajuste de inventário: faz a quantidade total do produto ficar igual a
        nova_quantidade. Se faltar, tira dos lotes mais antigos; se sobrar, soma no
        lote mais recente."""
        if nova_quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")
        self.descartar_vencidos(hoje)
        produto = self._produto_ou_erro(codigo)
        diferenca = nova_quantidade - produto.quantidade_total()
        if diferenca < 0:
            self._consumir(produto, -diferenca)
        elif diferenca > 0:
            lote = produto.lotes.ultimo()
            if lote is None:
                raise ValueError("Não há lote para receber o ajuste; registre uma compra.")
            lote.quantidade += diferenca

    def quantidade_disponivel(self, codigo, hoje=None):
        """Quantidade total do produto, depois de descartar os lotes vencidos."""
        self.descartar_vencidos(hoje)
        return self._produto_ou_erro(codigo).quantidade_total()

    def alertas(self, hoje=None):
        """Produtos cuja quantidade total (sem os vencidos) está abaixo do mínimo."""
        self.descartar_vencidos(hoje)
        return [p for p in self.produtos if p.quantidade_total() < p.minimo]

    def _produto_ou_erro(self, codigo):
        produto = self.buscar_produto(codigo)
        if produto is None:
            raise ValueError("Produto não encontrado.")
        return produto


# Teste rápido: rode `python estoque.py`.
if __name__ == "__main__":
    from datetime import timedelta

    hoje = date.today()
    estoque = Estoque()
    # mesmo produto, dois lotes: o de 30 dias atrás é o mais antigo
    estoque.registrar_compra("Vermífugo", "VER01", "VetPharma", 10.0, 25.0, 5,
                             hoje + timedelta(days=200), hoje - timedelta(days=30), minimo=8)
    estoque.registrar_compra("Vermífugo", "VER01", "VetPharma", 12.0, 28.0, 10,
                             hoje + timedelta(days=300), hoje - timedelta(days=5))
    # vacina com um lote que já venceu
    estoque.registrar_compra("Vacina antirrábica", "VAC01", "ImunoVet", 20.0, 45.0, 4,
                             hoje - timedelta(days=1), hoje - timedelta(days=90), minimo=3)

    verm = estoque.buscar_produto("VER01")
    print("Vermífugo - total:", verm.quantidade_total())

    valor = estoque.baixar("VER01", 7)       # 5 do lote mais antigo + 2 do seguinte
    print("Baixa de 7 un. Valor de venda:", valor)
    print("Lotes que sobraram:", [l.quantidade for l in verm.lotes])

    print("Alertas:", [p.nome for p in estoque.alertas()])
    for perda in estoque.perdas:
        print(f"Perda registrada: {perda.quantidade}x {perda.produto} "
              f"(custo R$ {perda.custo:.2f})")

    estoque.ajustar_quantidade("VER01", 12)
    print("Depois do ajuste para 12:", verm.quantidade_total())
    try:
        estoque.baixar("VER01", 100)
    except ValueError as erro:
        print("Erro esperado:", erro)