from abc import ABC, abstractmethod
from datetime import datetime


# ----------------------- TRANSACAO -----------------------

class Transacao(ABC):

    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


# ----------------------- DEPOSITO -----------------------

class Deposito(Transacao):

    def _init_(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)
        return sucesso


# ----------------------- SAQUE -----------------------

class Saque(Transacao):

    def _init_(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)
        return sucesso


# ----------------------- HISTORICO -----------------------

class Historico:

    def _init_(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append(
            {
                "tipo": transacao._class.name_,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
        )


# ----------------------- CONTA -----------------------

class Conta:

    def _init_(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("Valor inválido.")
            return False
        if valor > self._saldo:
            print("Saldo insuficiente.")
            return False

        self._saldo -= valor
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("Valor inválido.")
            return False

        self._saldo += valor
        return True


# ----------------------- CONTA CORRENTE -----------------------

class ContaCorrente(Conta):

    def _init_(self, numero, cliente, limite=500, limite_saques=3):
        super()._init_(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [t for t in self.historico.transacoes if t["tipo"] == "Saque"]
        )

        if numero_saques >= self.limite_saques:
            print("Limite de saques excedido.")
            return False

        if valor > self.limite:
            print("Valor do saque excede o limite.")
            return False

        return super().sacar(valor)


# ----------------------- CLIENTE -----------------------

class Cliente:

    def _init_(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


# ----------------------- PESSOA FÍSICA -----------------------

class PessoaFisica(Cliente):

    def _init_(self, nome, cpf, data_nascimento, endereco):
        super()._init_(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento


# ----------------------- PROGRAMA PRINCIPAL -----------------------

def menu():
    return input("""
    ================ MENU ================
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nc] Nova conta
    [lc] Listar contas
    [nu] Novo usuário
    [q] Sair
    => """)


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "nu":
            cpf = input("CPF: ")
            nome = input("Nome: ")
            data = input("Data de nascimento: ")
            end = input("Endereço: ")

            cliente = PessoaFisica(nome, cpf, data, end)
            clientes.append(cliente)

            print("Cliente criado!")

        elif opcao == "nc":
            cpf = input("Informe o CPF: ")
            cliente = next((c for c in clientes if c.cpf == cpf), None)

            if not cliente:
                print("Cliente não encontrado.")
                continue

            numero = len(contas) + 1
            conta = ContaCorrente(numero, cliente)
            cliente.adicionar_conta(conta)
            contas.append(conta)

            print("Conta criada!")

        elif opcao == "d":
            cpf = input("CPF: ")
            cliente = next((c for c in clientes if c.cpf == cpf), None)

            if not cliente:
                print("Cliente não encontrado.")
                continue

            conta = cliente.contas[0]
            valor = float(input("Valor do depósito: "))
            cliente.realizar_transacao(conta, Deposito(valor))

        elif opcao == "s":
            cpf = input("CPF: ")
            cliente = next((c for c in clientes if c.cpf == cpf), None)

            if not cliente:
                print("Cliente não encontrado.")
                continue

            conta = cliente.contas[0]
            valor = float(input("Valor do saque: "))
            cliente.realizar_transacao(conta, Saque(valor))

        elif opcao == "e":
            cpf = input("CPF: ")
            cliente = next((c for c in clientes if c.cpf == cpf), None)

            if not cliente:
                print("Cliente não encontrado.")
                continue

            conta = cliente.contas[0]
            print("\n===== EXTRATO =====")
            for t in conta.historico.transacoes:
                print(f"{t['tipo']} - R$ {t['valor']} - {t['data']}")
            print("Saldo:", conta.saldo)

        elif opcao == "lc":
            for conta in contas:
                print(f"\nAgência: {conta._agencia}")
                print(f"Conta: {conta._numero}")
                print(f"Titular: {conta.cliente.nome}")

        elif opcao == "q":
            print("Saindo...")
            break

        else:
            print("Opção inválida!")


main()