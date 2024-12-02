from flask import Flask, request, jsonify
from blockchain import Blockchain, generate_public_key

PRIVATE_KEY = "f6c93994817fddff529c65f477b6631e8a5e64454e0eb903f4f5bb191e2c84f4"
PUBLIC_KEY = generate_public_key(PRIVATE_KEY)

blockchain = Blockchain(PRIVATE_KEY, PUBLIC_KEY)

app = Flask(__name__)

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    return jsonify(chain_data), 200

@app.route('/validate_chain', methods=['GET'])
def validate_chain():
    if blockchain.is_chain_valid():
        return jsonify({"message": "Blockchain é válida"}), 200
    else:
        return jsonify({"message": "Blockchain é inválida"}), 400

@app.route('/add', methods=['POST'])
def add_block():
    data = request.json
    blockchain.add_block(data)
    return jsonify({"message": "Block added!", "data": data}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
