from abc import ABC, abstractmethod


class BankAccount(ABC):
    def __init__(self, owner, initial_balance):
        self.owner = owner
        self.__balance = initial_balance  # Encapsulación

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount

    def _get_balance(self):
        return self.__balance

    def _set_balance(self, new_balance):
        self.__balance = new_balance

    @abstractmethod
    def withdraw(self, amount):
        pass  # Polimorfismo

    def check_balance(self):
        return f'Saldo actual: ${self.__balance}'


account = BankAccount('Ricardo', 1000)  # Abstracción

account.deposit(500)
# account.withdraw(700)

print(account.check_balance())
