"""Funções auxiliares de terminal: menus, leitura validada e formatação."""
from datetime import datetime


def titulo(texto):
    print("\n" + "=" * 52)
    print(f" {texto}")
    print("=" * 52)


def menu(nome, opcoes, sair="Voltar"):
    """Mostra as opções numeradas e devolve a escolhida (0 = sair/voltar)."""
    titulo(nome)
    for numero, opcao in enumerate(opcoes, start=1):
        print(f"{numero} - {opcao}")
    print(f"0 - {sair}")
    return ler_inteiro("Escolha: ", 0, len(opcoes))


def ler_texto(prompt):
    """Repete a pergunta até a pessoa digitar alguma coisa."""
    while True:
        texto = input(prompt).strip()
        if texto:
            return texto
        print("Digite algo.")


def ler_inteiro(prompt, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(prompt))
        except ValueError:
            print("Digite um número inteiro.")
            continue
        if minimo is not None and valor < minimo:
            print(f"O valor mínimo é {minimo}.")
        elif maximo is not None and valor > maximo:
            print(f"O valor máximo é {maximo}.")
        else:
            return valor


def ler_decimal(prompt, minimo=0.0):
    """Lê um número com vírgula ou ponto (ex.: 25,90)."""
    while True:
        try:
            valor = float(input(prompt).replace(",", "."))
        except ValueError:
            print("Digite um número (ex.: 25,90).")
            continue
        if valor < minimo:
            print(f"O valor mínimo é {minimo}.")
        else:
            return valor


def ler_data(prompt):
    """Lê uma data no formato dd/mm/aaaa."""
    while True:
        try:
            return datetime.strptime(input(prompt).strip(), "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida. Use dd/mm/aaaa.")


def confirmar(prompt):
    while True:
        resposta = input(f"{prompt} (s/n): ").strip().lower()
        if resposta in ("s", "n"):
            return resposta == "s"
        print("Responda com s ou n.")


def pausar():
    input("\nEnter para continuar...")


def moeda(valor):
    """1234.5 vira 'R$ 1.234,50'."""
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def data_hora(momento):
    return momento.strftime("%d/%m/%Y %H:%M")