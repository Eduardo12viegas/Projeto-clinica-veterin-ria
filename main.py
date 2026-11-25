"""Ponto de entrada da clínica veterinária: escolhe o perfil (cliente ou funcionário).

Os dois perfis compartilham a mesma clínica (contexto.py), por isso rodam no mesmo
programa: python main.py
"""
from cli import menu
from contexto import carregar_exemplo
from cliente import menu_cliente
from funcionario import menu_funcionario


def main():
    carregar_exemplo()
    print("Dados de exemplo carregados (tutores, animais e estoque).")
    while True:
        op = menu("CLÍNICA VETERINÁRIA - QUEM É VOCÊ?",
                  ("Sou cliente (tutor)", "Sou funcionário"), sair="Sair")
        if op == 0:
            print("Até logo!")
            return
        if op == 1:
            menu_cliente()
        else:
            menu_funcionario()


if __name__ == "__main__":
    main()