# import da gary
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# 1 - building the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.transcations = []
        self.create_block(nonce=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, nonce, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'nonce': nonce,
            'previous_hash': previous_hash,
            'transcations': self.transcations
        }
        self.transcations = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def nonce_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(
                str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
        return new_nonce

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        index = 1
        while index < len(chain):
            block = chain[index]
            previous_block = chain[index - 1]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(
                str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            index += 1
        return True

    def add_transaction(self, sender, reciever, amount):
        self.transcations.append({
            'sender': sender,
            'reciever': reciever,
            'amount': amount
        })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        longest_chain = None
        this_chain_length = len(self.chain)

        for node in self.nodes:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                chain = response.json()['chain']
                length = response.json()['length']
                if length > this_chain_length:
                    this_chain_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# 2 - mining our blockchain
# create web app
app = Flask(__name__)

# creating an address for port 5000
node_address = str(uuid4()).replace('-', ' ')

# create the blockchain
blockchain = Blockchain()

# mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()

    previous_nonce = previous_block['nonce']
    previous_hash = blockchain.hash(previous_block)

    blockchain.add_transaction(sender = node_address, reciever = 'Rashid', amount=1)
    
    nonce = blockchain.nonce_of_work(previous_nonce)
    block = blockchain.create_block(nonce, previous_hash)

    response = {
        'message': 'Congratulations, you just mined a block!',
        **block
    }
    return jsonify(response), 200

# get the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

# check chain validity
@app.route('/is_valid', methods=['GET'])
def is_valid():
    validate = blockchain.is_chain_valid(blockchain.chain)
    if validate is True:
        return jsonify({'message': 'The chain is valid!'}), 200
    else:
        return jsonify({'message': 'ah shit. mfer been compromised'}), 200


# add a new transaction to the blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.get_json()
    transaction_keys = ['sender', 'reciever', 'amount']
    if not all(key in data for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(data['sender'], data['reciever'], data['amount']) # returns index of next block
    response = {'message': f'The transaction will be added to block {index}'}
    return jsonify(response), 201
    

# 3 - decentralizing the blockchain

# run the app
app.run(host='0.0.0.0', port=5000)
