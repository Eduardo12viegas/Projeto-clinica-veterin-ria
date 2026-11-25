"""Estado compartilhado entre os perfis (cliente e funcionário).

Existe uma única Clinica por execução. Cliente e funcionário usam o MESMO objeto,
então um pedido de atendimento feito pelo cliente aparece na fila do funcionário.
"""
from datetime import date, timedelta

from clinica import Clinica

# Senha de acesso ao perfil de funcionário (troque aqui). Ver nota no README.
SENHA_FUNCIONARIO = "vet123"

clinica = Clinica(num_consultorios=2)


def seguro(acao, *args):
    """Executa uma ação e mostra a mensagem se alguma regra for violada (ValueError)."""
    try:
        acao(*args)
    except ValueError as erro:
        print("Erro:", erro)


# ------------------------------------------------------------ dados de exemplo
def carregar_exemplo():
    clinica.cadastrar_tutor("Ana Souza", "111.111.111-11", "19 99999-0001")
    clinica.cadastrar_animal("11111111111", "Rex", "Cachorro", "Labrador", 4)
    clinica.cadastrar_animal("11111111111", "Mimi", "Gato", "Siamês", 2)
    clinica.cadastrar_tutor("Bruno Lima", "222.222.222-22", "19 98888-0002")
    clinica.cadastrar_animal("22222222222", "Thor", "Cachorro", "Pitbull", 6)

    hoje = date.today()
    est = clinica.estoque
    est.registrar_compra("Vermífugo", "VER01", "VetPharma", 10.0, 25.0, 5,
                         hoje + timedelta(days=200), hoje - timedelta(days=30), minimo=5)
    est.registrar_compra("Vermífugo", "VER01", "VetPharma", 12.0, 28.0, 10,
                         hoje + timedelta(days=300), hoje - timedelta(days=5))
    # o primeiro lote da vacina já venceu: vai virar perda
    est.registrar_compra("Vacina antirrábica", "VAC01", "ImunoVet", 20.0, 45.0, 4,
                         hoje - timedelta(days=1), hoje - timedelta(days=90), minimo=3)
    est.registrar_compra("Vacina antirrábica", "VAC01", "ImunoVet", 22.0, 48.0, 8,
                         hoje + timedelta(days=250), hoje - timedelta(days=10))
    est.registrar_compra("Antibiótico", "ANT01", "VetPharma", 15.0, 40.0, 6,
                         hoje + timedelta(days=150), hoje - timedelta(days=15), minimo=4)
    est.registrar_compra("Atadura", "ATA01", "MedVet", 2.0, 6.0, 20,
                         hoje + timedelta(days=900), hoje - timedelta(days=20), minimo=10)

