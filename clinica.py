from atendimento import ControleAtendimento, Solicitacao
from estruturas import Lista


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
        # Próximos passos: estoque, prontuário, pagamento...

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


# Teste rápido: rode `python clinica.py` para ver o que já funciona.
if __name__ == "__main__":
    clinica = Clinica()
    clinica.cadastrar_tutor("Ana Souza", "111.111.111-11", "19 99999-0001")
    clinica.cadastrar_animal("11111111111", "Rex", "Cachorro", "Labrador", 4)
    clinica.cadastrar_animal("11111111111", "Mimi", "Gato", "Siamês", 2)

    tutor, animal = clinica.buscar_animal("111.111.111-11", "rex")
    print(f"Achei: {animal.nome} ({animal.especie}, {animal.raca}, {animal.idade} anos) "
          f"- tutor {tutor.nome}")

    for erro in (lambda: clinica.cadastrar_animal("11111111111", "REX", "Cachorro", "SRD", 1),
                 lambda: clinica.cadastrar_tutor("Fulano", "123", "0"),
                 lambda: clinica.remover_animal("11111111111", "Totó")):
        try:
            erro()
        except ValueError as e:
            print("Erro esperado:", e)

    # atendimento: a emergência passa na frente de quem chegou antes
    clinica.cadastrar_tutor("Bruno Lima", "222.222.222-22", "19 98888-0002")
    clinica.cadastrar_animal("22222222222", "Thor", "Cachorro", "Pitbull", 6)
    clinica.solicitar_atendimento("11111111111", "Rex", "vômito")
    clinica.solicitar_atendimento("22222222222", "Thor", "atropelamento", emergencia=True)
    print("Ordem de chamada:", [x.nome_animal for x in clinica.atendimento.fila_em_ordem()])
    try:
        clinica.remover_animal("22222222222", "Thor")
    except ValueError as e:
        print("Erro esperado:", e)

    consultorio, atual = clinica.atendimento.chamar_proximo()
    print(f"Consultório {consultorio.numero} chamou {atual.nome_animal}")
    proximo = clinica.atendimento.liberar_consultorio(consultorio.numero)
    print("Próximo a ser atendido:", proximo.nome_animal)
    clinica.atendimento.chamar_proximo()          # Rex ocupa um consultório

    clinica.remover_animal("11111111111", "Mimi")
    print("Animais de Ana depois de remover a Mimi:",
          [a.nome for a in clinica.buscar_tutor("11111111111").animais])
    try:
        clinica.remover_tutor("11111111111")      # Rex está em atendimento
    except ValueError as e:
        print("Erro esperado:", e)