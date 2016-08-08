# Gossamer

## Introduction
A distributed web-like network transfer system that aims to provide security through a range of encryption schemes and anonymity through a Tor-like network.

## Modules
### Gossamer
* Provides classes to create a webbed graph of clients grown from an initial 'seed' node
* Also provides a simple Tor-like networking system with onion messages sent along random paths

_The Gossamer network aims to provide anonymity by disclosing addresses only to chosen neighbour nodes_

### NTRUEncrypt
* Provides a pure-python implementation of the NTRUEncrypt algorithm
* Should eventually allow for homomorphic functions to be applied to the scheme

### SHA3-Keccak
* Should eventually provide a pure-python Keccak implementation

### AES
* Should eventually provide a pure-python AES implementation

## Specifics
Each client connects to a number of other clients

Send encr(addr, encr(addr, encr(... , msg)))

Seed stores public key and username, client stores private key
Seed verifies on client joining

Clients store only nicknames and direction

Network-wide encryption layer using server's key
Each node has individual encryption key
Vote new users in using secret-sharing
