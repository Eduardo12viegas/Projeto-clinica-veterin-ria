"""Perfil do FUNCIONÁRIO: acesso completo (tutores, atendimento, prontuários, estoque,
relatórios). É quem chama os animais, faz as consultas e fecha os pagamentos."""

from getpass import getpass

import diagnostico
from cli import (menu, titulo, ler_texto, ler_inteiro, ler_decimal, ler_data, confirmar,
                 pausar, moeda, data_hora)
from contexto import clinica, seguro, SENHA_FUNCIONARIO


# ------------------------------------------------------------ tutores e animais
def mostrar_tutor(tutor):
    print(f"{tutor.nome} | CPF {tutor.cpf} | tel. {tutor.telefone}")
    if tutor.animais.vazia():
        print("     (sem animais)")
    for a in tutor.animais:
        print(f"     {a.nome} - {a.especie}, {a.raca}, {a.idade} ano(s)")


def cadastrar_tutor():
    clinica.cadastrar_tutor(ler_texto("Nome: "), ler_texto("CPF: "), ler_texto("Telefone: "))
    print("Tutor cadastrado!")


def cadastrar_animal():
    cpf = ler_texto("CPF do tutor: ")
    if clinica.buscar_tutor(cpf) is None:
        raise ValueError("Tutor não encontrado.")
    clinica.cadastrar_animal(cpf, ler_texto("Nome do animal: "), ler_texto("Espécie: "),
                             ler_texto("Raça: "), ler_inteiro("Idade (anos): ", 0))
    print("Animal cadastrado!")


def listar_tutores():
    titulo("Tutores cadastrados")
    if clinica.tutores.vazia():
        print("Nenhum tutor cadastrado.")
    for tutor in clinica.tutores:
        mostrar_tutor(tutor)


def buscar_tutor():
    tutor = clinica.buscar_tutor(ler_texto("CPF do tutor: "))
    if tutor is None:
        print("Tutor não encontrado.")
    else:
        mostrar_tutor(tutor)


def buscar_animal():
    tutor, animal = clinica.buscar_animal(ler_texto("CPF do tutor: "),
                                          ler_texto("Nome do animal: "))
    if tutor is None:
        print("Tutor não encontrado.")
    elif animal is None:
        print("Animal não encontrado para esse tutor.")
    else:
        print(f"{animal.nome} - {animal.especie}, {animal.raca}, {animal.idade} ano(s) "
              f"| tutor: {tutor.nome}")


def remover_tutor():
    cpf = ler_texto("CPF do tutor a remover: ")
    tutor = clinica.buscar_tutor(cpf)
    if tutor is None:
        raise ValueError("Tutor não encontrado.")
    if confirmar(f"Remover {tutor.nome} e todos os seus animais?"):
        clinica.remover_tutor(cpf)
        print("Tutor removido.")


def remover_animal():
    cpf = ler_texto("CPF do tutor: ")
    nome = ler_texto("Nome do animal a remover: ")
    if confirmar(f"Remover {nome}?"):
        clinica.remover_animal(cpf, nome)
        print("Animal removido.")


def menu_tutores():
    acoes = {1: cadastrar_tutor, 2: cadastrar_animal, 3: listar_tutores, 4: buscar_tutor,
             5: buscar_animal, 6: remover_tutor, 7: remover_animal}
    while True:
        op = menu("TUTORES E ANIMAIS", ("Cadastrar tutor", "Cadastrar animal",
                                        "Listar tutores", "Buscar tutor (CPF)",
                                        "Buscar animal (CPF + nome)", "Remover tutor",
                                        "Remover animal"))
        if op == 0:
            return
        seguro(acoes[op])
        pausar()


# ------------------------------------------------------------------ atendimento
def solicitar_atendimento():
    cpf = ler_texto("CPF do tutor: ")
    nome = ler_texto("Nome do animal: ")
    queixa = ler_texto("Queixa relatada: ")
    emergencia = confirmar("É emergência (atropelamento, intoxicação, falta de ar...)?")
    clinica.solicitar_atendimento(cpf, nome, queixa, emergencia)
    print("Animal na fila de espera.")


def ver_fila():
    titulo("Fila de espera (ordem de chamada)")
    vazia = True
    for posicao, s in enumerate(clinica.atendimento.fila_em_ordem(), start=1):
        tipo = "EMERGÊNCIA" if s.emergencia else "normal"
        print(f"{posicao}. {s.nome_animal} (tutor {s.nome_tutor}) - {tipo} - {s.queixa} "
              f"- chegou {data_hora(s.data_hora)}")
        vazia = False
    if vazia:
        print("Fila vazia.")
    titulo("Consultórios")
    for c in clinica.atendimento.consultorios:
        estado = "livre" if c.ocupante is None else f"ocupado por {c.ocupante.nome_animal}"
        print(f"Consultório {c.numero}: {estado}")


def chamar_proximo():
    proximo = clinica.atendimento.proximo_da_fila()
    if proximo is None:
        raise ValueError("A fila de espera está vazia.")
    print(f"Próximo da fila: {proximo.nome_animal} (tutor {proximo.nome_tutor})")
    prontuario = clinica.chamar_proximo(ler_texto("Veterinário responsável: "))
    print(f"Prontuário {prontuario.numero} aberto para {prontuario.nome_animal} "
          f"no consultório {prontuario.consultorio}. Queixa: {prontuario.queixa}")


def menu_atendimento():
    acoes = {1: solicitar_atendimento, 2: ver_fila, 3: chamar_proximo}
    while True:
        op = menu("ATENDIMENTO", ("Solicitar atendimento (chegada do animal)",
                                  "Ver fila e consultórios", "Chamar próximo animal"))
        if op == 0:
            return
        seguro(acoes[op])
        pausar()


# ------------------------------------------------------------------ prontuários
def mostrar_prontuario(p):
    titulo(f"Prontuário {p.numero} - {p.nome_animal} (tutor {p.nome_tutor})")
    print(f"Veterinário: {p.veterinario} | Consultório {p.consultorio} | "
          f"Aberto em {data_hora(p.data_hora)}")
    print(f"Queixa: {p.queixa} | Alta: {'sim' if p.alta else 'não'}")
    print("Medicamentos:")
    if p.medicamentos.vazia():
        print("  (nenhum)")
    for item in p.medicamentos:
        print(f"  - {item.quantidade}x {item.nome} [{item.codigo}]")
    print("Procedimentos:")
    if p.procedimentos.vazia():
        print("  (nenhum)")
    for proc in p.procedimentos:
        print(f"  - {proc.nome} ({moeda(proc.valor)})")
    print("Diagnóstico:")
    diagnostico.exibir(p.diagnostico)


def listar_prontuarios():
    titulo("Prontuários abertos")
    if clinica.prontuarios.vazia():
        print("Nenhum prontuário aberto.")
    for p in clinica.prontuarios:
        print(f"{p.numero} - {p.nome_animal} (tutor {p.nome_tutor}) - consultório "
              f"{p.consultorio} - alta: {'sim' if p.alta else 'não'}")


def fechar_e_pagar(numero):
    """Devolve True se o prontuário foi fechado."""
    formas = {1: "PIX", 2: "CARTAO", 3: "DINHEIRO"}
    op = menu("FORMA DE PAGAMENTO", ("PIX", "Cartão", "Dinheiro"), sair="Cancelar")
    if op == 0:
        return False
    forma = formas[op]
    parcelas = ler_inteiro("Parcelas (1 = à vista): ", 1) if forma == "CARTAO" else 1
    try:
        pagamento, proximo = clinica.fechar_prontuario(numero, forma, parcelas)
    except ValueError as erro:
        print("Erro:", erro)
        return False
    print(f"Prontuário {numero} fechado. Medicamentos {moeda(pagamento.valor_medicamentos)} "
          f"+ procedimentos {moeda(pagamento.valor_procedimentos)} = "
          f"{moeda(pagamento.valor_total)} ({pagamento.forma}, {pagamento.parcelas}x).")
    print("Estoque baixado e consumo registrado.")
    if proximo is None:
        print("Consultório liberado. Não há animais na fila de espera.")
    else:
        print(f"Consultório liberado. Próximo a ser atendido: {proximo.nome_animal} "
              f"(tutor {proximo.nome_tutor}).")
    return True


def executar_acao_prontuario(op, numero):
    if op == 1:
        mostrar_prontuario(clinica.buscar_prontuario(numero))
    elif op == 2:
        nome = ler_texto("Nome do sistema/órgão (ex.: Pulmões): ")
        clinica.marcar_alterado(numero, nome)
        print("Marcado como Alterado.")
    elif op == 3:
        clinica.adicionar_medicamento(numero, ler_texto("Código do produto: "),
                                      ler_inteiro("Quantidade: ", 1))
        print("Medicamento incluído.")
    elif op == 4:
        clinica.remover_medicamento(numero, ler_texto("Código do produto: "))
        print("Medicamento removido.")
    elif op == 5:
        clinica.adicionar_procedimento(numero, ler_texto("Procedimento: "),
                                       ler_decimal("Valor (R$): "))
        print("Procedimento incluído.")
    elif op == 6:
        clinica.remover_procedimento(numero, ler_texto("Procedimento: "))
        print("Procedimento removido.")
    elif op == 7:
        clinica.dar_alta(numero)
        print("Alta registrada. O prontuário já pode ser fechado.")


def gerenciar_prontuario():
    numero = ler_inteiro("Número do prontuário: ", 1)
    if clinica.buscar_prontuario(numero) is None:
        print("Prontuário aberto não encontrado.")
        return
    while True:
        op = menu(f"PRONTUÁRIO {numero}",
                  ("Ver prontuário e árvore", "Marcar item como Alterado",
                   "Adicionar medicamento", "Remover medicamento",
                   "Adicionar procedimento", "Remover procedimento",
                   "Dar alta ao animal", "Fechar prontuário e pagar"))
        if op == 0:
            return
        if op == 8:
            if fechar_e_pagar(numero):
                pausar()
                return
        else:
            seguro(executar_acao_prontuario, op, numero)
        pausar()


def menu_prontuarios():
    while True:
        op = menu("PRONTUÁRIOS", ("Listar prontuários abertos", "Gerenciar um prontuário"))
        if op == 0:
            return
        if op == 1:
            listar_prontuarios()
            pausar()
        else:
            gerenciar_prontuario()


# ---------------------------------------------------------------------- estoque
def listar_estoque():
    clinica.estoque.descartar_vencidos()
    titulo("Estoque (lotes do mais antigo para o mais novo)")
    if clinica.estoque.produtos.vazia():
        print("Estoque vazio.")
    for p in clinica.estoque.produtos:
        print(f"{p.nome} [{p.codigo}] - total {p.quantidade_total()} (mínimo {p.minimo})")
        for lote in p.lotes:
            print(f"     comprado em {lote.data_compra:%d/%m/%Y}: {lote.quantidade} un | "
                  f"{lote.fornecedor} | compra {moeda(lote.preco_compra)} | "
                  f"venda {moeda(lote.preco_venda)} | validade {lote.validade:%d/%m/%Y}")


def registrar_compra():
    nome = ler_texto("Nome do produto: ")
    codigo = ler_texto("Código: ")
    fornecedor = ler_texto("Fornecedor: ")
    preco_compra = ler_decimal("Preço de compra (R$): ")
    preco_venda = ler_decimal("Preço de venda (R$): ")
    quantidade = ler_inteiro("Quantidade: ", 1)
    validade = ler_data("Validade (dd/mm/aaaa): ")
    minimo = None
    if clinica.estoque.buscar_produto(codigo) is None:
        minimo = ler_inteiro("Estoque mínimo para alerta: ", 0)
    clinica.estoque.registrar_compra(nome, codigo, fornecedor, preco_compra, preco_venda,
                                     quantidade, validade, minimo=minimo)
    print("Compra registrada (novo lote).")


def ajustar_estoque():
    codigo = ler_texto("Código do produto: ")
    nova = ler_inteiro("Nova quantidade total em estoque: ", 0)
    clinica.estoque.ajustar_quantidade(codigo, nova)
    print("Estoque ajustado.")


def ver_alertas():
    titulo("Alertas de estoque")
    produtos = clinica.estoque.alertas()
    if not produtos:
        print("Nenhum produto abaixo do mínimo.")
    for p in produtos:
        print(f"ATENÇÃO: {p.nome} [{p.codigo}] com {p.quantidade_total()} un "
              f"(mínimo {p.minimo}).")


def descartar_vencidos():
    antes = len(clinica.estoque.perdas)
    clinica.estoque.descartar_vencidos()
    print(f"{len(clinica.estoque.perdas) - antes} lote(s) vencido(s) descartado(s).")


def menu_estoque():
    acoes = {1: listar_estoque, 2: registrar_compra, 3: ajustar_estoque, 4: ver_alertas,
             5: descartar_vencidos}
    while True:
        op = menu("ESTOQUE", ("Listar produtos e lotes", "Registrar compra (novo lote)",
                              "Ajustar quantidade (inventário)", "Ver alertas de mínimo",
                              "Descartar lotes vencidos"))
        if op == 0:
            return
        seguro(acoes[op])
        pausar()


# ------------------------------------------------------------------- relatórios
def relatorio_pagamentos():
    titulo("Pagamentos recebidos")
    if clinica.pagamentos.vazia():
        print("Nenhum pagamento registrado.")
    for pg in clinica.pagamentos:
        print(f"{data_hora(pg.data_hora)} | Prontuário {pg.numero_prontuario} | "
              f"{pg.nome_pagador} | {pg.forma} ({pg.parcelas}x) | "
              f"medicamentos {moeda(pg.valor_medicamentos)} + procedimentos "
              f"{moeda(pg.valor_procedimentos)} = {moeda(pg.valor_total)}")


def relatorio_consumo():
    titulo("Consumo: quem usou o quê")
    if clinica.consumos.vazia():
        print("Nenhum consumo registrado.")
    for c in clinica.consumos:
        print(f"{data_hora(c.data_hora)} | Prontuário {c.numero_prontuario} | "
              f"tutor {c.nome_tutor} | animal {c.nome_animal} | "
              f"{c.quantidade}x {c.produto} | {moeda(c.valor)}")


def relatorio_perdas():
    titulo("Perdas por validade")
    if clinica.estoque.perdas.vazia():
        print("Nenhuma perda registrada.")
    for p in clinica.estoque.perdas:
        print(f"{p.data_descarte:%d/%m/%Y} | {p.quantidade}x {p.produto} [{p.codigo}] | "
              f"venceu em {p.validade:%d/%m/%Y} | custo {moeda(p.custo)}")


def menu_relatorios():
    acoes = {1: relatorio_pagamentos, 2: relatorio_consumo, 3: relatorio_perdas}
    while True:
        op = menu("RELATÓRIOS", ("Pagamentos recebidos", "Consumo por tutor e animal",
                                 "Perdas por validade"))
        if op == 0:
            return
        acoes[op]()
        pausar()


# ------------------------------------------------------------------------ início
def autenticar():
    """Pede a senha (3 tentativas). Devolve True se o acesso foi liberado."""
    for _ in range(3):
        if getpass("Senha do funcionário: ") == SENHA_FUNCIONARIO:
            return True
        print("Senha incorreta.")
    return False


def menu_funcionario():
    if not autenticar():
        print("Acesso negado.")
        return
    submenus = {1: menu_tutores, 2: menu_atendimento, 3: menu_prontuarios,
                4: menu_estoque, 5: menu_relatorios}
    while True:
        op = menu("ÁREA DO FUNCIONÁRIO",
                  ("Tutores e animais", "Atendimento", "Prontuários", "Estoque",
                   "Relatórios"), sair="Sair da área do funcionário")
        if op == 0:
            return
        submenus[op]()
