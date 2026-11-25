"""Regras da clínica veterinária.

Reúne as regras de tutores e animais, atendimento, prontuário, estoque e pagamento.
Quem usa a Clinica (menu, interface) deve tratar ValueError, que é como ela avisa
que uma regra foi violada.
"""
from datetime import datetime

import diagnostico
from atendimento import ControleAtendimento, Solicitacao
from estoque import Estoque
from estruturas import Lista
from pagamento import FORMAS, Consumo, Pagamento
from prontuario import ItemMedicamento, Procedimento, Prontuario


class Animal:
    def __init__(self, nome, especie, raca, idade):
        self.nome = nome
        self.especie = especie
        self.raca = raca
        self.idade = idade


class Tutor:
    def __init__(self, nome, cpf, telefone):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.animais = Lista()      # Lista de Animal, sem limite de quantidade


class Clinica:
    def __init__(self, num_consultorios=2):
        self.tutores = Lista()      # Lista de Tutor (cada um com sua Lista de Animal)
        self.atendimento = ControleAtendimento(num_consultorios)
        self.estoque = Estoque()
        self.prontuarios = Lista()      # prontuários abertos
        self.pagamentos = Lista()       # histórico de pagamentos
        self.consumos = Lista()         # histórico: qual tutor/animal consumiu o quê
        self._proximo_numero = 1        # número do próximo prontuário

    # ---------------------------------------------------------------- auxiliares
    @staticmethod
    def _limpar_cpf(cpf):
        """Deixa só os dígitos ('123.456.789-00' vira '12345678900')."""
        return "".join(c for c in cpf if c.isdigit())

    @staticmethod
    def _igual(a, b):
        """Compara textos ignorando espaços nas pontas e maiúsculas/minúsculas."""
        return a.strip().lower() == b.strip().lower()

    def _tutor_ou_erro(self, cpf):
        tutor = self.buscar_tutor(cpf)
        if tutor is None:
            raise ValueError("Tutor não encontrado.")
        return tutor

    # ------------------------------------------------------------------- tutores
    def cadastrar_tutor(self, nome, cpf, telefone):
        cpf = self._limpar_cpf(cpf)
        if not nome.strip():
            raise ValueError("Informe o nome do tutor.")
        if len(cpf) != 11:
            raise ValueError("O CPF deve ter 11 dígitos.")
        if self.buscar_tutor(cpf) is not None:
            raise ValueError("Já existe um tutor com esse CPF.")
        tutor = Tutor(nome.strip(), cpf, telefone.strip())
        self.tutores.adicionar(tutor)
        return tutor

    def buscar_tutor(self, cpf):
        """Busca por CPF. Custo O(n), com n = número de tutores."""
        cpf = self._limpar_cpf(cpf)
        return self.tutores.buscar(lambda t: t.cpf == cpf)

    def remover_tutor(self, cpf):
        """Remove o tutor e, junto com ele, a lista de animais dele."""
        tutor = self._tutor_ou_erro(cpf)
        for animal in tutor.animais:
            if self.atendimento.animal_ocupado(tutor.cpf, animal.nome):
                raise ValueError(f"{animal.nome} está na fila ou em atendimento.")
        self.tutores.remover(lambda t: t is tutor)
        return tutor

    # ------------------------------------------------------------------- animais
    def cadastrar_animal(self, cpf, nome, especie, raca, idade):
        tutor = self._tutor_ou_erro(cpf)
        if not nome.strip():
            raise ValueError("Informe o nome do animal.")
        if idade < 0:
            raise ValueError("A idade não pode ser negativa.")
        # o nome só precisa ser único dentro dos animais do mesmo tutor
        if tutor.animais.buscar(lambda a: self._igual(a.nome, nome)) is not None:
            raise ValueError(f"{tutor.nome} já tem um animal chamado {nome.strip()}.")
        animal = Animal(nome.strip(), especie.strip(), raca.strip(), idade)
        tutor.animais.adicionar(animal)
        return animal

    def buscar_animal(self, cpf, nome_animal):
        """Combinação Lista + Lista: percorre a lista de tutores até achar o CPF e,
        em seguida, a lista de animais desse tutor. Devolve (tutor, animal).
        Custo O(t + a): t = tutores, a = animais do tutor encontrado.
        """
        tutor = self.buscar_tutor(cpf)
        if tutor is None:
            return None, None
        animal = tutor.animais.buscar(lambda a: self._igual(a.nome, nome_animal))
        return tutor, animal

    def remover_animal(self, cpf, nome_animal):
        tutor = self._tutor_ou_erro(cpf)
        if self.atendimento.animal_ocupado(tutor.cpf, nome_animal):
            raise ValueError("Esse animal está na fila ou em atendimento.")
        animal = tutor.animais.remover(lambda a: self._igual(a.nome, nome_animal))
        if animal is None:
            raise ValueError("Animal não encontrado para esse tutor.")
        return animal

    # --------------------------------------------------------------- atendimento
    def solicitar_atendimento(self, cpf, nome_animal, queixa, emergencia=False):
        """Confere se o tutor e o animal existem e coloca o animal na fila de espera."""
        tutor, animal = self.buscar_animal(cpf, nome_animal)
        if tutor is None:
            raise ValueError("Tutor não encontrado.")
        if animal is None:
            raise ValueError("Animal não encontrado para esse tutor.")
        if not queixa.strip():
            raise ValueError("Informe a queixa relatada.")
        solicitacao = Solicitacao(animal.nome, tutor.nome, tutor.cpf,
                                  queixa.strip(), emergencia)
        self.atendimento.chegada(solicitacao)
        return solicitacao


    # ---------------------------------------------------------------- prontuário
    def chamar_proximo(self, veterinario):
        """Chama o próximo animal da fila para um consultório livre e abre o prontuário."""
        if not veterinario.strip():
            raise ValueError("Informe o veterinário responsável.")
        consultorio, solicitacao = self.atendimento.chamar_proximo()
        prontuario = Prontuario(self._proximo_numero, solicitacao.nome_animal,
                                solicitacao.nome_tutor, solicitacao.cpf,
                                veterinario.strip(), consultorio.numero, solicitacao.queixa)
        self._proximo_numero += 1
        self.prontuarios.adicionar(prontuario)
        return prontuario

    def buscar_prontuario(self, numero):
        return self.prontuarios.buscar(lambda p: p.numero == numero)

    def _prontuario_aberto(self, numero):
        prontuario = self.buscar_prontuario(numero)
        if prontuario is None:
            raise ValueError("Prontuário aberto não encontrado.")
        return prontuario

    def marcar_alterado(self, numero, nome_componente):
        prontuario = self._prontuario_aberto(numero)
        return diagnostico.marcar_alterado(prontuario.diagnostico, nome_componente)

    def adicionar_medicamento(self, numero, codigo, quantidade):
        """Inclui o medicamento no prontuário (o estoque só é baixado no fechamento)."""
        prontuario = self._prontuario_aberto(numero)
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        produto = self.estoque.buscar_produto(codigo)
        if produto is None:
            raise ValueError("Produto não encontrado no estoque.")
        item = prontuario.medicamentos.buscar(lambda i: i.codigo == produto.codigo)
        ja_incluido = item.quantidade if item is not None else 0
        if self.estoque.quantidade_disponivel(produto.codigo) < ja_incluido + quantidade:
            raise ValueError(f"Estoque insuficiente de {produto.nome}.")
        if item is None:
            prontuario.medicamentos.adicionar(
                ItemMedicamento(produto.codigo, produto.nome, quantidade))
        else:
            item.quantidade += quantidade

    def remover_medicamento(self, numero, codigo):
        prontuario = self._prontuario_aberto(numero)
        codigo = codigo.strip().upper()
        if prontuario.medicamentos.remover(lambda i: i.codigo == codigo) is None:
            raise ValueError("Esse medicamento não está no prontuário.")

    def adicionar_procedimento(self, numero, nome, valor):
        prontuario = self._prontuario_aberto(numero)
        if not nome.strip():
            raise ValueError("Informe o nome do procedimento.")
        if valor < 0:
            raise ValueError("O valor não pode ser negativo.")
        prontuario.procedimentos.adicionar(Procedimento(nome.strip(), valor))

    def remover_procedimento(self, numero, nome):
        prontuario = self._prontuario_aberto(numero)
        removido = prontuario.procedimentos.remover(lambda p: self._igual(p.nome, nome))
        if removido is None:
            raise ValueError("Esse procedimento não está no prontuário.")

    def dar_alta(self, numero):
        self._prontuario_aberto(numero).alta = True

    def fechar_prontuario(self, numero, forma, parcelas=1):
        """Fecha o prontuário: baixa o estoque (lote mais antigo primeiro), registra o
        consumo de cada medicamento, registra o pagamento e libera o consultório.
        Devolve (pagamento, próximo animal da fila ou None)."""
        prontuario = self._prontuario_aberto(numero)
        if not prontuario.alta:
            raise ValueError("O prontuário só pode ser fechado depois da alta do animal.")
        forma = forma.strip().upper()
        if forma not in FORMAS:
            raise ValueError("Forma de pagamento inválida (PIX, CARTAO ou DINHEIRO).")
        if forma != "CARTAO":
            parcelas = 1
        elif parcelas < 1:
            raise ValueError("Número de parcelas inválido.")

        # 1) confere o estoque de todos os itens antes de mexer em qualquer coisa
        for item in prontuario.medicamentos:
            if self.estoque.quantidade_disponivel(item.codigo) < item.quantidade:
                raise ValueError(f"Estoque insuficiente de {item.nome}.")

        # 2) baixa o estoque e registra quem consumiu o quê
        agora = datetime.now()
        valor_medicamentos = 0
        for item in prontuario.medicamentos:
            valor = self.estoque.baixar(item.codigo, item.quantidade)
            valor_medicamentos += valor
            self.consumos.adicionar(Consumo(prontuario.cpf, prontuario.nome_tutor,
                                            prontuario.nome_animal, prontuario.numero,
                                            item.codigo, item.nome, item.quantidade,
                                            valor, agora))

        # 3) registra o pagamento
        pagamento = Pagamento(prontuario.nome_tutor, prontuario.numero, forma, parcelas,
                              valor_medicamentos, prontuario.valor_procedimentos(), agora)
        self.pagamentos.adicionar(pagamento)

        # 4) encerra o prontuário e libera o consultório (indicando o próximo da fila)
        self.prontuarios.remover(lambda p: p is prontuario)
        proximo = self.atendimento.liberar_consultorio(prontuario.consultorio)
        return pagamento, proximo


# Teste rápido: rode `python clinica.py` para simular um atendimento completo.
if __name__ == "__main__":
    from datetime import date, timedelta

    clinica = Clinica(num_consultorios=1)
    clinica.cadastrar_tutor("Ana Souza", "111.111.111-11", "19 99999-0001")
    clinica.cadastrar_animal("11111111111", "Rex", "Cachorro", "Labrador", 4)
    clinica.cadastrar_tutor("Bruno Lima", "222.222.222-22", "19 98888-0002")
    clinica.cadastrar_animal("22222222222", "Thor", "Cachorro", "Pitbull", 6)
    clinica.estoque.registrar_compra("Vermífugo", "VER01", "VetPharma", 10.0, 25.0, 10,
                                     date.today() + timedelta(days=200))

    # 1) chegada: o Rex chega primeiro, mas o Thor é emergência
    clinica.solicitar_atendimento("11111111111", "Rex", "vômito")
    clinica.solicitar_atendimento("22222222222", "Thor", "atropelamento", emergencia=True)

    # 2) chamada do próximo e abertura do prontuário
    prontuario = clinica.chamar_proximo("Dra. Paula")
    print(f"Prontuário {prontuario.numero} aberto para {prontuario.nome_animal} "
          f"no consultório {prontuario.consultorio}")

    # 3) diagnóstico
    clinica.marcar_alterado(prontuario.numero, "Pulmões")
    diagnostico.exibir(prontuario.diagnostico)

    # 4) medicamentos e procedimentos
    clinica.adicionar_medicamento(prontuario.numero, "VER01", 2)
    clinica.adicionar_procedimento(prontuario.numero, "Consulta de emergência", 120.0)

    # 5) alta, fechamento e pagamento
    try:
        clinica.fechar_prontuario(prontuario.numero, "PIX")
    except ValueError as erro:
        print("Erro esperado:", erro)
    clinica.dar_alta(prontuario.numero)
    pagamento, proximo = clinica.fechar_prontuario(prontuario.numero, "cartao", 3)
    print(f"Pago: R$ {pagamento.valor_total:.2f} ({pagamento.forma}, {pagamento.parcelas}x)")
    print("Próximo animal a ser atendido:", proximo.nome_animal)
    for c in clinica.consumos:
        print(f"Consumo: {c.quantidade}x {c.produto} - {c.nome_animal} (tutor {c.nome_tutor})")
    print("Estoque de vermífugo:", clinica.estoque.buscar_produto("VER01").quantidade_total())