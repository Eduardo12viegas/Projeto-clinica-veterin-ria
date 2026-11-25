"""Perfil do CLIENTE (tutor): cadastra a si mesmo e seus animais, pede atendimento e
acompanha a espera. Só enxerga os dados do próprio CPF; consultas, prontuários, estoque,
pagamentos e dados de outros tutores ficam exclusivos do funcionário."""

from cli import menu, titulo, ler_texto, ler_inteiro, confirmar, pausar, data_hora
from contexto import clinica, seguro


# ---------------------------------------------------------------- identificação
def ler_cpf():
    """Pede o CPF até ter 11 dígitos (aceita com ou sem pontos e traço)."""
    while True:
        cpf = ler_texto("Digite seu CPF: ")
        if len("".join(c for c in cpf if c.isdigit())) == 11:
            return cpf
        print("CPF inválido: digite os 11 números (ex.: 123.456.789-00).")


def cadastrar_se(cpf):
    """Cadastro de um tutor novo com o CPF já informado. Devolve o Tutor ou None."""
    try:
        tutor = clinica.cadastrar_tutor(ler_texto("Nome: "), cpf, ler_texto("Telefone: "))
    except ValueError as erro:
        print("Erro:", erro)
        pausar()
        return None
    print(f"Cadastro concluído, {tutor.nome}!")
    return tutor


def identificar():
    """Pede o CPF; se não houver cadastro, oferece criar um (reaproveitando o CPF digitado)
    e já entra com o novo usuário. Devolve o Tutor ou None."""
    cpf = ler_cpf()
    tutor = clinica.buscar_tutor(cpf)
    if tutor is not None:
        print(f"Olá, {tutor.nome}!")
        return tutor
    print("Não encontramos cadastro com esse CPF.")
    if confirmar("Deseja se cadastrar agora?"):
        return cadastrar_se(cpf)
    return None


# ---------------------------------------------------------------- meus animais
def meus_animais(tutor):
    titulo("Meus dados e animais")
    print(f"{tutor.nome} | CPF {tutor.cpf} | tel. {tutor.telefone}")
    if tutor.animais.vazia():
        print("     (nenhum animal cadastrado)")
    for a in tutor.animais:
        print(f"     {a.nome} - {a.especie}, {a.raca}, {a.idade} ano(s)")


def cadastrar_animal(tutor):
    clinica.cadastrar_animal(tutor.cpf, ler_texto("Nome do animal: "),
                             ler_texto("Espécie: "), ler_texto("Raça: "),
                             ler_inteiro("Idade (anos): ", 0))
    print("Animal cadastrado!")


# ------------------------------------------------------------------- atendimento
def solicitar_atendimento(tutor):
    if tutor.animais.vazia():
        raise ValueError("Cadastre um animal antes de pedir atendimento.")
    nome = ler_texto("Nome do animal: ")
    queixa = ler_texto("O que ele está sentindo? ")
    emergencia = confirmar("É emergência (atropelamento, intoxicação, falta de ar...)?")
    clinica.solicitar_atendimento(tutor.cpf, nome, queixa, emergencia)
    print("Pedido enviado! Seu animal entrou na fila de espera.")


def acompanhar_espera(tutor):
    """Mostra a situação dos animais do tutor sem revelar dados de outros tutores."""
    titulo("Acompanhar atendimento")
    if tutor.animais.vazia():
        print("Você não tem animais cadastrados.")
        return
    total = sum(1 for _ in clinica.atendimento.fila_em_ordem())
    for animal in tutor.animais:
        situacao = "não está na fila"
        for posicao, s in enumerate(clinica.atendimento.fila_em_ordem(), start=1):
            if s.e_do_animal(tutor.cpf, animal.nome):
                tipo = "emergência" if s.emergencia else "normal"
                situacao = (f"na fila ({tipo}), posição {posicao} de {total} "
                            f"- pedido às {data_hora(s.data_hora)}")
                break
        for c in clinica.atendimento.consultorios:
            if c.ocupante is not None and c.ocupante.e_do_animal(tutor.cpf, animal.nome):
                situacao = f"em atendimento no consultório {c.numero}"
        print(f"{animal.nome}: {situacao}")


# ------------------------------------------------------------------------ início
def menu_cliente():
    tutor = identificar()
    if tutor is None:
        return
    acoes = {1: meus_animais, 2: cadastrar_animal, 3: solicitar_atendimento,
             4: acompanhar_espera}
    while True:
        op = menu(f"ÁREA DO CLIENTE - {tutor.nome}",
                  ("Meus dados e animais", "Cadastrar animal", "Solicitar atendimento",
                   "Acompanhar meu animal na fila"), sair="Sair da área do cliente")
        if op == 0:
            return
        seguro(acoes[op], tutor)
        pausar()
