# import da gary
import datetime
import hashlib
import json
from flask import Flask, jsonify

# 1 - building the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(nonce = 1, previous_hash = '0')

    def create_block(self, nonce, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'nonce': nonce,
            'previous_hash': previous_hash
                 }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def nonce_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
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
            hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            index += 1
        return True



# 2 - mining our blockchain
# create web app
app = Flask(__name__)

# create a blockchain
blockchain = Blockchain()

# mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()

    previous_nonce = previous_block['nonce']
    previous_hash = blockchain.hash(previous_block)

    nonce = blockchain.nonce_of_work(previous_nonce)
    block = blockchain.create_block(nonce, previous_hash)

    response = {'message':'Congratulations, you just mined a block!', **block}
    return jsonify(response), 200

# get the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
        }
    return jsonify(response), 200

# run the app
app.run(host = '0.0.0.0', port = 5000)