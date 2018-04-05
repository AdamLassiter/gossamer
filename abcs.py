from abc import ABC, abstractmethod


class Cipher(ABC):
    
    @abstractmethod
    def encrypt(self, text: str) -> str:
        pass

    @abstractmethod
    def decrypt(self, text: str) -> str:
        pass


class SymmetricCipher(Cipher):

    @abstractmethod
    def key(self) -> str:
        pass


class AsymmetricCipher(Cipher):

    @abstractmethod
    def pubkey(self) -> str:
        pass

    @abstractmethod
    def privkey(self) -> str:
        pass


class Hash(ABC):

    @abstractmethod
    def update(self, text: str) -> None:
        pass

    @abstractmethod
    def digest(self) -> str:
        pass


class NetworkLayer(ABC):

    @abstractmethod
    def send(self, text: str) -> None:
        pass

    @abstractmethod
    def recv(self) -> str:
        pass
