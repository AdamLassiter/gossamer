#! /usr/bin/env python3

from __future__ import annotations
from collections import namedtuple
from functools import partial
import hashlib
import json
from time import time
from typing import List, Set
from urllib.parse import urlparse
from uuid import uuid4

from flask import Flask, jsonify, request
import requests


Block = namedtuple('Block', ['message', 'index', 'timestamp', 'transactions', 'proof', 'previous_hash'])
Block.__new__.__defaults__ = (None,) * len(Block._fields)
Transaction = namedtuple('Transaction', ['sender', 'recipient', 'amount'])


class Blockchain:

    def __init__(self):
        self.current_transactions: List[Transaction] = []
        self.chain: List[Block] = []
        self.nodes: Set[str] = set()
        # Create the genesis block
        self.new_block(100, '1')


    def register_node(self, address: str) -> None:
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self, chain: List[Block]) -> bool:
        for last_block, block in zip(chain[:-1], chain[1:]):
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block.previous_hash != self.hash(last_block):
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block.proof, block.proof, last_block.previous_hash):
                return False
        return True


    def resolve_conflicts(self) -> bool:
        neighbours = self.nodes
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False


    def new_block(self, proof: int, previous_hash: str) -> Block:
        block = Block(**{
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        })
        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block


    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        self.current_transactions.append(Transaction(**{
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        }))
        return self.last_block.index + 1


    @property
    def last_block(self):
        return self.chain[-1]


    @staticmethod
    def hash(block: Block) -> str:
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    def proof_of_work(self, last_block: Block) -> int:
        last_proof = last_block.proof
        last_hash = self.hash(last_block)
        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        return proof


    @staticmethod
    def valid_proof(last_proof: int, proof: int, last_hash: str,
                    difficulty: int = 4) -> bool:
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == "0" * difficulty



class BlockchainNode(Flask):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.node_id = str(uuid4()).replace('-', '')
        self.blockchain = Blockchain()
        for rule, func, methods in self.routes:
            self.add_url_rule(rule, view_func=getattr(self, func), methods=methods)


    def mine(self):
        last_block = self.blockchain.last_block
        proof = self.blockchain.proof_of_work(last_block)
        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        self.blockchain.new_transaction('0', self.node_id, 1)
        # Forge the new Block by adding it to the chain
        previous_hash = self.blockchain.hash(last_block)
        block = self.blockchain.new_block(proof, previous_hash)
        response = Block(**{
            'message': "New Block Forged",
            'index': block.index,
            'transactions': block.transactions,
            'proof': block.proof,
            'previous_hash': block.previous_hash,
        })
        return jsonify(response), 200


    def new_transaction(self):
        values = request.get_json()
        # Check that the required fields are in the POST'ed data
        required = ['sender', 'recipient', 'amount']
        if not all(k in values for k in required):
            return 'Missing values', 400
        # Create a new Transaction
        index = self.blockchain.new_transaction(
            values['sender'],
            values['recipient'],
            values['amount'],
        )
        response = {'message': f'Transaction will be added to Block {index}'}
        return jsonify(response), 201


    def full_chain(self):
        response = {
            'chain': self.blockchain.chain,
            'length': len(self.blockchain.chain),
        }
        return jsonify(response), 200


    def register_nodes(self):
        values = request.get_json()
        nodes = values.get('nodes')
        if nodes is None:
            return "Error: Please supply a valid list of nodes", 400
        for node in nodes:
            self.blockchain.register_node(node)
        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(self.blockchain.nodes),
        }
        return jsonify(response), 201


    def consensus(self):
        replaced = self.blockchain.resolve_conflicts()
        if replaced:
            response = {
                'message': 'Our chain was replaced',
                'new_chain': self.blockchain.chain
            }
        else:
            response = {
                'message': 'Our chain is authoritative',
                'chain': self.blockchain.chain
            }
        return jsonify(response), 200


    routes = [('/mine', 'mine', ['GET']),
              ('/transactions/new', 'new_transaction', ['POST']),
              ('/chain', 'full_chain', ['GET']),
              ('/nodes/register', 'register_nodes', ['POST']),
              ('/nodes/resolve', 'consensus', ['GET'])]



if __name__ == '__main__':
    from argparse import ArgumentParser

    app = BlockchainNode(__name__)
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
