# Gossamer

## Introduction
A distributed web-like network transfer system that aims to provide security through a range of encryption schemes and anonymity through a Tor-like network.

## Modules
### Gossamer
* Provides classes to create a webbed graph of clients grown from an initial 'seed' node
* Also provides a simple Tor-like networking system with onion messages sent along random paths

_The Gossamer network aims to provide anonymity by disclosing addresses only to chosen neighbour nodes_

### LZW
* Provides a basic LZW compression scheme that may be used for longer messages

### NTRUEncrypt
* Provides a typed Haskell implementation of the NTRUEncrypt algorithm

### SHA3-Keccak
* Provides a typed Haskell implementation of the Keccak Hash algorithm

### AES
* Provides a typed Haskell implementation of the AES algorithm

### Feistel
* Provides a typed Haskell implementation of a Feistel cipher, which may be used with arbitrary hash functions

## Specifics
* Each client connects to a number of other clients
* Send encr(addr, encr(addr, encr(... , msg)))
* Seed stores public key and username, client stores private key
* Seed verifies on client joining
* Clients store only nicknames and direction
* Network-wide encryption layer using server's key
* Each node has individual encryption key
* Vote new users in using secret-sharing

## License
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.  
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.  
You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

[//]: # "Add sources, flavour"
