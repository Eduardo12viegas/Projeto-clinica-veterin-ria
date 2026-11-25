"""Atendimento: espera dos animais e consultórios.

Combinação de estruturas: Fila + Fila.
Existe uma fila de emergência e uma fila normal. O próximo a ser atendido vem da fila de
emergência; se ela estiver vazia, vem da normal. Cada fila mantém a ordem de chegada.
"""
from datetime import datetime

from estruturas import Fila, Lista


class Solicitacao:

    def __init__(self, nome_animal, nome_tutor, cpf, queixa, emergencia=False):
        self.nome_animal = nome_animal
        self.nome_tutor = nome_tutor
        self.cpf = cpf
        self.queixa = queixa
        self.emergencia = emergencia
        self.data_hora = datetime.now()

    def e_do_animal(self, cpf, nome_animal):
        return (self.cpf == cpf
                and self.nome_animal.strip().lower() == nome_animal.strip().lower())


class Consultorio:
    def __init__(self, numero):
        self.numero = numero
        self.ocupante = None        # Solicitacao em atendimento (None = livre)


class ControleAtendimento:
    def __init__(self, num_consultorios=2):
        self.fila_emergencia = Fila()
        self.fila_normal = Fila()
        self.consultorios = Lista()
        for numero in range(1, num_consultorios + 1):
            self.consultorios.adicionar(Consultorio(numero))

    # ------------------------------------------------------------------- chegada
    def chegada(self, solicitacao):
        """Coloca o animal na fila certa. Enfileirar é O(1)."""
        if self.animal_ocupado(solicitacao.cpf, solicitacao.nome_animal):
            raise ValueError("Esse animal já está na fila de espera ou em atendimento.")
        if solicitacao.emergencia:
            self.fila_emergencia.enfileirar(solicitacao)
        else:
            self.fila_normal.enfileirar(solicitacao)

    # ------------------------------------------------------------ próximo da fila
    def proximo_da_fila(self):
        """Só espia quem é o próximo (sem tirar da fila). Emergência primeiro. O(1)."""
        if not self.fila_emergencia.vazia():
            return self.fila_emergencia.primeiro()
        return self.fila_normal.primeiro()

    def consultorio_livre(self):
        """Primeiro consultório sem ocupante, ou None. O(c), c = nº de consultórios."""
        return self.consultorios.buscar(lambda c: c.ocupante is None)

    def chamar_proximo(self):
        """Tira o próximo da fila e coloca num consultório livre.
        Devolve (consultorio, solicitacao)."""
        if self.proximo_da_fila() is None:
            raise ValueError("A fila de espera está vazia.")
        consultorio = self.consultorio_livre()
        if consultorio is None:
            raise ValueError("Nenhum consultório livre no momento.")
        if not self.fila_emergencia.vazia():
            solicitacao = self.fila_emergencia.desenfileirar()
        else:
            solicitacao = self.fila_normal.desenfileirar()
        consultorio.ocupante = solicitacao
        return consultorio, solicitacao

    def liberar_consultorio(self, numero):
        """Libera o consultório e devolve quem é o próximo da fila (ou None).
        É assim que o sistema indica o próximo animal quando um consultório fica livre."""
        consultorio = self.consultorios.buscar(lambda c: c.numero == numero)
        if consultorio is None or consultorio.ocupante is None:
            raise ValueError("Esse consultório não está ocupado.")
        consultorio.ocupante = None
        return self.proximo_da_fila()

    # ------------------------------------------------------------------ consultas
    def fila_em_ordem(self):
        """Ordem de chamada: primeiro as emergências, depois os normais."""
        yield from self.fila_emergencia
        yield from self.fila_normal

    def animal_ocupado(self, cpf, nome_animal):
        """True se o animal está esperando ou dentro de um consultório."""
        for s in self.fila_em_ordem():
            if s.e_do_animal(cpf, nome_animal):
                return True
        for c in self.consultorios:
            if c.ocupante is not None and c.ocupante.e_do_animal(cpf, nome_animal):
                return True
        return False


# Teste rápido: rode `python atendimento.py`.
if __name__ == "__main__":
    ctrl = ControleAtendimento(num_consultorios=1)
    ctrl.chegada(Solicitacao("Rex", "Ana", "111", "vômito"))
    ctrl.chegada(Solicitacao("Mimi", "Bia", "222", "falta de apetite"))
    ctrl.chegada(Solicitacao("Thor", "Caio", "333", "atropelamento", emergencia=True))
    ctrl.chegada(Solicitacao("Luna", "Duda", "444", "intoxicação", emergencia=True))

    print("Ordem de chamada:", [s.nome_animal for s in ctrl.fila_em_ordem()])

    consultorio, atual = ctrl.chamar_proximo()
    print(f"Consultório {consultorio.numero} chamou: {atual.nome_animal}")
    try:
        ctrl.chamar_proximo()
    except ValueError as erro:
        print("Erro esperado:", erro)

    proximo = ctrl.liberar_consultorio(1)
    print("Consultório 1 liberado. Próximo a ser atendido:", proximo.nome_animal)