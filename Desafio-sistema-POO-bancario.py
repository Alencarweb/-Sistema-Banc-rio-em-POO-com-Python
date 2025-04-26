import textwrap
from abc import ABC, abstractmethod
from datetime import date

# Interface Transacao
class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta: 'Conta'):
        pass

# Saque
class Saque(Transacao):
    def __init__(self, valor: float):
        self.valor = valor

    def registrar(self, conta: 'Conta'):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

# Deposito
class Deposito(Transacao):
    def __init__(self, valor: float):
        self.valor = valor

    def registrar(self, conta: 'Conta'):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

# Historico
class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao: Transacao):
        self.transacoes.append(transacao)

# Conta
class Conta:
    def __init__(self, cliente: 'Cliente', numero: int, agencia: str = '0001'):
        self.saldo = 0.0
        self.numero = numero
        self.agencia = agencia
        self.cliente = cliente
        self.historico = Historico()

    def saldo_atual(self) -> float:
        return self.saldo

    def sacar(self, valor: float) -> bool:
        if valor > 0 and self.saldo >= valor:
            self.saldo -= valor
            return True
        print("Saldo insuficiente.")
        return False

    def depositar(self, valor: float) -> bool:
        if valor > 0:
            self.saldo += valor
            return True
        print("Valor inválido para depósito.")
        return False

# Conta Corrente (herda Conta)
class ContaCorrente(Conta):
    def __init__(self, cliente: 'Cliente', numero: int, limite: float = 1000.0, limite_saques: int = 3):
        super().__init__(cliente, numero)
        self.limite = limite
        self.limite_saques = limite_saques

# Cliente
class Cliente:
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta: Conta, transacao: Transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta):
        self.contas.append(conta)

# Pessoa Fisica (herda Cliente)
class PessoaFisica(Cliente):
    def __init__(self, endereco: str, cpf: str, nome: str, data_nascimento: date):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

# Função menu
def menu():
    return input(
        textwrap.dedent(
            """
            ================ MENU ================
            [d] Depositar
            [s] Sacar
            [sa] Saldo atual
            [e] Extrato
            [nc] Nova conta
            [lc] Listar contas
            [nu] Novo usuário
            [q] Sair
            => """
        )
    )

# Funções auxiliares
def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente números): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("Já existe usuário com esse CPF.")
        return

    nome = input("Informe o nome completo: ")
    nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
    nascimento = date.fromisoformat(f"{nascimento[6:]}-{nascimento[3:5]}-{nascimento[0:2]}")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/estado): ")

    usuario = PessoaFisica(endereco, cpf, nome, nascimento)
    usuarios.append(usuario)
    print("Usuário criado com sucesso!")

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(numero_conta, usuarios, contas):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print("Usuário não encontrado, fluxo de criação de conta encerrado!")
        return

    conta = ContaCorrente(cliente=usuario, numero=numero_conta)
    contas.append(conta)
    usuario.adicionar_conta(conta)
    print("Conta criada com sucesso!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 30)
        print(f"Agência: {conta.agencia}")
        print(f"C/C: {conta.numero}")
        print(f"Titular: {conta.cliente.nome}")

def exibir_extrato(conta):
    print("\nExtrato:")
    if not conta.historico.transacoes:
        print("Nenhuma transação realizada.")
    else:
        for transacao in conta.historico.transacoes:
            tipo = transacao.__class__.__name__
            valor = transacao.valor
            print(f"{tipo}: R$ {valor:.2f}")
    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
    print("=" * 30)

# Função principal
def main():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            cpf = input("Informe o CPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)

            if not usuario:
                print("Usuário não encontrado.")
                continue

            valor = float(input("Informe o valor do depósito: "))
            numero = int(input("Informe o número da conta: "))
            conta = next((c for c in usuario.contas if c.numero == numero), None)

            if conta:
                deposito = Deposito(valor)
                usuario.realizar_transacao(conta, deposito)
                print("Depósito realizado com sucesso!")
            else:
                print("Conta não encontrada.")

        elif opcao == "s":
            cpf = input("Informe o CPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)

            if not usuario:
                print("Usuário não encontrado.")
                continue

            valor = float(input("Informe o valor do saque: "))
            numero = int(input("Informe o número da conta: "))
            conta = next((c for c in usuario.contas if c.numero == numero), None)

            if conta:
                saque = Saque(valor)
                usuario.realizar_transacao(conta, saque)
            else:
                print("Conta não encontrada.")

        elif opcao == "sa":
            cpf = input("Informe o CPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)

            if not usuario:
                print("Usuário não encontrado.")
                continue

            numero = int(input("Informe o número da conta: "))
            conta = next((c for c in usuario.contas if c.numero == numero), None)

            if conta:
                print(f"Saldo atual: R$ {conta.saldo:.2f}")
            else:
                print("Conta não encontrada.")

        elif opcao == "e":
            cpf = input("Informe o CPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)

            if not usuario:
                print("Usuário não encontrado.")
                continue

            numero = int(input("Informe o número da conta: "))
            conta = next((c for c in usuario.contas if c.numero == numero), None)

            if conta:
                exibir_extrato(conta)
            else:
                print("Conta não encontrada.")

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, usuarios, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "q":
            print("Saindo do sistema...")
            break

        else:
            print("Operação inválida, por favor selecione novamente a opção desejada.")

if __name__ == "__main__":
    main()
