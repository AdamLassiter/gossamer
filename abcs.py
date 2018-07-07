#! /usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')
S = TypeVar('S')


class Cipher(ABC, Generic[T, S]):
    
    @abstractmethod
    def encrypt(self, text: T) -> S:
        pass

    @abstractmethod
    def decrypt(self, text: S) -> T:
        pass


class SymmetricCipher(Cipher, Generic[T]):

    @abstractmethod
    def key(self) -> T:
        pass


class AsymmetricCipher(Cipher, Generic[T, S]):

    @abstractmethod
    def pubkey(self) -> T:
        pass

    @abstractmethod
    def privkey(self) -> S:
        pass


class Hash(ABC, Generic[T, S]):

    @abstractmethod
    def update(self, text: T) -> None:
        pass

    @abstractmethod
    def digest(self) -> S:
        pass


class NetworkLayer(ABC, Generic[T]):

    @abstractmethod
    def send(self, text: T) -> None:
        pass

    @abstractmethod
    def recv(self) -> T:
        pass


class Blockchain(ABC, Generic[T, S]):

    @abstractmethod
    def new_block(self, proof: T, previous_hash: S):
        pass
