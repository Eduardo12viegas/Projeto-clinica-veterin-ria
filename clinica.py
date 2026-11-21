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
    def __init__(self):
        self.tutores = Lista()      # Lista de Tutor (cada um com sua Lista de Animal)
        # Próximos passos: fila_emergencia, fila_normal, consultorios, estoque...

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
        # TODO: quando a fila existir, não deixar remover se algum animal estiver
        # esperando ou em atendimento.
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
        # TODO: mesma regra do tutor (não remover animal na fila ou em atendimento).
        animal = tutor.animais.remover(lambda a: self._igual(a.nome, nome_animal))
        if animal is None:
            raise ValueError("Animal não encontrado para esse tutor.")
        return animal


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

    clinica.remover_animal("11111111111", "Mimi")
    print("Animais de Ana depois de remover a Mimi:",
          [a.nome for a in clinica.buscar_tutor("11111111111").animais])
    clinica.remover_tutor("11111111111")
    print("Tutores restantes:", len(clinica.tutores))